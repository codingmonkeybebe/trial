import streamlit as st
#import pandas as pd
#import datetime
#import calendar
import numpy_financial as npf
from datetime import date
#from pyxirr import xirr


st.set_page_config(
    page_title="Vessel Upgrade and Required Premium",
    page_icon="Seaspan",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

#"st.session_state object:",st.session_state

st.write("Vessel Upgrade and Required Premium")
col1,col2= st.columns([20,1])
col3,col4 = st.columns([20,1])
#col1, col2= st.columns([5,5])
c3, c4 = st.columns([5,5])

def findBBC():
    st.session_state.bbc=round(npf.pmt(st.session_state.irr/100/12,st.session_state.n*12,-st.session_state.capex*(10**6),st.session_state.rv*(10**6))/30.5,1)
def findIRR():
    st.session_state.irr= round(100*npf.rate(st.session_state.n*12, st.session_state.bbc*30.5, -st.session_state.capex*(10**6), st.session_state.rv*(10**6))*12,5)

with st.container():

    with col1:     
        sbc = st.slider('SBC $/vsl',
                            min_value=10.0, max_value=215.0,
                            value=20.0, step=0.5,format="$%fm",key='capex',on_change = findBBC)
        
        opex = st.slider('Operating Cost',
                            min_value=0, max_value=20000,
                            value=500, step=1,format="$%d/Day",key='opex',on_change = findBBC)
        

        n = st.slider('Firm Period',
                            min_value=1, max_value=25,
                            value=10, step=1,format="%d yr",key='n',on_change = findBBC)


        
        rv = st.slider('Residual Value $mn',
                            min_value=0.0, max_value=40.0,
                            value=10.0, step=0.5,format="$%fm",key='rv',on_change = findBBC)


        bbc = st.slider('Daily Rate',
                            1000.0,100000.0,0.0,100.0,key='bbc',format="$%f /Day",
                        on_change = findIRR)


        irr = st.number_input('Target IRR %',
                            min_value=0.00, max_value=1000000.00,
                            value=8.0, step=0.1,key='irr',format="%0.1f",
                        on_change = findBBC)

        opexPV = -npf.pv(irr/100/12,n*12,opex*30.421,0)/10**6
        capex=sbc+opexPV

    with col3:
        st.write(f"Total Cost: ${capex}mn")
        st.write("BBC rate ",bbc," ", float("{:.1f}".format(st.session_state.irr)),"%")
        capexR0=round(capex,1)
        deltaCpx=2
        bbcR=round(bbc,-1)
        deltaBBC=1000

        st.write("Sensitivities Tables:")
        
        columnLimit=5
        cols=st.columns(columnLimit)
        with cols[0]:
            st.write("Capex\BBC")
            capexR=capexR0-deltaCpx
            for j in range(1,deltaCpx*2+2,1):
                st.write(capexR)
                capexR=capexR+1

                
        bbcR=bbcR-deltaBBC*2
        for i in range(1,columnLimit,1):
            with cols[i]:
                bbcR=bbcR+deltaBBC
                st.write(bbcR)
                capexR= capexR0-deltaCpx
                for j in range(1,deltaCpx*2+2,1):
                    #irr=findIRR()
                    irr = npf.rate(n*12, bbcR*30.5, -capexR*(10**6), rv*(10**6))*12
                    st.write(float("{:.1f}".format(float(irr)*100)),"%")
                    capexR= capexR+1
                 

with st.container():
    c3.write(f"Total capex: ${capex}mn")
    c4.write(f"Total opexPV: ${opexPV}mn")

