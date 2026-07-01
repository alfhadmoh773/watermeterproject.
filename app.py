import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect('village_water.db')
    c = conn.cursor()
    # جدول المشتركين
    c.execute('''CREATE TABLE IF NOT EXISTS subscribers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)''')
    # جدول القراءات (يربط كل قراءة بالمشترك)
    c.execute('''CREATE TABLE IF NOT EXISTS readings 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, sub_id INTEGER, last_reading REAL, current_reading REAL, date TEXT)''')
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="نظام إدارة المياه", layout="wide")
st.title("💧 نظام إدارة عدادات المياه الذكي")

# القائمة الجانبية (للمدير)
with st.sidebar:
    st.header("⚙️ لوحة الإدارة")
    if "admin" not in st.session_state: st.session_state.admin = False
    if not st.session_state.admin:
        pwd = st.text_input("كلمة المرور:", type="password")
        if st.button("دخول"):
            if pwd == "12345": st.session_state.admin = True; st.rerun()
    else:
        st.success("أنت المدير")
        # إضافة مشترك
        with st.form("add_sub", clear_on_submit=True):
            name = st.text_input("اسم مشترك جديد")
            if st.form_submit_button("إضافة"):
                conn = sqlite3.connect('village_water.db')
                conn.execute("INSERT INTO subscribers (name) VALUES (?)", (name,))
                conn.commit(); conn.close(); st.rerun()
        
        # إضافة قراءة
        st.write("---")
        with st.form("add_read", clear_on_submit=True):
            sub_id = st.number_input("ID المشترك", step=1)
            last = st.number_input("العداد السابق")
            curr = st.number_input("العداد الحالي")
            if st.form_submit_button("حفظ القراءة"):
                conn = sqlite3.connect('village_water.db')
                conn.execute("INSERT INTO readings (sub_id, last_reading, current_reading, date) VALUES (?,?,?,?)", 
                             (sub_id, last, curr, datetime.now().strftime("%Y-%m-%d")))
                conn.commit(); conn.close(); st.rerun()
        if st.button("خروج"): st.session_state.admin = False; st.rerun()

# العرض (بطاقات المشتركين مع الاستهلاك)
st.subheader("👥 قائمة المشتركين واستهلاكهم")
conn = sqlite3.connect('village_water.db')
subs = pd.read_sql_query("SELECT * FROM subscribers", conn)
readings = pd.read_sql_query("SELECT * FROM readings", conn)
conn.close()

if not subs.empty:
    cols = st.columns(4)
    for index, row in subs.iterrows():
        # جلب آخر قراءة لهذا المشترك
        user_read = readings[readings['sub_id'] == row['id']]
        
        with cols[index % 4]:
            with st.container(border=True):
                st.write(f"👤 **{row['name']}** (ID: {row['id']})")
                if not user_read.empty:
                    last_r = user_read.iloc[-1]['last_reading']
                    curr_r = user_read.iloc[-1]['current_reading']
                    diff = curr_r - last_r
                    
                    st.write(f"الاستهلاك: **{diff} وحدة**")
                    
                    # منطق التنبيه الأحمر
                    if diff > 50: # حد التنبيه (يمكنك تغييره)
                        st.error("⚠️ استهلاك مرتفع جداً!")
                else:
                    st.warning("لا توجد قراءات")
else:
    st.info("لا يوجد مشتركين.")
