import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# إعداد قاعدة البيانات (هيكلية نظيفة)
def init_db():
    conn = sqlite3.connect('village_water.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS subscribers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS readings (id INTEGER PRIMARY KEY AUTOINCREMENT, sub_id INTEGER, last_reading REAL, current_reading REAL)''')
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="نظام إدارة المياه", layout="wide")
st.title("💧 نظام إدارة عدادات المياه الذكي")

# 1. لوحة الإدارة (في القائمة الجانبية فقط)
with st.sidebar:
    st.header("⚙️ لوحة الإدارة")
    if "admin" not in st.session_state: st.session_state.admin = False
    
    if not st.session_state.admin:
        pwd = st.text_input("كلمة مرور المدير:", type="password")
        if st.button("دخول"):
            if pwd == "12345": st.session_state.admin = True; st.rerun()
            else: st.error("كلمة المرور خطأ")
    else:
        st.success("أنت الآن بصلاحيات المدير")
        # إضافة مشترك
        with st.form("add_sub", clear_on_submit=True):
            name = st.text_input("اسم المشترك:")
            if st.form_submit_button("إضافة مشترك"):
                conn = sqlite3.connect('village_water.db')
                conn.execute("INSERT INTO subscribers (name) VALUES (?)", (name,))
                conn.commit(); conn.close(); st.rerun()
        
        # إضافة قراءة
        with st.form("add_read", clear_on_submit=True):
            sid = st.number_input("ID المشترك:", min_value=1, step=1)
            last = st.number_input("القراءة السابقة:")
            curr = st.number_input("القراءة الحالية:")
            if st.form_submit_button("حفظ القراءة"):
                conn = sqlite3.connect('village_water.db')
                conn.execute("INSERT INTO readings (sub_id, last_reading, current_reading) VALUES (?,?,?)", (sid, last, curr))
                conn.commit(); conn.close(); st.rerun()
        
        if st.button("خروج"): st.session_state.admin = False; st.rerun()

# 2. العرض الرئيسي (بطاقات مرتبة)
st.subheader("👥 قائمة المشتركين")
conn = sqlite3.connect('village_water.db')
subs = pd.read_sql_query("SELECT * FROM subscribers", conn)
readings = pd.read_sql_query("SELECT * FROM readings", conn)
conn.close()

if not subs.empty:
    cols = st.columns(4)
    for i, row in subs.iterrows():
        # ربط القراءة بالمشترك
        user_read = readings[readings['sub_id'] == row['id']]
        with cols[i % 4]:
            with st.container(border=True):
                st.markdown(f"**🆔 ID:** {row['id']}")
                st.markdown(f"**👤 الاسم:** {row['name']}")
                
                if not user_read.empty:
                    last_r = user_read.iloc[-1]['last_reading']
                    curr_r = user_read.iloc[-1]['current_reading']
                    diff = curr_r - last_r
                    st.write(f"📊 الاستهلاك: **{diff} وحدة**")
                    if diff > 50:
                        st.error("⚠️ استهلاك مرتفع!")
                else:
                    st.warning("لا توجد قراءات")
else:
    st.info("لا يوجد مشتركين.")
