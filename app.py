import streamlit as st
import pandas as pd
import sqlite3

# إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect('village_water.db')
    c = conn.cursor()
    # حذف الجدول القديم لضمان تحديثه بالأعمدة الجديدة (فقط إذا كنت لا تمانع فقدان البيانات الحالية)
    c.execute('DROP TABLE IF EXISTS subscribers') 
    c.execute('''CREATE TABLE IF NOT EXISTS subscribers 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, added_by TEXT)''')
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="نظام إدارة المياه", layout="wide")
st.title("💧 نظام إدارة عدادات المياه")

# القائمة الجانبية للمدير
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
        
        with st.form("add_sidebar", clear_on_submit=True):
            st.write("### ➕ إضافة مشترك")
            name = st.text_input("اسم المشترك")
            if st.form_submit_button("حفظ"):
                conn = sqlite3.connect('village_water.db')
                conn.execute("INSERT INTO subscribers (name, added_by) VALUES (?, ?)", (name, "المدير"))
                conn.commit()
                conn.close()
                st.rerun()
        
        sub_id = st.number_input("رقم (ID) للحذف:", min_value=1, step=1)
        if st.button("🗑 حذف المشترك"):
            conn = sqlite3.connect('village_water.db')
            conn.execute("DELETE FROM subscribers WHERE id=?", (sub_id,))
            conn.commit()
            conn.close()
            st.rerun()
            
        if st.button("خروج"): st.session_state.admin = False; st.rerun()

# العرض العام
st.subheader("👥 قائمة المشتركين")
conn = sqlite3.connect('village_water.db')
df = pd.read_sql_query("SELECT * FROM subscribers", conn)
conn.close()

if not df.empty:
    cols = st.columns(4)
    for index, row in df.iterrows():
        with cols[index % 4]:
            with st.container(border=True):
                st.write(f"👤 **{row['name']}**")
                # استخدام .get لتجنب الخطأ إذا كان العمود لا يزال غير موجود في بعض الحالات
                added_by = row.get('added_by', 'غير معروف')
                st.write(f"✍️ بواسطة: {added_by}")
else:
    st.info("لا يوجد مشتركين.")
