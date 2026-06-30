import streamlit as st
import pandas as pd
import sqlite3
import os

# 1. إعداد الصفحة
st.set_page_config(page_title="نظام عدادات المياه", layout="wide")

# 2. إنشاء قاعدة البيانات إذا لم تكن موجودة
def init_db():
    conn = sqlite3.connect('village_water.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS subscribers 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, last_reading REAL, current_reading REAL)''')
    conn.commit()
    conn.close()

init_db()

# 3. دالة جلب البيانات (مُعدلة لتكون أكثر أماناً)
def get_data():
    conn = sqlite3.connect('village_water.db')
    try:
        df = pd.read_sql_query("SELECT * FROM subscribers", conn)
    except:
        df = pd.DataFrame(columns=['id', 'name', 'last_reading', 'current_reading'])
    conn.close()
    return df

# 4. تحميل البيانات (هنا نضمن أن df دائماً معرف)
df = get_data()

# 5. الواجهة
st.title("💧 نظام إدارة عدادات المياه")

if not df.empty:
    df['consumption'] = df['current_reading'] - df['last_reading']
    # هنا كود الإحصائيات والبطاقات الذي اتفقنا عليه...
    st.write("تم تحميل البيانات بنجاح.")
else:
    st.warning("قاعدة البيانات فارغة حالياً.")

# 6. الإضافة (هنا تضمن أنك لا تحذف df)
with st.sidebar.form("add_form", clear_on_submit=True):
    name = st.text_input("اسم المشترك")
    last = st.number_input("القراءة السابقة")
    curr = st.number_input("القراءة الحالية")
    if st.form_submit_button("إضافة"):
        if name:
            conn = sqlite3.connect('village_water.db')
            conn.execute('INSERT INTO subscribers (name, last_reading, current_reading) VALUES (?, ?, ?)', (name, last, curr))
            conn.commit()
            conn.close()
            st.rerun()
