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
    # جدول القراءات
    c.execute('''CREATE TABLE IF NOT EXISTS readings 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, sub_id INTEGER, last_reading REAL, current_reading REAL, date TEXT)''')
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="نظام إدارة المياه", layout="wide")
st.title("💧 نظام إدارة عدادات المياه الذكي")

# القائمة الجانبية (للمدير فقط)
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
            st.write("### ➕ إضافة مشترك")
            name = st.text_input("اسم المشترك")
            if st.form_submit_button("حفظ المشترك"):
                conn = sqlite3.connect('village_water.db')
                conn.execute("INSERT INTO subscribers (name) VALUES (?)", (name,))
                conn.commit(); conn.close(); st.rerun()
        
        # إضافة قراءة
        with st.form("add_read", clear_on_submit=True):
            st.write("### 📝 تسجيل قراءة")
            sub_id = st.number_input("ID المشترك", step=1)
            last = st.number_input("العداد السابق")
            curr = st.number_input("العداد الحالي")
            if st.form_submit_button("حفظ القراءة"):
                conn = sqlite3.connect('village_water.db')
                conn.execute("INSERT INTO readings (sub_id, last_reading, current_reading, date) VALUES (?,?,?,?)", 
                             (sub_id, last, curr, datetime.now().strftime("%Y-%m-%d")))
                conn.commit(); conn.close(); st.rerun()
                
        # حذف مشترك
        st.write("---")
        del_id = st.number_input("ID للحذف:", step=1)
        if st.button("🗑 حذف مشترك"):
            conn = sqlite3.connect('village_water.db')
            conn.execute("DELETE FROM subscribers WHERE id=?", (del_id,))
            conn.execute("DELETE FROM readings WHERE sub_id=?", (del_id,))
            conn.commit(); conn.close(); st.rerun()
            
        if st.button("خروج"): st.session_state.admin = False; st.rerun()

# العرض العام (بطاقات المشتركين)
st.subheader("👥 قائمة المشتركين")
conn = sqlite3.connect('village_water.db')
subs = pd.read_sql_query("SELECT * FROM subscribers", conn)
readings = pd.read_sql_query("SELECT * FROM readings", conn)
conn.close()

if not subs.empty:
    cols = st.columns(4)
    for index, row in subs.iterrows():
        user_read = readings[readings['sub_id'] == row['id']]
        with cols[index % 4]:
            with st.container(border=True):
                st.write(f"🆔 **ID:** {row['id']}")
                st.write(f"👤 **الاسم:** {row['name']}")
                
                if not user_read.empty:
                    last_r = user_read.iloc[-1]['last_reading']
                    curr_r = user_read.iloc[-1]['current_reading']
                    diff = curr_r - last_r
                    st.write(f"📊 الاستهلاك: **{diff} وحدة**")
                    if diff > 50:
                        st.error("⚠️ استهلاك مرتفع جداً!")
                else:
                    st.info("لا توجد قراءات")
else:
    st.info("لا يوجد مشتركين مسجلين.")
