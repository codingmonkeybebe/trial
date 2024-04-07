import streamlit as st
#import pandas as pd
import datetime
import calendar
from datetime import date
#from pyxirr import xirr


st.set_page_config(
    page_title="Vessel Valuation Made Simple",
    page_icon="Seaspan",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)


st.write("Vessel Valuation Made Simple")
col1, col2,col3,col4= st.columns(4)
with col1:
    ecd1 = st.date_input('Economic Closing Date',datetime.date.today())
    res = calendar.monthrange(ecd1.year, ecd1.month)
    ecd = date(ecd1.year,ecd1.month,res[1])
    
    builtDate1 = st.date_input('Built Date',datetime.date.today())
    res = calendar.monthrange(builtDate1.year, builtDate1.month)
    builtDate = date(builtDate1.year,builtDate1.month,res[1])
    
    teu = st.slider('Vessel TEU Capacity',
                        min_value=1000, max_value=20000,
                        value=9000, step=1000)
    lwt=teu*0.3
    
    
    nbPrice = st.slider('Vessel Purchase Price',
                        min_value=10.0, max_value=200.0,
                        value=95.0, step=0.5,format="$%f.dmn")
    commission = st.slider('SBC Commission %',
                        min_value=0, max_value=3,
                        value=0, format="%d%%")
    yardExtra = st.slider('Yard Extra and Upgrade',
                        min_value=00.0, max_value=3.0,
                        value=2.5, step=0.5,format="$%fmn")
    pdCost = st.slider('Pre-Delivery Cost',
                        min_value=00.0, max_value=3.0,
                        value=1.75, step=0.05,format="$%fmn")
    OtherCost = st.slider('Legal and other Cost',
                        min_value=0.05, max_value=1.0,
                        value=0.05, step=0.05,format="$%fmn")

    opex = st.slider('Operating Cost',
                        min_value=4000, max_value=10000,
                        value=6000, step=50,format="$%g/Day")

    ddCost = st.slider('Dry Docking Cost',
                        min_value=1.0, max_value=6.0,
                        value=2.0, step=0.05,format="$%fmn")

    scrapPrice = st.slider('Scrap Price $/LWT',
                        min_value=300.0, max_value=600.0,
                        value=400.0, step=50.0,format="$%f")

    totalCost=nbPrice*(1+commission/100) \
               +yardExtra \
               +pdCost+OtherCost
    

with col2:
    dates = [ecd, builtDate, date(builtDate.year, 12, 1)]
    amounts = [-nbPrice, -100, teu*10]

    # feed tuples
    #p=xirr(zip(dates, amounts)) 

    st.write(f"Model starts: {ecd}")
    st.write(f"LWT is: {lwt}")
    st.write(builtDate)
    st.write(f"Total Cost: {totalCost}")
    st.write(dates)
    st.write(float("{:.1f}".format(p*100)),"%")
