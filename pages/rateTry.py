import streamlit as st
import math
#import pandas as pd
#import datetime
#import calendar
import numpy_financial as npf
from datetime import date
#from pyxirr import xirr

dm=30.421#days in momth
#ecoLife=25.0
mm=10**6

defaultIRR=8.0

inflation=2#2%

st.set_page_config(
    
    page_title="Vessel Upgrade and Required Premium",
    page_icon="Seaspan",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)


st.write("Vessels Investment Returns and Daily Chartering Rate")
col1,col12,col2= st.columns([5,1,20])
col3,col4 = st.columns([20,1])
#col1, col2= st.columns([5,5])
c3, c4 = st.columns([5,5])

def roundup(x):
    return int(math.ceil(x / 100)) * 100#to the nearest 10th

def findFV(int):         
    #find the End of economic life value of re-lease, opex, rv
    i=int/100/12 #interest rate in decimal and monthly basis
    RREndOfFirmFV=-npf.pv(i,(ecoLife-n)*12,releaseRate*dm,0)/mm #the fv of release rate at end of firm period
    RVEndOfFirmFV=-npf.pv(i,(ecoLife-n)*12,0,rv)/mm #the fv of residual value at end of firm period


    i=(int-inflation)/100/12 #interest rate in decimal and monthly basis 
    escale=(1+inflation/100)**(n)

    opexEndOfFirmFV=-npf.pv(i,(ecoLife-n)*12,opex*escale*dm,0)/mm #the fv of release rate at end of firm period
    
    return (RREndOfFirmFV + RVEndOfFirmFV + opexEndOfFirmFV)

    i=(st.session_state.irr-inflation)/100/12 #interest rate in decimal and monthly basis 
    st.session_state.opexPV = -npf.pv(i,n*12,opex*dm,0)/mm  #PV of opex during the firm period
    st.session_state.pv=(st.session_state.sbc+st.session_state.opexPV+st.session_state.otherCapex)


def findBBC():
    fv=findFV(st.session_state.irr)
    
    i=st.session_state.irr/100/12 #interest rate in decimal and monthly basis
    term=st.session_state.n*12 #number of months
    npv=st.session_state.pv*mm #present value
    fv=fv*mm #future value

    st.write(st.session_state.sbc)
    st.write(st.session_state.opexPV)
    st.write(st.session_state.otherCapex)

    
    adj=(dm*utiizationFirm)
    st.session_state.bbc=roundup(npf.pmt(i,term,-npv,fv)/adj)

    return roundup(npf.pmt(i,term,-npv,fv)/adj)
def findIRR():
    fv=findFV(st.session_state.irr)
    pmt=st.session_state.bbc*dm #monthly payment
    term=st.session_state.n*12 #number of months
    npv=st.session_state.pv*mm #present value
    fv=fv*mm #future value
    adj=12*100#from monthly to annual rate and in whole number
    st.session_state.irr= round(npf.rate(term, pmt, -npv, fv)*adj,1)


with st.container():

    with col1:     
        sbc = st.slider('SBC $/vsl',
                            min_value=10.0, max_value=215.0,
                            value=100.0, step=0.5,format="$%fm",key='sbc',on_change = findBBC)
        otherCapex = st.slider('Other Capex: PD+Yard Ext+Legal $/vsl',
                            min_value=0.0, max_value=15.0,
                            value=7.5, step=0.5,format="$%fm",key='otherCapex',on_change = findBBC)
        opex = st.slider('Operating Cost + DD with 2% inflation',
                            min_value=0, max_value=20000,
                            value=5000, step=1,format="$%d pd",key='opex',on_change = findBBC)
        
        if opex>0:
            utiizationFirm=0.997
        else:
            utiizationFirm=1#0.997

        
        releaseRate = st.slider('Release Rate $ pd',
                            min_value=5000, max_value=80000,
                            value=35000, step=100,format="$%d pd",key='releaseRate',on_change = findBBC)
        
        rv = st.slider('End of Life Residual Value $mn',
                            min_value=0.0, max_value=40.0,
                            value=10.0, step=0.5,format="$%fm",key='rv',on_change = findBBC)
        
        ecoLife = st.slider('Economic Life 18/25/30 yrs',
                            min_value=18, max_value=30,
                            value=25, step=1,format="%d yr",key='ecoLife',on_change = findBBC)
        
        n = st.slider('Firm Period',
                            min_value=1, max_value=ecoLife,
                            value=10, step=1,format="%d yr",key='n',on_change = findBBC)
        irr = st.slider('Target IRR %',
                            min_value=4.0, max_value=15.0,
                            value=defaultIRR, step=0.1,format="%0.1f",key='irr',on_change = findBBC)

        defaultBBC=findBBC()
        
        bbc = st.slider('Daily Rate',
                            min_value=0, max_value=200000,
                            value=defaultBBC, step=100,format="$%d pd",key='bbc',on_change = findIRR)
        
    with col2:

        fsBBC= '{:,d}'.format(bbc)
        fsIRR = "{:.1f}".format(st.session_state.irr)
        fsN="{:d}".format(st.session_state.n)
        fsTOTALCAPEX="{:0.1f}".format(st.session_state.sbc+st.session_state.otherCapex)
        fsOPEX= "{:,}".format(opex)
        fsRELEASERATE= "{:,}".format(releaseRate)
        st.write("Recommendation: ",fsIRR,"%" " Daily Rate ",fsBBC,"pd,",
                " for firm period "+fsN+" yrs,",
                " with Capex ",fsTOTALCAPEX,"m,",
                " with Opex ",fsOPEX+"pd,",
                " with release rate ",fsRELEASERATE,"pd")
        
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
                st.write("$"+formatted_string+"m")
                sbcR=sbcR+1

                
        irrR=(round(st.session_state.irr-0.2,1))/100
        for i in range(1,columnLimit,1):
            with cols[i]:
                
                formatted_string = "{:.2f}".format(irrR*100)
                st.write(formatted_string+"%")
                
                opexPV = -npf.pv((irrR-inflation/100)/12,n*12,opex*dm,0)/mm
                sbcR= sbcR0-deltaCpx
                for j in range(1,deltaCpx*2+2,1):

                    pv=(sbcR+otherCapex+opexPV)*mm #sum all pv of capex and opex and dd and any other capex
                    fv=findFV(irrR*100)
                    bbc = roundup(npf.pmt(irrR/12,n*12, -pv, fv)/dm/utiizationFirm)
                    formatted_string = "${:.1f}".format(bbc/1000)
                    st.write(formatted_string,"k")
                    sbcR= sbcR+1
                    
                irrR=irrR+0.001

with st.container():
    #capex=sbc+st.session_state.opexPV
    c3.write("Total capex")
    #c4.write(f"Total opexPV: ${round(st.session_state.opexPV,1)}mn")

