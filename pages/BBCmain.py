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


    bbc = st.slider('BBC Rate / Day',
                        min_value=1000, max_value=50000,
                        value=5000, step=5,format="$%d /Day")


#     opex = st.slider('Operating Cost',
#                         min_value=100, max_value=2000,
#                         value=500, step=1,format="$%d/Day")
    rv = st.slider('Residual Value $mn',
                        min_value=0.0, max_value=40.0,
                        value=10.0, step=0.5,format="$%fm")

    n = st.slider('Repayment Years',
                        min_value=1, max_value=25,
                        value=10, step=1,format="%d yr")

#     bIRR = st.slider('BBC IRR',
#                         min_value=0.001, max_value=0.5,
#                         value=irr, step=0.001,format="%_%")

with col2:
    st.write(f"Total Cost: ${capex}mn")
    irr = npf.rate(n*12, bbc*30.5, -capex*(10**6), rv*(10**6))*12
    st.write("BBC rate ",bbc," ", float("{:.1f}".format(irr*100)),"%")
    capexR0=round(capex,-0)
    deltaCpx=5
    bbcR=round(bbc,-1)
    deltaBBC=1000

    st.write("Sensitivities Tables:")
    
    columnLimit=8
    cols=st.columns(columnLimit)
    with cols[1]:
        st.write("Capex\BBC")
        capexR=capexR0-deltaCpx
        for j in range(1,deltaCpx*2+2,1):
            st.write(capexR)
            print(capexR)
            capexR=capexR+1

            
    bbcR=bbcR-deltaBBC*3
    for i in range(2,columnLimit,1):
        with cols[i]:
            st.write(bbcR)
            capexR= capexR0-deltaCpx
            for j in range(1,deltaCpx*2+2,1):
                irr = npf.rate(n*12, bbcR*30.5, -capexR*(10**6), rv*(10**6))*12
                st.write(float("{:.1f}".format(irr*100)),"%")
                capexR= capexR+1
        bbcR=bbcR+deltaBBC

