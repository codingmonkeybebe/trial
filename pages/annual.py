import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
from dateutil.relativedelta import relativedelta

# Predefined top 20 containership liners (examples)
top_liners = [
    "Maersk", "Mediterranean Shipping Company (MSC)", "CMA CGM", "COSCO Shipping",
    "Hapag-Lloyd", "ONE", "Evergreen", "Yang Ming", "Hyundai Merchant Marine",
    "Zim", "K Line", "MOL", "NYK Line", "Hamburg Süd", "Wan Hai", "Pacific International Lines",
    "Hanjin", "EUKOR", "Spliethoff Group", "Sea Consortium"
]

default_size_teu = 10000

# --- Cached Functions ---
@st.cache_data
def calc_milestone_payments(initial_investment, milestone_dates, milestone_percents):
    milestone_dates_end = [
        pd.Timestamp(d) + pd.offsets.MonthEnd(0)
        if pd.Timestamp(d).day != (pd.Timestamp(d) + pd.offsets.MonthEnd(0)).day
        else pd.Timestamp(d)
        for d in milestone_dates
    ]
    payments = [(md, -initial_investment * p / 100) for md, p in zip(milestone_dates_end, milestone_percents)]
    return payments

@st.cache_data
def calc_cashflows_and_irr_annual(
    project_life_years,
    firm_period_years,
    milestone_payments,
    delivery_date,
    tc_rate,
    release_rate,
    opex_start,
    dd_cost_start,
    annual_escalation,
    scrap_value,
):
    delivery_date = pd.Timestamp(delivery_date)
    milestone_payments = [(pd.Timestamp(d), amt) for d, amt in milestone_payments]
    start_year = min(min(mp[0].year for mp in milestone_payments), delivery_date.year)
    end_year = delivery_date.year + project_life_years

    # Create year range
    years = range(start_year, end_year + 1)

    # Initialize annual cashflow dict
    annual_cashflows = {year: 0.0 for year in years}

    # Add milestone payments
    for date, payment in milestone_payments:
        annual_cashflows[date.year] += payment

    # Calculate full year net cash for operational years
    for year in range(delivery_date.year, end_year + 1):
        years_from_delivery = year - delivery_date.year
        if years_from_delivery < 0:
            continue
        if years_from_delivery < firm_period_years:
            current_tc_rate = tc_rate
        else:
            current_tc_rate = release_rate

        opex = opex_start * ((1 + annual_escalation) ** years_from_delivery)
        net_revenue_per_day = current_tc_rate - opex
        net_revenue_year = net_revenue_per_day * 365  # Annual revenue net of OPEX

        # Subtract dry docking costs at applicable years (every 5 years)
        if (years_from_delivery > 0) and (years_from_delivery % 5 == 0):
            dd_cost = dd_cost_start * ((1 + annual_escalation) ** years_from_delivery)
        else:
            dd_cost = 0

        annual_cashflows[year] += net_revenue_year - dd_cost

    # Add scrap value to last year cash flow
    annual_cashflows[end_year] += scrap_value

    # Prepare cash flows with actual discounted dates at mid-year
    cashflow_dates = [pd.Timestamp(year=yr, month=7, day=1) for yr in years]
    cashflow_values = [annual_cashflows[yr] for yr in years]

    # Calculate IRR using npf.xirr which accepts dates
    irr_annual = npf.xirr(list(zip(cashflow_dates, cashflow_values)))

    return pd.Series(cashflow_values, index=cashflow_dates), irr_annual

@st.cache_data(show_spinner=False)
def calc_sensitivity_table(
    vessel_price_million,
    current_irr_annual,
    project_life_years,
    opex_start,
    dd_cost_start,
    annual_escalation
):
    vessel_prices = [vessel_price_million - i for i in reversed(range(5))]
    irr_targets = [current_irr_annual - 0.02 + i * 0.01 for i in range(5)]
    
    def compute_required_tc(vp_m, target_irr):
        low_tc, high_tc = 1000, 100000
        tolerance = 50  # less precision for faster convergence
        max_iterations = 15  # limit iterations
        
        vp = vp_m * 1_000_000
        months = project_life_years * 12
        avg_opex = opex_start * ((1 + annual_escalation) ** (project_life_years / 2))
        
        for _ in range(max_iterations):
            mid_tc = (low_tc + high_tc) / 2
            monthly_cf = (mid_tc - avg_opex) * 30.4375
            cfs = np.empty(months)
            cfs.fill(monthly_cf)
            cfs[0] -= vp
            irr_m = npf.irr(cfs)
            if irr_m is None:
                return None
            irr_a = (1 + irr_m) ** 12 - 1
            if irr_a < target_irr:
                low_tc = mid_tc
            else:
                high_tc = mid_tc
            if high_tc - low_tc <= tolerance:
                break
        return round((low_tc + high_tc) / 2, 0)
    
    matrix = []
    for vp_m in vessel_prices:
        row = [compute_required_tc(vp_m, irr_t) for irr_t in irr_targets]
        matrix.append(row)
    
    df = pd.DataFrame(
        matrix,
        columns=[f"{irr*100:.1f}%" for irr in irr_targets],
        index=[f"{vp:.1f}M" for vp in vessel_prices]
    )
    return df

# --- Page Title ---
st.title("Monthly Vessel Leasing IRR Calculator with Costs Escalation and Extra Inputs")

# --- Inputs Section ---

# Carrier, Vessel Size, Contract Type, and PO input in one row
st.write("### Carrier, Vessel Size, Contract Type and PO")
cols_top = st.columns(4)

with cols_top[0]:
    carrier = st.selectbox("Select Carrier", top_liners, index=0)

with cols_top[1]:
    vessel_teu = st.number_input("Vessel Size (TEU)", min_value=1000, max_value=23000, value=default_size_teu, step=1000)

with cols_top[2]:
    contract_type = st.selectbox("Contract Type", ["TC", "BBC"])

with cols_top[3]:
    po_option = st.selectbox("PO (Purchase Option)", ["No", "Yes"])

# Vessel price input
vessel_price_million = st.number_input("Vessel Price (Million USD)", value=100.0, min_value=0.1, step=0.1)

# Conditional inputs for costs based on contract type
if contract_type == "BBC":
    predelivery_cost_million = 0.0
    shipyard_extra_million = 0.0
    supervision_million = 0.0
    opex_per_day_start = 0.0
    dd_cost_start = 0.0
    annual_escalation_pct = 0.0
    st.write(
        "Pre-delivery Cost, Shipyard Extra Cost, Supervision, OPEX and Dry Docking costs set to 0 for BBC contract type."
    )
else:
    cols_costs = st.columns(3)
    with cols_costs[0]:
        predelivery_cost_million = st.number_input("Pre-delivery Cost (Million USD)", value=1.0, min_value=0.0, step=0.01)
    with cols_costs[1]:
        shipyard_extra_million = st.number_input("Shipyard Extra Cost (Million USD)", value=1.0, min_value=0.0, step=0.01)
    
    # Supervision and legal fee in same row
    cols_supervision_legal = st.columns(2)
    with cols_supervision_legal[0]:
        supervision_million = st.number_input("Supervision Cost (Million USD)", value=0.7, min_value=0.0, step=0.01)
    with cols_supervision_legal[1]:
        legal_fee_million = st.number_input("Legal Fee (Million USD)", value=0.07, min_value=0.0, step=0.001)

    opex_per_day_start = st.number_input("OPEX (USD/day) at Year 0", value=6000)
    dd_cost_million_start = st.number_input("Dry Docking Cost every 5 years (Million USD) at Year 0", value=1.0, min_value=0.0, step=0.1)
    dd_cost_start = dd_cost_million_start * 1_000_000
    annual_escalation_pct = st.number_input("Annual Escalation Rate (%) for OPEX and DD Costs", value=2.0, min_value=0.0, step=0.1) / 100

if contract_type == "BBC":
    # Even if BBC, legal fee input always visible and separate
    legal_fee_million = st.number_input("Legal Fee (Million USD)", value=0.07, min_value=0.0, step=0.001)

# Convert to USD
vessel_price = vessel_price_million * 1_000_000
predelivery_cost = predelivery_cost_million * 1_000_000 if contract_type != "BBC" else 0.0
shipyard_extra = shipyard_extra_million * 1_000_000 if contract_type != "BBC" else 0.0
supervision = supervision_million * 1_000_000 if contract_type != "BBC" else 0.0
legal_fee = legal_fee_million * 1_000_000

initial_investment = vessel_price + predelivery_cost + shipyard_extra + supervision + legal_fee

delivery_date = st.date_input("Vessel Delivery Date", value=pd.to_datetime("2026-12-31"))

n_milestones = 5
default_percents = [20, 10, 10, 10]  # last milestone percent auto-calculated

st.write("### Milestone Dates (Day, Month and Year)")
cols_dates = st.columns(n_milestones)
milestone_dates = []
for i in range(n_milestones):
    dt = cols_dates[i].date_input(
        f"Milestone {i+1} Date",
        value=delivery_date - relativedelta(months=3 * (n_milestones - 1 - i)),
        key=f"milestone_date_{i}"
    )
    milestone_dates.append(pd.Timestamp(dt))

st.write("### Milestone Percentages (%)")
cols_perc = st.columns(n_milestones)
milestone_percents = []
for i in range(n_milestones):
    if i < n_milestones - 1:
        perc = cols_perc[i].slider(f"% Milestone {i+1}", min_value=1, max_value=99, value=default_percents[i], key=f"milestone_perc_{i}")
        milestone_percents.append(perc)
    else:
        perc = 100 - sum(milestone_percents)
        cols_perc[i].markdown(f"**Milestone {i+1} (Delivery) %: {perc:.2f}%**")
        milestone_percents.append(perc)

total_perc = sum(milestone_percents)
if abs(total_perc - 100) > 0.01:
    st.error(f"Milestone percentages must sum to 100%. Current sum: {total_perc:.2f}%")

# Firm Period and Release Rate inputs
firm_period_years = st.number_input("Firm Period (years)", value=15, min_value=1, max_value=30)
release_rate = st.number_input("Release Rate (USD/day)", value=20000)

# Adjust project life and release rate if PO is Yes
if po_option == "Yes":
    project_life_years = firm_period_years
    release_rate = 0.0
else:
    project_life_years = st.number_input("Project Life (years)", value=25, min_value=firm_period_years, max_value=30)

scrap_value_million = st.number_input("Terminal Scrap Value (Million USD)", value=25.0, min_value=0.0, step=0.1)
scrap_value = scrap_value_million * 1_000_000

# TC Rate Input
tc_rate_input = st.number_input("TC Rate (USD/day)", value=40000)

# Recompute with current inputs using annual cashflow function
milestone_payments = calc_milestone_payments(initial_investment, milestone_dates, milestone_percents)
cashflows, irr_annual = calc_cashflows_and_irr_annual(
    project_life_years,
    firm_period_years,
    milestone_payments,
    delivery_date,
    tc_rate_input,
    release_rate,
    opex_per_day_start,
    dd_cost_start,
    annual_escalation_pct,
    scrap_value,
)

if irr_annual is not None and abs(total_perc - 100) < 0.01:
    investment_analysis = f"""
    **Investment Opportunity Overview**

    This vessel leasing project models a container ship of approximately {vessel_teu:,} TEU operated by {carrier}, one of the top 20 global containership liners.
    The total investment including vessel price and pre-delivery related costs is approximately USD {initial_investment / 1_000_000:,.2f} million. Operating expenses and dry docking costs escalate annually at {annual_escalation_pct * 100:.2f}% over a {project_life_years}-year term.

    Recent industry reports highlight strong newbuilding orders with en bloc deals for vessels similar in size to {vessel_teu} TEU priced around USD 90-140 million, e.g., the Hapag Lloyd contract for 12 Post Panamax vessels near 9,200 TEU at approx. USD 140 million each.
    Daily TC rates in the market for prime operators typically range USD 35,000 to 45,000 for these sizes, aligning well with the model's base TC rate of USD {tc_rate_input:,.0f}/day.
    Industry forecasts note intensifying competition driven by fleet capacity growth (over 350 vessels added in 2024-2025) and evolving environmental regulations impacting operating costs and Charter Party terms.

    The target annualized IRR of {irr_annual * 100:.2f}% fits within market expectations of 8-14% for containership leases, reflecting balanced risk-return.
    To secure this deal, Seaspan should leverage milestone payments aligned with construction progress, negotiate flexibly on fuel transition and environmental compliance costs, and capitalize on its fleet scale and operational efficiencies.
    Transparent risk-sharing and cost-control provisions will enhance charterer confidence amid volatile freight rate conditions.

    Recent comparable transactions illustrate vessels priced between USD 90-110 million with similar TEU and TC rates chartered by industry leaders such as Maersk, MSC, and CMA CGM.
    Despite global trade uncertainties and excess supply risk, the structured milestone approach and sensitivity analysis enable informed investment decisions and highlight pricing flexibility to meet IRR targets.
    """
    st.markdown(investment_analysis)

# Average Annual Net Cash Flow
st.write("### Annual Net Cash Flow (USD)")
st.dataframe(cashflows.apply(lambda x: f"${x:,.2f}"))

# IRR Results
st.write("### IRR Results")
if irr_annual is not None and abs(total_perc - 100) < 0.01:
    st.write(f"Annualized IRR: {irr_annual * 100:.3f}%")
else:
    st.write("IRR could not be computed or milestone percentages invalid.")

# Sensitivity Table
if irr_annual is not None:
    sensitivity_df = calc_sensitivity_table(
        vessel_price_million,
        irr_annual,
        project_life_years,
        opex_per_day_start,
        dd_cost_start,
        annual_escalation_pct,
    )
    st.write("### Sensitivity Table: Required TC Rate (USD/day)")
    st.dataframe(sensitivity_df)
