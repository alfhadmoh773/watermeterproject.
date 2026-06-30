import streamlit as st
import pandas as pd

st.title("Water Meter System")

data = {
    'User': ['Ahmed', 'Salem', 'Ali'],
    'Usage': [60, 250, 45],
    'Status': ['Normal', 'Leak Alert!', 'Normal']
}

df = pd.DataFrame(data)

st.table(df)

if st.button('Check Leaks'):
    st.error("Alert: Salem has high consumption!")
