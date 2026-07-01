import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# 1. إعداد قاعدة البيانات (هيكلة احترافية)
def init_db():
    conn = sqlite3.connect('village_water.db')
    c = conn.cursor()
    # جدول المستخدمين
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, name TEXT, is_admin BOOLEAN)''')
    # جدول القراءات (يربط كل قراءة بمستخدم معين)
    c.execute('''CREATE TABLE IF NOT EXISTS readings 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, last_reading REAL, current_reading REAL, date TEXT)''')
    # إضافة مدير افتراضي
    c.execute("INSERT OR IGNORE INTO users VALUES ('admin', '12345', 'المدير العام', 1)")
    conn.commit()
    conn.close()

init_db()

# 2. إدارة الجلسة
if 'user' not in st.session_state: st.session_state.user = None
if 'is_admin' not in st.session_state: st.session_state.is_admin = False

st.set_page_config(page_title="نظام إدارة المياه المحترف", layout="wide")

# 3. واجهة تسجيل الدخول
if not st.session_state.user:
    st.title("🔐 تسجيل الدخول إلى نظام المياه")
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        conn = sqlite3.connect('village_water.db')
        user_data = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p)).fetchone()
        if user_data:
            st.session_state.user = u
            st.session_state.is_admin = user_data[3] 
            st.rerun()
        else:
            st.error("اسم المستخدم أو كلمة المرور غير صحيحة")
        conn.close()
    st.stop()

# 4. الواجهة الرئيسية بعد الدخول
st.sidebar.write(f"👤 المستخدم: {st.session_state.user}")
if st.sidebar.button("تسجيل خروج"):
    st.session_state.user = None
    st.rerun()

if st.session_state.is_admin:
    st.title("⚙️ لوحة تحكم المدير")
    st.write("مرحباً بك في لوحة الإدارة.")
    # هنا يمكنك لاحقاً إضافة أدوات إدارة المستخدمين
else:
    st.title(f"💧 بيانات عداد المشترك: {st.session_state.user}")
    conn = sqlite3.connect('village_water.db')
    # جلب القراءات الخاصة بالمستخدم الحالي فقط
    df = pd.read_sql_query("SELECT * FROM readings WHERE username=?", conn, params=(st.session_state.user,))
    conn.close()
    
    if not df.empty:
        df['consumption'] = df['current_reading'] - df['last_reading']
        st.write(f"إجمالي استهلاكك الحالي: {df['consumption'].iloc[-1]} م³")
    else:
        st.info("لا توجد قراءات مسجلة باسمك بعد.")
