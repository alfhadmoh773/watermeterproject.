import streamlit as st
import pandas as pd
import sqlite3

# 1. تهيئة قاعدة البيانات (نظام نظيف)
def init_db():
    conn = sqlite3.connect('water_v2.db') # استخدمنا اسماً جديداً لضمان النظافة
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS subscribers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS readings (id INTEGER PRIMARY KEY AUTOINCREMENT, sub_id INTEGER, last REAL, curr REAL)''')
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
        if st.text_input("كلمة المرور:", type="password") == "12345":
            if st.button("دخول"): st.session_state.admin = True; st.rerun()
    else:
        st.success("مرحباً بك يا مدير")
        with st.form("admin_form", clear_on_submit=True):
            st.subheader("إضافة بيانات")
            name = st.text_input("اسم المشترك:")
            last = st.number_input("القراءة السابقة:")
            curr = st.number_input("القراءة الحالية:")
            if st.form_submit_button("حفظ"):
                conn = sqlite3.connect('water_v2.db')
                c = conn.cursor()
                c.execute("INSERT INTO subscribers (name) VALUES (?)", (name,))
                sub_id = c.lastrowid
                c.execute("INSERT INTO readings (sub_id, last, curr) VALUES (?,?,?)", (sub_id, last, curr))
                conn.commit(); conn.close(); st.rerun()
        
        del_id = st.number_input("ID للحذف:", step=1)
        if st.button("🗑 حذف نهائي"):
            conn = sqlite3.connect('water_v2.db')
            conn.execute("DELETE FROM subscribers WHERE id=?", (del_id,))
            conn.execute("DELETE FROM readings WHERE sub_id=?", (del_id,))
            conn.commit(); conn.close(); st.rerun()
        if st.button("خروج"): st.session_state.admin = False; st.rerun()

# 3. العرض الرئيسي
conn = sqlite3.connect('water_v2.db')
subs = pd.read_sql_query("SELECT * FROM subscribers", conn)
readings = pd.read_sql_query("SELECT * FROM readings", conn)
conn.close()

if not subs.empty:
    cols = st.columns(4)
    for i, row in subs.iterrows():
        with cols[i % 4]:
            with st.container(border=True):
                st.write(f"🆔 **ID:** {row['id']} | 👤 **{row['name']}**")
                # البحث عن قراءة المشترك
                u_read = readings[readings['sub_id'] == row['id']]
                if not u_read.empty:
                    diff = u_read.iloc[-1]['curr'] - u_read.iloc[-1]['last']
                    st.write(f"📊 الاستهلاك: **{diff}**")
                    if diff > 50: st.error("⚠️ مرتفع")
                else:
                    st.warning("لا توجد قراءات")
else:
    st.info("لا يوجد مشتركين.")
