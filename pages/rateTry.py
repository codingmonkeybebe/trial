import streamlit as st

#import pandas as pd
#import datetime
#import calendar
import numpy_financial as npf
from datetime import date
#from pyxirr import xirr

dm=30.421#days in momth
ecoLife=25
mm=10**6
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
    pv=(st.session_state.capex+st.session_state.opexPV)*mm
    disRate=st.session_state.irr/100/12
    st.session_state.bbc=round(npf.pmt(disRate,st.session_state.n*12,-pv,st.session_state.rv*(10**6))/dm,1)
def findIRR():
    pv=(st.session_state.capex+st.session_state.opexPV)*mm
    st.session_state.irr= round(100*npf.rate(st.session_state.n*12, st.session_state.bbc*dm, -pv, st.session_state.rv*(10**6))*12,5)

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


        irr = st.slider('Target IRR %',
                            min_value=0.01, max_value=20.00,
                            value=8.0, step=0.1,format="%0.1f",key='irr',on_change = findBBC)

        st.session_state.opexPV = -npf.pv(irr/100/12,ecoLife*12,opex*dm,0)/mm
        
        bbc = st.slider('Daily Rate',
                            1000.0,200000.0,0.0,100.0,key='bbc',format="$%f /Day",
                        on_change = findIRR)





        capex=sbc+st.session_state.opexPV

    with col3:
        st.write(f"Total Cost: ${round(capex,1)}mn")
        st.write("BBC rate ",st.session_state.bbc," ", float("{:.1f}".format(st.session_state.irr)),"%")
        sbcR0=round(sbc,1)
        deltaCpx=2
        bbcR=round(bbc,-1)
        deltaBBC=1000

        st.write("Sensitivities Tables:")
        
        columnLimit=5
        cols=st.columns(columnLimit)
        with cols[0]:
            st.write("sbc\BBC")
            sbcR=sbcR0-deltaCpx
            for j in range(1,deltaCpx*2+2,1):
                st.write(sbcR)
                sbcR=sbcR+1

                
        irrR=0.078
        for i in range(1,columnLimit,1):
            with cols[i]:
                irrR=irrR+0.001
                opexPV = -npf.pv(irrR/100/12,ecoLife*12,opex*dm,0)/mm
                st.write(irrR)
                sbcR= sbcR0-deltaCpx
                for j in range(1,deltaCpx*2+2,1):
                    #irr=findIRR()
                    npvR=sbcR+opexPV
                    bbc = npf.pmt(irrR/12,n*12, -npvR*mm, rv*mm)/dm
                    st.write(float("{:.1f}".format(float(bbc))),"")
                    sbcR= sbcR+1
                 

with st.container():
    c3.write(f"Total capex: ${round(capex,1)}mn")
    c4.write(f"Total opexPV: ${round(st.session_state.opexPV,1)}mn")

