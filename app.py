import streamlit as st
import pandas as pd
import sqlite3

# إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect('village_water.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS subscribers 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT)''')
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="نظام إدارة المياه", layout="wide")
st.title("💧 نظام إدارة عدادات المياه - عرض البطاقات")

# 1. لوحة تحكم المدير (محمية)
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
        if st.button("خروج"): st.session_state.admin = False; st.rerun()

# 2. أدوات الإضافة والحذف (تظهر للمدير فقط)
if st.session_state.admin:
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        with st.form("add_sub", clear_on_submit=True):
            name = st.text_input("اسم المشترك الجديد")
            if st.form_submit_button("إضافة مشترك"):
                conn = sqlite3.connect('village_water.db')
                conn.execute("INSERT INTO subscribers (name) VALUES (?)", (name,))
                conn.commit()
                conn.close()
                st.rerun()
    with col2:
        sub_id = st.number_input("رقم المشترك (ID) للحذف:", min_value=1, step=1)
        if st.button("حذف هذا المشترك"):
            conn = sqlite3.connect('village_water.db')
            conn.execute("DELETE FROM subscribers WHERE id=?", (sub_id,))
            conn.commit()
            conn.close()
            st.rerun()
    st.divider()

# 3. عرض المشتركين على شكل بطاقات (للجميع)
st.subheader("👥 قائمة المشتركين")
conn = sqlite3.connect('village_water.db')
df = pd.read_sql_query("SELECT * FROM subscribers", conn)
conn.close()

if not df.empty:
    cols = st.columns(4) # عرض 4 بطاقات في كل صف
    for index, row in df.iterrows():
        with cols[index % 4]:
            with st.container(border=True):
                st.subheader(f"👤 {row['name']}")
                st.write(f"رقم المشترك: {row['id']}")
else:
    st.info("لا يوجد مشتركين حالياً.")
