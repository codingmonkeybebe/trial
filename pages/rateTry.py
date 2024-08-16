import streamlit as st
import math
#import pandas as pd
#import datetime
#import calendar
import numpy_financial as npf
from datetime import date
#from pyxirr import xirr

dm=30.421#days in momth
ecoLife=25.0
mm=10**6

defaultIRR=8.0
utiizationFirm=0.997
inflation=2#2%
#st.session_state.irr=defaultIRR
#st.session_state.bbc=defaultBBC

#st.markdown('<span style="font-size: 24px;">Larger text</span>', unsafe_allow_html=True)
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

def roundup(x):
    return int(math.ceil(x / 100)) * 100#to the nearest 10th

def finxXX():

    #for i in range(1,10):
   st.session_state.irr=st.session_state.irr
   st.session_state.opexPV = -npf.pv((st.session_state.irr-inflation)/100/12,ecoLife*12,opex*dm,0)/mm
   findBBC()
        #findIRR() 
    #    
    #bbc=st.session_state.bbc

    

def findBBC():
    #st.session_state.irr=8
    #st.session_state.irr=findIRR()
    st.session_state.opexPV = -npf.pv((st.session_state.irr-inflation)/100/12,ecoLife*12,opex*dm,0)/mm
    st.session_state.pv=(st.session_state.sbc+st.session_state.opexPV+st.session_state.otherCapex)*mm
    st.session_state.bbc=roundup(npf.pmt(st.session_state.irr/100/12,st.session_state.n*12,-st.session_state.pv,st.session_state.rv*mm)/dm/utiizationFirm)
def findIRR():
    #bbc=st.session_state.bbc
    st.session_state.opexPV = -npf.pv((st.session_state.irr-inflation)/100/12,ecoLife*12,opex*dm,0)/mm
    st.session_state.pv=(st.session_state.sbc+st.session_state.opexPV+st.session_state.otherCapex)*mm
    st.session_state.irr= round(100*npf.rate(st.session_state.n*12, st.session_state.bbc*dm, -st.session_state.pv, st.session_state.rv*mm)*12,1)
with st.container():
    #finxXX()
    with col1:     
        sbc = st.slider('SBC $/vsl',
                            min_value=10.0, max_value=215.0,
                            value=100.0, step=0.5,format="$%fm",key='sbc',on_change = findBBC)
        otherCapex = st.slider('Other Capex: PD+Yard Ext+Legal $/vsl',
                            min_value=0.5, max_value=15.0,
                            value=7.5, step=0.5,format="$%fm",key='otherCapex',on_change = findBBC)
        opex = st.slider('Operating Cost + DD with 2% inflation',
                            min_value=0, max_value=20000,
                            value=5000, step=1,format="$%d/Day",key='opex',on_change = finxXX)

        releaseRate = st.slider('Release Rate $/Day',
                            min_value=5000, max_value=80000,
                            value=35000, step=100,format="$%d/Day",key='releaseRate',on_change = findBBC)
        
        rv = st.slider('Residual Value $mn',
                            min_value=0.0, max_value=40.0,
                            value=10.0, step=0.5,format="$%fm",key='rv',on_change = finxXX)
        
        n = st.slider('Firm Period',
                            min_value=1, max_value=25,
                            value=10, step=1,format="%d yr",key='n',on_change = findBBC)
        irr = st.slider('Target IRR %',
                            min_value=5.0, max_value=15.0,
                            value=defaultIRR, step=0.1,format="%0.1f",key='irr',on_change = findBBC)
        defaultBBC=findBBC()
        bbc = st.slider('Daily Rate',
                            min_value=0, max_value=200000,
                            value=defaultBBC, step=100,format="$%d/Day",key='bbc',on_change = findIRR)
        
    with col3:
        #formatted_string = "{:,}".format(bbc)
        st.write("Total Cost: ")#+formatted_string+"mn")

        fsBBC= "{:,}".format(bbc)
        fsIRR = "{:.1f}".format(st.session_state.irr)
        fsN="{:d}".format(st.session_state.n)
        fsTOTALCAPEX="{:0.1f}".format(st.session_state.sbc+st.session_state.otherCapex)
        fsOPEX= "{:,}".format(opex)
        st.write("Recommendation: ",fsIRR,"%" " Daily Rate ",fsBBC,
                " for firm period ",fsN," yrs",
                " with $",fsTOTALCAPEX,"m",
                " with Opex",fsOPEX,"pd",
                " with release rate","pd")
        
        
        sbcR0=round(sbc,1)
        deltaCpx=2
        bbcR=round(bbc,-1)
        columnLimit=6
        
        st.write("Sensitivities Tables:")

        cols=st.columns(columnLimit)
        with cols[0]:
            st.write("sbc\BBC")
            sbcR=sbcR0-deltaCpx
            for j in range(1,deltaCpx*2+2,1):
                formatted_string = "{:.1f}".format(sbcR)
                st.write("$"+formatted_string+"mn")
                sbcR=sbcR+1

                
        irrR=(round(st.session_state.irr-0.2,1))/100
        for i in range(1,columnLimit,1):
            with cols[i]:
                
                formatted_string = "{:.2f}".format(irrR*100)
                st.write(formatted_string+"%")
                
                opexPV = -npf.pv((irrR-inflation/100)/12,ecoLife*12,opex*dm,0)/mm
                sbcR= sbcR0-deltaCpx
                for j in range(1,deltaCpx*2+2,1):
                    npvR=sbcR+otherCapex+opexPV#sum all pv of capex and opex and dd and any other capex
                    bbc = roundup(npf.pmt(irrR/12,n*12, -(npvR)*mm, rv*mm)/dm/utiizationFirm)
                    formatted_string = "{:,}".format(bbc)
                    st.write(formatted_string)
                    sbcR= sbcR+1
                    
                irrR=irrR+0.001

with st.container():
    #capex=sbc+st.session_state.opexPV
    c3.write("Total capex")
    #c4.write(f"Total opexPV: ${round(st.session_state.opexPV,1)}mn")

