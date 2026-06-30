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

# 2. البحث (Search)
st.subheader("لوحة التحكم والبحث")
search = st.text_input("🔍 ابحث عن مشترك بالاسم...")

# فلترة البيانات
if search:
    filtered_df = df[df['name'].str.contains(search, case=False, na=False)]
else:
    filtered_df = df

# 3. نظام التصفح (Pagination)
if not filtered_df.empty:
    filtered_df['consumption'] = filtered_df['current_reading'] - filtered_df['last_reading']
    
    page_size = 6
    total_pages = (len(filtered_df) - 1) // page_size + 1
    
    # اختيار رقم الصفحة
    page = st.number_input("رقم الصفحة", min_value=1, max_value=total_pages, value=1)
    
    # تقسيم البيانات حسب الصفحة
    subset = filtered_df.iloc[(page-1)*page_size : page*page_size]
    
    # عرض البطاقات
    cols = st.columns(3)
    for index, (_, row) in enumerate(subset.iterrows()):
        with cols[index % 3]:
            with st.container(border=True):
                st.subheader(f"👤 {row['name']}")
                st.write(f"الاستهلاك: **{row['consumption']:.2f} م³**")
                st.caption(f"قراءة حالية: {row['current_reading']}")
                
                # زر الحذف
                if st.button(f"حذف {row['name']}", key=f"del_{row['id']}"):
                    conn = sqlite3.connect('village_water.db')
                    conn.execute('DELETE FROM subscribers WHERE id = ?', (row['id'],))
                    conn.commit()
                    conn.close()
                    st.rerun()
else:
    st.info("لا توجد بيانات تطابق بحثك.")

# 4. القائمة الجانبية للإضافة
with st.sidebar:
    st.header("➕ إضافة مشترك جديد")
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
