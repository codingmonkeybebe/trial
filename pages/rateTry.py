import streamlit as st
import math
import numpy_financial as npf
from datetime import date

#Global Variables
irrDefault=8.0
sbcDefault=100
otherCapexDefault=7.5
opexDefault=5000
ecoLifeDefault=25
firmPeriodDefault=12
inflation=2#2%
utiizationFirmDefault=0.997
utiizationRELEASE=0.96
dm=30.421#days in momth
mm=10**6


st.set_page_config(
    
    page_title="TC and IRR",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)


st.write("Vessels Investment Returns and Daily Chartering Rate")
col1,col12,col2= st.columns([20,1,20])
col3,col34,col4 = st.columns([20,1,20])
#col1, col2= st.columns([5,5])
c3, c4 = st.columns([5,5])

def roundup(x):
    return int(math.ceil(x / 100)) * 100#to the nearest 10th

def findFV(int):         
    #find the End of economic life value of re-lease, opex, rv
    i=int/100/12 #interest rate in decimal and monthly basis
    pmt=releaseRate*dm*utiizationRELEASE
    RREndOfFirmFV=-npf.pv(i,(ecoLife-n)*12,pmt,0)/mm #the fv of release rate at end of firm period
    RVEndOfFirmFV=-npf.pv(i,(ecoLife-n)*12,0,rv*mm)/mm #the fv of residual value at end of firm period

    i=(int-inflation)/100/12 #interest rate in decimal and monthly basis 
    escale=(1+inflation/100)**(n)
    OPEXEndOfFirmFV=-npf.pv(i,(ecoLife-n)*12,opex*escale*dm,0)/mm #the fv of release rate at end of firm period

    return (RREndOfFirmFV + RVEndOfFirmFV + OPEXEndOfFirmFV)

def findPV(int,sbcPV):
    i=(int-inflation)/100/12 #interest rate in decimal and monthly basis 
    pmt=opex*dm
    term=n*12
    fv=0
    opexPV = -npf.pv(i,term,pmt,fv)/mm  #PV of opex during the firm period

    return (sbcPV+opexPV+otherCapex)    
    
def findBBC(int):
    fv=findFV(int)*mm
    i=int/100/12 #interest rate in decimal and monthly basis
    term=n*12 #number of months
    npv=findPV(i*100*12,sbc)*mm #present value   
    adj=(dm*utiizationFirm)
    #st.session_state.bbc=roundup(npf.pmt(i,term,-npv,fv)/adj)
    return roundup(npf.pmt(i,term,-npv,fv)/adj)

def findSTATEbbc():
    i=st.session_state.irr
    fv=findFV(i)*mm
    term=n*12 #number of months
    npv=findPV(i,sbc)*mm #present value   
    adj=(dm*utiizationFirm)
    i=i/100/12 #interest rate in decimal and monthly basis
    st.session_state.bbc=roundup(npf.pmt(i,term,-npv,fv)/adj)
    return roundup(npf.pmt(i,term,-npv,fv)/adj)


def findIRR():
    fv=findFV(st.session_state.irr)
    pmt=st.session_state.bbc*dm #monthly payment
    term=n*12 #number of months
    npv=findPV(st.session_state.irr,sbc)*mm #present value  
    fv=fv*mm #future value
    adj=12*100#from monthly to annual rate and in whole number
    st.session_state.irr= round(npf.rate(term, pmt, -npv, fv)*adj,1)

with st.container():

    with col1:     
        sbc = st.slider('SBC $/vsl',
            min_value=10.0, max_value=215.0,
            value=100.0, step=0.5,format="$%fm",key='sbc',on_change = findSTATEbbc)
        otherCapex = st.slider('Other Capex: PD+Yard Ext+Legal $/vsl',
            min_value=0.0, max_value=15.0,
            value=otherCapexDefault, step=0.5,format="$%fm",key='otherCapex',on_change = findSTATEbbc)
        opex = st.slider('Operating Cost + DD with 2% inflation',
            min_value=0, max_value=20000,
            value=opexDefault, step=100,format="$%d pd",key='opex',on_change = findSTATEbbc)
        
        if opex>0:
            utiizationFirm=utiizationFirmDefault
        else:
            utiizationFirm=1#0.997

        
        releaseRate = st.slider('Release Rate $ pd',
            min_value=5000, max_value=80000,
            value=35000, step=100,format="$%d pd",key='releaseRate',on_change = findSTATEbbc)
        
        rv = st.slider('PO/RV $mn',
            min_value=0.0, max_value=100.0,
            value=25.0, step=1.0,format="$%fm",key='rv',on_change = findSTATEbbc)
        

        
    with col2:

        ecoLife = st.slider('Remaining Economic Life 18/25/30 yrs',
            min_value=5, max_value=30,
            value=ecoLifeDefault, step=1,format="%d yr",key='ecoLife',on_change = findSTATEbbc)
        
        n = st.slider('Firm Period',
            min_value=1, max_value=ecoLife,
            value=min(ecoLife,firmPeriodDefault), step=1,format="%d yr",key='n',on_change = findSTATEbbc)


        irr = st.slider('Target IRR %',
            min_value=4.0, max_value=15.0,
            value=irrDefault, step=0.1,format="%0.1f",key='irr',on_change = findSTATEbbc)
        
        defaultBBC=findSTATEbbc()
        bbc = st.slider('Daily Rate',
            min_value=0, max_value=200000,
            value=defaultBBC, step=100,format="$%d pd",key='bbc',on_change = findIRR)












        


with st.container():


    #with col3:

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

                
        irrR=round(st.session_state.irr-0.2,1)
        for i in range(1,columnLimit,1):
            with cols[i]:
                st.write("{:.1f}".format(irrR)+"%")
                i=(irrR-inflation)/100/12
                term=n*12
                pmt=opex*dm
                fv=0
                opexPV = -npf.pv(i,term,pmt,fv)/mm
                sbcR= sbcR0-deltaCpx
                for j in range(1,deltaCpx*2+2,1):

                    pv=findPV(irrR,sbcR)*mm #sum all pv of capex and opex and dd and any other capex
                    fv=findFV(irrR)*mm
                    i=irrR/100/12
                    term=n*12
                    bbc = roundup(npf.pmt(i,term, -pv, fv)/dm/utiizationFirm)
                    formatted_string = "${:.1f}".format(bbc/1000)
                    st.write(formatted_string,"k")
                    sbcR= sbcR+1
            irrR=irrR+0.1
