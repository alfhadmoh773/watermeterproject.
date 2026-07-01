import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# 1. إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect('village_water.db')
    c = conn.cursor()
    # جدول القراءات (يربط كل قراءة باسم المشترك)
    c.execute('''CREATE TABLE IF NOT EXISTS readings 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, last_reading REAL, current_reading REAL, date TEXT)''')
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="نظام إدارة المياه المحترف", layout="wide")

# 2. الواجهة الرئيسية (متاحة للجميع مباشرة)
st.title("💧 نظام إدارة عدادات المياه")

# نموذج إضافة القراءات
with st.expander("➕ إضافة قراءة جديدة للمشترك"):
    with st.form("add_reading_form"):
        user = st.text_input("اسم المشترك")
        last = st.number_input("القراءة السابقة", min_value=0.0)
        curr = st.number_input("القراءة الحالية", min_value=0.0)
        date = datetime.now().strftime("%Y-%m-%d")
        
        if st.form_submit_button("حفظ البيانات"):
            conn = sqlite3.connect('village_water.db')
            conn.execute("INSERT INTO readings (username, last_reading, current_reading, date) VALUES (?, ?, ?, ?)", 
                         (user, last, curr, date))
            conn.commit()
            conn.close()
            st.success("تم حفظ القراءة بنجاح!")

# 3. عرض البيانات
st.subheader("📋 سجل القراءات المسجلة")
conn = sqlite3.connect('village_water.db')
df = pd.read_sql_query("SELECT * FROM readings", conn)
conn.close()

if not df.empty:
    df['consumption'] = df['current_reading'] - df['last_reading']
    st.dataframe(df, use_container_width=True)
else:
    st.info("لا توجد قراءات مسجلة بعد.")
