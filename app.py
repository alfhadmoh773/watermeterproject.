import streamlit as st
import pandas as pd
import sqlite3

st.title("💧 نظام عدادات المياه")

# الاتصال بقاعدة البيانات
def get_data():
    try:
        conn = sqlite3.connect('village_water.db')
        # التأكد من وجود الجدول قبل القراءة
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                last_reading REAL,
                current_reading REAL
            )
        ''')
        conn.commit()
        
        df = pd.read_sql_query("SELECT * FROM subscribers", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"خطأ في الاتصال: {e}")
        return pd.DataFrame()

# عرض البيانات
df = get_data()
st.subheader("جدول بيانات المشتركين")
if not df.empty:
    st.table(df)
else:
    st.info("قاعدة البيانات فارغة، أضف مشتركاً جديداً.")

# نموذج الإضافة
with st.sidebar.form("add_form"):
    name = st.text_input("اسم المشترك")
    last = st.number_input("القراءة السابقة")
    curr = st.number_input("القراءة الحالية")
    submit = st.form_submit_button("إضافة")

if submit:
    conn = sqlite3.connect('village_water.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO subscribers (name, last_reading, current_reading) VALUES (?, ?, ?)', (name, last, curr))
    conn.commit()
    conn.close()
    st.success("تمت الإضافة!")
    st.rerun()
