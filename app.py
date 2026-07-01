import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# 1. إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect('village_water.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS readings 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, subscriber_name TEXT, last_reading REAL, current_reading REAL, date TEXT)''')
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="نظام إدارة المياه", layout="wide")
st.title("💧 نظام إدارة عدادات المياه")

# 2. لوحة تحكم المدير (محمية بكلمة مرور)
with st.sidebar:
    st.header("⚙️ لوحة الإدارة")
    if "admin_logged_in" not in st.session_state: st.session_state.admin_logged_in = False
    
    if not st.session_state.admin_logged_in:
        pwd = st.text_input("كلمة مرور المدير:", type="password")
        if st.button("دخول"):
            if pwd == "12345": # يمكنك تغيير كلمة المرور هنا
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("كلمة المرور غير صحيحة")
    else:
        st.success("تم الدخول بصلاحيات المدير")
        if st.button("تسجيل خروج"):
            st.session_state.admin_logged_in = False
            st.rerun()

# 3. وظائف الإدارة (تظهر فقط إذا كان المدير مسجلاً للدخول)
if st.session_state.admin_logged_in:
    with st.expander("🛠 أدوات المدير", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("➕ إضافة قراءة")
            with st.form("add_form", clear_on_submit=True):
                name = st.text_input("اسم المشترك")
                last = st.number_input("القراءة السابقة", min_value=0.0)
                curr = st.number_input("القراءة الحالية", min_value=0.0)
                if st.form_submit_button("حفظ"):
                    conn = sqlite3.connect('village_water.db')
                    conn.execute("INSERT INTO readings (subscriber_name, last_reading, current_reading, date) VALUES (?, ?, ?, ?)", 
                                 (name, last, curr, datetime.now().strftime("%Y-%m-%d")))
                    conn.commit()
                    conn.close()
                    st.rerun()
        
        with col2:
            st.subheader("🗑 حذف سجل")
            del_id = st.number_input("أدخل رقم السجل (ID) للحذف:", min_value=1, step=1)
            if st.button("حذف السجل"):
                conn = sqlite3.connect('village_water.db')
                conn.execute("DELETE FROM readings WHERE id=?", (del_id,))
                conn.commit()
                conn.close()
                st.rerun()

# 4. العرض العام (متاح للجميع)
st.subheader("📋 سجل القراءات العام")
conn = sqlite3.connect('village_water.db')
df = pd.read_sql_query("SELECT * FROM readings", conn)
conn.close()

if not df.empty:
    df['consumption'] = df['current_reading'] - df['last_reading']
    st.dataframe(df, use_container_width=True)
else:
    st.info("لا توجد قراءات مسجلة حالياً.")
