import streamlit as st
import pandas as pd
import sqlite3

# إعداد الصفحة
st.set_page_config(page_title="نظام عدادات المياه", layout="wide")

# 1. الاتصال بقاعدة البيانات
def get_data():
    conn = sqlite3.connect('village_water.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS subscribers 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, last_reading REAL, current_reading REAL)''')
    df = pd.read_sql_query("SELECT * FROM subscribers", conn)
    conn.close()
    return df

df = get_data()

st.title("💧 نظام إدارة عدادات المياه")

# 2. عرض البيانات بنظام البطاقات (بدون CSS معقد يفسد الشكل)
if not df.empty:
    df['consumption'] = df['current_reading'] - df['last_reading']
    
    # تقسيم الأعمدة لعرض البطاقات
    cols = st.columns(3)
    
    for index, row in df.iterrows():
        # نستخدم الـ col المتغير لعرض البطاقات
        with cols[index % 3]:
            # استخدام st.container بحدود بسيطة وبدون أكواد HTML كثيرة
            with st.container(border=True):
                st.subheader(f"👤 {row['name']}")
                st.write(f"**الاستهلاك:** {row['consumption']:.2f} م³")
                st.caption(f"قراءة حالية: {row['current_reading']}")
                
                # زر الحذف
                if st.button(f"حذف {row['name']}", key=f"btn_{row['id']}"):
                    conn = sqlite3.connect('village_water.db')
                    conn.execute('DELETE FROM subscribers WHERE id = ?', (row['id'],))
                    conn.commit()
                    conn.close()
                    st.rerun()
else:
    st.info("قاعدة البيانات فارغة.")

# 3. القائمة الجانبية للإضافة
with st.sidebar:
    st.header("إضافة مشترك")
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
