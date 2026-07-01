import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# 1. إعداد قاعدة البيانات (هيكلية صلبة)
def init_db():
    conn = sqlite3.connect('village_water.db')
    c = conn.cursor()
    # جدول المشتركين
    c.execute('''CREATE TABLE IF NOT EXISTS subscribers 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)''')
    # جدول القراءات
    c.execute('''CREATE TABLE IF NOT EXISTS readings 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, sub_id INTEGER, 
                  last_reading REAL, current_reading REAL, date TEXT)''')
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="نظام إدارة المياه", layout="wide")
st.title("💧 نظام إدارة عدادات المياه الذكي")

# 2. لوحة الإدارة (Sidebar)
with st.sidebar:
    st.header("⚙️ لوحة التحكم")
    if "admin" not in st.session_state: st.session_state.admin = False
    
    if not st.session_state.admin:
        pwd = st.text_input("كلمة مرور المدير:", type="password")
        if st.button("دخول"):
            if pwd == "12345": st.session_state.admin = True; st.rerun()
            else: st.error("كلمة المرور خطأ")
    else:
        st.success("أنت الآن المدير")
        
        # إضافة مشترك جديد
        with st.form("add_sub", clear_on_submit=True):
            st.subheader("➕ إضافة مشترك جديد")
            sub_name = st.text_input("اسم المشترك")
            if st.form_submit_button("حفظ المشترك"):
                conn = sqlite3.connect('village_water.db')
                conn.execute("INSERT INTO subscribers (name) VALUES (?)", (sub_name,))
                conn.commit(); conn.close(); st.rerun()

        # إضافة قراءة لمشترك
        with st.form("add_read", clear_on_submit=True):
            st.subheader("📝 إضافة قراءة عداد")
            sid = st.number_input("ID المشترك", min_value=1, step=1)
            last = st.number_input("القراءة السابقة")
            curr = st.number_input("القراءة الحالية")
            if st.form_submit_button("حفظ القراءة"):
                conn = sqlite3.connect('village_water.db')
                conn.execute("INSERT INTO readings (sub_id, last_reading, current_reading, date) VALUES (?,?,?,?)", 
                             (sid, last, curr, datetime.now().strftime("%Y-%m-%d")))
                conn.commit(); conn.close(); st.rerun()

        if st.button("خروج"): st.session_state.admin = False; st.rerun()

# 3. العرض (الواجهة الرئيسية)
st.subheader("👥 قائمة المشتركين والاستهلاك")
conn = sqlite3.connect('village_water.db')
subs = pd.read_sql_query("SELECT * FROM subscribers", conn)
try:
    readings = pd.read_sql_query("SELECT * FROM readings", conn)
except:
    readings = pd.DataFrame()
conn.close()

if not subs.empty:
    cols = st.columns(4)
    for index, row in subs.iterrows():
        # فلترة قراءات المشترك الحالي
        user_read = readings[readings['sub_id'] == row['id']]
        
        with cols[index % 4]:
            with st.container(border=True):
                st.write(f"🆔 ID: {row['id']} | 👤 **{row['name']}**")
                
                if not user_read.empty:
                    last_r = user_read.iloc[-1]['last_reading']
                    curr_r = user_read.iloc[-1]['current_reading']
                    diff = curr_r - last_r
                    
                    st.write(f"الاستهلاك: **{diff} وحدة**")
                    if diff > 50: # حد التنبيه
                        st.error("⚠️ استهلاك مرتفع جداً!")
                else:
                    st.info("لم يتم تسجيل قراءات بعد")
else:
    st.info("لا يوجد مشتركين مسجلين.")
