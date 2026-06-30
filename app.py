import streamlit as st
import pandas as pd
import sqlite3

# إعداد الصفحة
st.set_page_config(page_title="نظام عدادات المياه الآمن", layout="wide")

# 1. نظام الحماية (البوابة)
def check_password():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        with st.sidebar:
            st.header("🔐 دخول الإدارة")
            password = st.text_input("أدخل كلمة المرور:", type="password")
            if st.button("دخول"):
                if password == "12345": # غيّر كلمة السر من هنا
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("كلمة المرور غير صحيحة")
        return False
    return True

# 2. إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect('village_water.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS subscribers 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, last_reading REAL, current_reading REAL)''')
    conn.commit()
    conn.close()

init_db()

# 3. عرض البيانات (متاح للجميع)
st.title("💧 نظام إدارة عدادات المياه")

conn = sqlite3.connect('village_water.db')
df = pd.read_sql_query("SELECT * FROM subscribers", conn)
conn.close()

if not df.empty:
    df['consumption'] = df['current_reading'] - df['last_reading']
    st.subheader("لوحة المشتركين")
    
    # البحث
    search = st.text_input("🔍 ابحث عن مشترك...")
    filtered_df = df[df['name'].str.contains(search, case=False, na=False)] if search else df
    
    # التصفح
    page_size = 6
    total_pages = (len(filtered_df) - 1) // page_size + 1
    page = st.number_input("الصفحة", min_value=1, max_value=total_pages, value=1)
    subset = filtered_df.iloc[(page-1)*page_size : page*page_size]
    
    cols = st.columns(3)
    for i, (_, row) in enumerate(subset.iterrows()):
        with cols[i % 3]:
            with st.container(border=True):
                st.subheader(f"👤 {row['name']}")
                st.write(f"الاستهلاك: **{row['consumption']:.2f} م³**")
                
                # إظهار زر الحذف فقط إذا كان المدير مسجلاً دخوله
                if st.session_state.get("logged_in", False):
                    if st.button(f"حذف {row['name']}", key=f"del_{row['id']}"):
                        conn = sqlite3.connect('village_water.db')
                        conn.execute('DELETE FROM subscribers WHERE id = ?', (row['id'],))
                        conn.commit()
                        conn.close()
                        st.rerun()

# 4. صلاحيات الإدارة (الإضافة)
if check_password():
    with st.sidebar:
        st.success("✅ أنت الآن في وضع الإدارة")
        if st.button("تسجيل خروج"):
            st.session_state.logged_in = False
            st.rerun()
            
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
