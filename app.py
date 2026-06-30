import streamlit as st
import pandas as pd
import sqlite3
import os

# إعداد الصفحة
st.set_page_config(
    page_title="نظام إدارة المياه المطور", 
    page_icon="icon.png", 
    layout="wide"
)

# 1. إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect('village_water.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS subscribers 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, last_reading REAL, current_reading REAL)''')
    conn.commit()
    conn.close()

init_db()

# 2. نظام الحماية
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 3. واجهة التطبيق
st.title("💧 نظام إدارة عدادات المياه المطور")

# جلب البيانات
conn = sqlite3.connect('village_water.db')
df = pd.read_sql_query("SELECT * FROM subscribers", conn)
conn.close()

if not df.empty:
    df['consumption'] = df['current_reading'] - df['last_reading']
    
    # 4. لوحة الإحصائيات
    with st.expander("📊 تحليل الاستهلاك العام"):
        st.bar_chart(df[['name', 'consumption']].set_index('name'))

    # البحث والتصفح
    search = st.text_input("🔍 ابحث عن مشترك...")
    filtered_df = df[df['name'].str.contains(search, case=False, na=False)] if search else df
    
    page = st.number_input("رقم الصفحة", min_value=1, value=1)
    subset = filtered_df.iloc[(page-1)*6 : page*6]
    
    # 5. عرض البطاقات
    cols = st.columns(3)
    for i, (_, row) in enumerate(subset.iterrows()):
        with cols[i % 3]:
            with st.container(border=True):
                st.subheader(f"👤 {row['name']}")
                st.write(f"الاستهلاك: **{row['consumption']:.2f} م³**")
                
                # التنبيهات
                if row['consumption'] > 100: st.error("⚠️ استهلاك مرتفع جداً!")
                elif row['consumption'] > 50: st.warning("⚠️ استهلاك متوسط-مرتفع")
                else: st.success("✅ استهلاك طبيعي")
                
                if st.session_state.logged_in:
                    if st.button(f"حذف {row['name']}", key=f"del_{row['id']}"):
                        conn = sqlite3.connect('village_water.db')
                        conn.execute('DELETE FROM subscribers WHERE id = ?', (row['id'],))
                        conn.commit()
                        conn.close()
                        st.rerun()

# 6. القائمة الجانبية
with st.sidebar:
    st.header("⚙️ لوحة الإدارة")
    if not st.session_state.logged_in:
        pwd = st.text_input("كلمة مرور المدير:", type="password")
        if st.button("دخول"):
            if pwd == "12345":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("كلمة المرور خطأ")
    else:
        st.success("أنت الآن في وضع المدير")
        if st.button("تسجيل خروج"):
            st.session_state.logged_in = False
            st.rerun()
            
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 تحميل تقرير Excel", csv, "report.csv", "text/csv")
        
        st.divider()
        st.header("➕ إضافة مشترك")
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
