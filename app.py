import streamlit as st
import pandas as pd
import sqlite3

# إعداد الصفحة
st.set_page_config(page_title="نظام عدادات المياه", layout="wide")

# 1. الاتصال بقاعدة البيانات
def get_data():
    conn = sqlite3.connect('village_water.db')
    # التأكد من وجود الجدول
    conn.execute('''CREATE TABLE IF NOT EXISTS subscribers 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, last_reading REAL, current_reading REAL)''')
    df = pd.read_sql_query("SELECT * FROM subscribers", conn)
    conn.close()
    return df

# 2. جلب البيانات
df = get_data()

st.title("💧 نظام إدارة عدادات المياه")

# 3. عرض البيانات (باستخدام st.dataframe وهو الأكثر استقراراً)
if not df.empty:
    df['consumption'] = df['current_reading'] - df['last_reading']
    
    st.subheader("جدول بيانات المشتركين")
    st.dataframe(df, use_container_width=True) # عرض الجدول بشكل متناسق مع الشاشة
else:
    st.info("قاعدة البيانات فارغة.")

# 4. إضافة مشترك (بسيط ومباشر)
with st.sidebar:
    st.header("إضافة مشترك جديد")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("اسم المشترك")
        last = st.number_input("القراءة السابقة")
        curr = st.number_input("القراءة الحالية")
        if st.form_submit_button("إضافة"):
            conn = sqlite3.connect('village_water.db')
            conn.execute('INSERT INTO subscribers (name, last_reading, current_reading) VALUES (?, ?, ?)', (name, last, curr))
            conn.commit()
            conn.close()
            st.rerun()

# 5. حذف مشترك
st.subheader("حذف مشترك")
delete_id = st.number_input("أدخل رقم (ID) المشترك للحذف", min_value=1, step=1)
if st.button("حذف المشترك"):
    conn = sqlite3.connect('village_water.db')
    conn.execute('DELETE FROM subscribers WHERE id = ?', (delete_id,))
    conn.commit()
    conn.close()
    st.rerun()
