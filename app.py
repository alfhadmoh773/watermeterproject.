import streamlit as st
import pandas as pd
import sqlite3

st.title("💧 نظام عدادات المياه")

# الاتصال بقاعدة البيانات
conn = sqlite3.connect('village_water.db')

# عرض البيانات
st.subheader("جدول بيانات المشتركين")
df = pd.read_sql_query("SELECT * FROM subscribers", conn)
st.table(df)

# إضافة مشترك جديد
st.sidebar.subheader("إضافة مشترك جديد")
with st.sidebar.form("add_form"):
    name = st.text_input("اسم المشترك")
    last = st.number_input("القراءة السابقة")
    curr = st.number_input("القراءة الحالية")
    submit = st.form_submit_button("إضافة")

if submit:
    cursor = conn.cursor()
    cursor.execute('INSERT INTO subscribers (name, last_reading, current_reading) VALUES (?, ?, ?)', (name, last, curr))
    conn.commit()
    st.success("تمت الإضافة بنجاح!")
    st.rerun()

conn.close()
