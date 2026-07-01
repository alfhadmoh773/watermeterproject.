import streamlit as st
import pandas as pd
import sqlite3

# إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect('village_water.db')
    c = conn.cursor()
    # جدول المشتركين
    c.execute('''CREATE TABLE IF NOT EXISTS subscribers 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT)''')
    # جدول القراءات
    c.execute('''CREATE TABLE IF NOT EXISTS readings 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, subscriber_id INTEGER, last_reading REAL, current_reading REAL)''')
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="نظام إدارة المياه", layout="wide")
st.title("💧 نظام إدارة المشتركين والعدادات")

# لوحة التحكم الجانبية (محمية)
with st.sidebar:
    st.header("⚙️ لوحة الإدارة")
    if "admin" not in st.session_state: st.session_state.admin = False
    
    if not st.session_state.admin:
        pwd = st.text_input("كلمة مرور المدير:", type="password")
        if st.button("دخول"):
            if pwd == "12345": st.session_state.admin = True; st.rerun()
            else: st.error("كلمة المرور خطأ")
    else:
        st.success("تم الدخول بصلاحيات المدير")
        if st.button("خروج"): st.session_state.admin = False; st.rerun()

# أدوات الإدارة
if st.session_state.admin:
    st.divider()
    tab1, tab2 = st.tabs(["👥 إدارة المشتركين", "📈 إدارة القراءات"])
    
    with tab1:
        st.subheader("إضافة أو حذف مشترك")
        col_a, col_b = st.columns(2)
        with col_a:
            with st.form("add_sub"):
                new_name = st.text_input("اسم المشترك الجديد")
                if st.form_submit_button("إضافة مشترك"):
                    conn = sqlite3.connect('village_water.db')
                    conn.execute("INSERT INTO subscribers (name) VALUES (?)", (new_name,))
                    conn.commit()
                    conn.close()
                    st.rerun()
        with col_b:
            sub_id = st.number_input("رقم المشترك (ID) للحذف:", min_value=1)
            if st.button("حذف المشترك نهائياً"):
                conn = sqlite3.connect('village_water.db')
                conn.execute("DELETE FROM subscribers WHERE id=?", (sub_id,))
                conn.commit()
                conn.close()
                st.rerun()

# عرض البيانات للجميع
st.subheader("📋 قائمة المشتركين المسجلين")
conn = sqlite3.connect('village_water.db')
df = pd.read_sql_query("SELECT * FROM subscribers", conn)
conn.close()
st.dataframe(df, use_container_width=True)
