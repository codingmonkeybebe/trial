import streamlit as st
#import pandas as pd
import datetime
import calendar
import numpy_financial as npf
from datetime import date
from pyxirr import xirr


st.set_page_config(
    page_title="Vessel Upgrade and Required Premium",
    page_icon="Seaspan",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)


st.write("Vessel Upgrade and Required Premium")
col1, col2= st.columns(2)
with col1:     
    capex = st.slider('Upgrade CapEx Cost',
                        min_value=10.0, max_value=60.0,
                        value=20.0, step=0.5,format="$%fm")
    OtherCost = st.slider('Total Other Costs',
                        min_value=0.05, max_value=10.0,
                        value=0.05, step=0.05,format="$%fm")

    bbc = st.slider('BBC Rate / Day',
                        min_value=1000, max_value=50000,
                        value=5000, step=10,format="$%d /Day")

#     opex = st.slider('Operating Cost',
#                         min_value=100, max_value=2000,
#                         value=500, step=1,format="$%d/Day")
    rv = st.slider('Residual Value $mn',
                        min_value=0.0, max_value=40.0,
                        value=10.0, step=0.5,format="$%fm")

    n = st.slider('Repayment Years',
                        min_value=1, max_value=40,
                        value=10, step=1,format="%d yr")

    totalCost=capex+OtherCost

with col2:
    irr = npf.rate(n*12, bbc*30.5, -totalCost*(10**6), rv*(10**6))*12
    print(irr)
    st.write(f"Total Cost: ${totalCost}mn")
    st.write(float("{:.1f}".format(irr*100)),"%")
