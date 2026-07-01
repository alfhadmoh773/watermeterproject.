import streamlit as st
import pandas as pd
import sqlite3

# 1. تهيئة قاعدة البيانات (تأكد من حذف الملف القديم قبل التشغيل)
def init_db():
    conn = sqlite3.connect('village_water.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS subscribers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS readings (id INTEGER PRIMARY KEY AUTOINCREMENT, sub_id INTEGER, last_reading REAL, current_reading REAL)''')
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="نظام المياه", layout="wide")
st.title("💧 نظام إدارة عدادات المياه")

# 2. القائمة الجانبية (الإدارة)
with st.sidebar:
    st.header("⚙️ لوحة الإدارة")
    if "admin" not in st.session_state: st.session_state.admin = False
    
    if not st.session_state.admin:
        pwd = st.text_input("كلمة المرور:", type="password")
        if st.button("دخول"):
            if pwd == "12345": st.session_state.admin = True; st.rerun()
    else:
        st.success("أنت المدير")
        # نموذج الإضافة
        with st.form("admin_form", clear_on_submit=True):
            st.subheader("إضافة بيانات")
            name = st.text_input("اسم المشترك:")
            last = st.number_input("القراءة السابقة:")
            curr = st.number_input("القراءة الحالية:")
            if st.form_submit_button("حفظ المشترك والقراءة"):
                conn = sqlite3.connect('village_water.db')
                c = conn.cursor()
                c.execute("INSERT INTO subscribers (name) VALUES (?)", (name,))
                sub_id = c.lastrowid
                c.execute("INSERT INTO readings (sub_id, last_reading, current_reading) VALUES (?,?,?)", (sub_id, last, curr))
                conn.commit(); conn.close(); st.rerun()
        if st.button("خروج"): st.session_state.admin = False; st.rerun()

# 3. العرض الرئيسي (البطاقات)
st.subheader("👥 قائمة المشتركين")
conn = sqlite3.connect('village_water.db')
subs = pd.read_sql_query("SELECT * FROM subscribers", conn)
readings = pd.read_sql_query("SELECT * FROM readings", conn)
conn.close()

if not subs.empty:
    cols = st.columns(4)
    for i, row in subs.iterrows():
        # ربط دقيق للقراءة بالمشترك
        user_read = readings[readings['sub_id'] == row['id']]
        with cols[i % 4]:
            with st.container(border=True):
                st.write(f"🆔 **ID:** {row['id']}")
                st.write(f"👤 **{row['name']}**")
                
                if not user_read.empty:
                    last_val = user_read.iloc[-1]['last_reading']
                    curr_val = user_read.iloc[-1]['current_reading']
                    diff = curr_val - last_val
                    st.write(f"📊 الاستهلاك: {diff} وحدة")
                    if diff > 50:
                        st.error("⚠️ استهلاك مرتفع!")
                else:
                    st.warning("لا توجد قراءات")
else:
    st.info("لم يتم إضافة مشتركين بعد.")
