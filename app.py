import streamlit as st
import pandas as pd
import sqlite3

# إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect('village_water.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS subscribers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)''')
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="نظام إدارة المياه", layout="wide")
st.title("💧 نظام إدارة عدادات المياه")

# القائمة الجانبية (كل شيء يخص المدير هنا)
with st.sidebar:
    st.header("⚙️ لوحة الإدارة")
    if "admin" not in st.session_state: st.session_state.admin = False
    
    # حالة عدم الدخول
    if not st.session_state.admin:
        pwd = st.text_input("كلمة مرور المدير:", type="password")
        if st.button("دخول"):
            if pwd == "12345": st.session_state.admin = True; st.rerun()
            else: st.error("كلمة المرور خطأ")
            
    # حالة الدخول (هنا تظهر الإضافة والحذف تحت زر الخروج)
    else:
        st.success("أنت الآن بصلاحيات المدير")
        
        # نموذج الإضافة داخل القائمة الجانبية
        with st.form("add_sidebar", clear_on_submit=True):
            st.write("### ➕ إضافة مشترك")
            name = st.text_input("اسم المشترك")
            if st.form_submit_button("حفظ"):
                conn = sqlite3.connect('village_water.db')
                conn.execute("INSERT INTO subscribers (name) VALUES (?)", (name,))
                conn.commit()
                conn.close()
                st.rerun()
        
        # نموذج الحذف داخل القائمة الجانبية
        sub_id = st.number_input("رقم (ID) للحذف:", min_value=1, step=1)
        if st.button("🗑 حذف المشترك"):
            conn = sqlite3.connect('village_water.db')
            conn.execute("DELETE FROM subscribers WHERE id=?", (sub_id,))
            conn.commit()
            conn.close()
            st.rerun()
            
        if st.button("خروج"): st.session_state.admin = False; st.rerun()

# العرض العام (خارج القائمة الجانبية)
st.subheader("👥 قائمة المشتركين")
conn = sqlite3.connect('village_water.db')
df = pd.read_sql_query("SELECT * FROM subscribers", conn)
conn.close()

if not df.empty:
    cols = st.columns(4)
    for index, row in df.iterrows():
        with cols[index % 4]:
            st.container(border=True).write(f"🆔 {row['id']} \n\n 👤 {row['name']}")
else:
    st.info("لا يوجد مشتركين.")
