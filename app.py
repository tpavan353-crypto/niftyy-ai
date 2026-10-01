import streamlit as st
import pandas as pd
from nsepython import nse_optionchain_scrapper
import google.generativeai as genai
import time

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Missing API Key in Secrets")
    st.stop()

def get_data():
    try:
        payload = nse_optionchain_scrapper("NIFTY")
        price = payload['records']['underlyingValue']
        data = payload['filtered']['data']
        rows = [{"Strike": s['strikePrice'], "CE_OI": s['CE']['openInterest'], "CE_CHG": s['CE']['changeinOpenInterest'], "PE_OI": s['PE']['openInterest'], "PE_CHG": s['PE']['changeinOpenInterest']} for s in data]
        return pd.DataFrame(rows), price
    except: return None, None

st.title("📈 Nifty AI Analyst")
df, price = get_data()
if df is not None:
    pcr = df['PE_OI'].sum() / df['CE_OI'].sum()
    st.metric("Nifty Spot", price, delta=f"PCR: {round(pcr, 2)}")
    if st.button("AI Analysis"):
        atm = round(price / 50) * 50
        subset = df[(df['Strike'] >= atm - 150) & (df['Strike'] <= atm + 150)]
        response = model.generate_content(f"Nifty {price}, PCR {pcr:.2f}. Data: {subset.to_string()}. Short sentiment?")
        st.info(response.text)
    st.dataframe(df)
time.sleep(180)
st.rerun()
