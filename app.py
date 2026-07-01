import streamlit as st
import pandas as pd
import sqlite3

# إعداد قاعدة البيانات (هيكل موحد)
def init_db():
    conn = sqlite3.connect('village_water.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS subscribers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS readings (id INTEGER PRIMARY KEY AUTOINCREMENT, sub_id INTEGER, last REAL, curr REAL)''')
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="نظام المياه", layout="wide")
st.title("💧 نظام إدارة عدادات المياه")

# 1. القائمة الجانبية (للإدارة فقط)
with st.sidebar:
    st.header("⚙️ لوحة الإدارة")
    if "admin" not in st.session_state: st.session_state.admin = False
    
    if not st.session_state.admin:
        if st.text_input("كلمة المرور:", type="password") == "12345":
            if st.button("دخول"): st.session_state.admin = True; st.rerun()
    else:
        st.success("مرحباً بك يا مدير")
        # إضافة مشترك
        with st.form("add_sub"):
            name = st.text_input("اسم المشترك:")
            if st.form_submit_button("إضافة مشترك"):
                conn = sqlite3.connect('village_water.db')
                conn.execute("INSERT INTO subscribers (name) VALUES (?)", (name,))
                conn.commit(); conn.close(); st.rerun()
        # إضافة قراءة
        with st.form("add_read"):
            sid = st.number_input("ID المشترك:", step=1)
            last = st.number_input("القراءة السابقة:")
            curr = st.number_input("القراءة الحالية:")
            if st.form_submit_button("إضافة قراءة"):
                conn = sqlite3.connect('village_water.db')
                conn.execute("INSERT INTO readings (sub_id, last, curr) VALUES (?,?,?)", (sid, last, curr))
                conn.commit(); conn.close(); st.rerun()
        # حذف
        del_id = st.number_input("ID للحذف:", step=1)
        if st.button("🗑 حذف مشترك وبياناته"):
            conn = sqlite3.connect('village_water.db')
            conn.execute("DELETE FROM subscribers WHERE id=?", (del_id,))
            conn.execute("DELETE FROM readings WHERE sub_id=?", (del_id,))
            conn.commit(); conn.close(); st.rerun()
        if st.button("خروج"): st.session_state.admin = False; st.rerun()

# 2. العرض الرئيسي (بطاقات)
conn = sqlite3.connect('village_water.db')
subs = pd.read_sql_query("SELECT * FROM subscribers", conn)
readings = pd.read_sql_query("SELECT * FROM readings", conn)
conn.close()

if not subs.empty:
    cols = st.columns(4)
    for i, row in subs.iterrows():
        # جلب أخر قراءة
        u_read = readings[readings['sub_id'] == row['id']]
        with cols[i % 4]:
            with st.container(border=True):
                st.write(f"🆔 **ID:** {row['id']} | 👤 **{row['name']}**")
                if not u_read.empty:
                    diff = u_read.iloc[-1]['curr'] - u_read.iloc[-1]['last']
                    st.write(f"📊 الاستهلاك: **{diff}**")
                    if diff > 50: st.error("⚠️ استهلاك مرتفع")
                else:
                    st.warning("لا يوجد قراءات")
else:
    st.info("لا يوجد مشتركين.")
