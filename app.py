import streamlit as st
import pandas as pd
import sqlite3

# إعداد الصفحة
st.set_page_config(page_title="نظام عدادات المياه - لوحة التحكم", layout="wide")

# الاتصال بقاعدة البيانات
def get_data():
    conn = sqlite3.connect('village_water.db')
    df = pd.read_sql_query("SELECT * FROM subscribers", conn)
    conn.close()
    return df

# استدعاء البيانات
df = get_data()
if not df.empty:
    df['consumption'] = df['current_reading'] - df['last_reading']

st.title("💧 نظام إدارة عدادات المياه - لوحة التحكم")

# --- 1. لوحة الإحصائيات (KPIs) ---
if not df.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المشتركين", len(df))
    col2.metric("إجمالي الاستهلاك", f"{df['consumption'].sum():.2f} م³")
    col3.metric("متوسط الاستهلاك", f"{df['consumption'].mean():.2f} م³")

st.markdown("---")

# --- 2. البحث والتصفح ---
st.subheader("قائمة المشتركين")
search = st.text_input("🔍 ابحث عن مشترك بالاسم...")

if not df.empty:
    # فلترة البحث
    if search:
        filtered_df = df[df['name'].str.contains(search, case=False, na=False)]
    else:
        filtered_df = df

    # نظام التصفح (Pagination)
    page_size = 6
    total_pages = (len(filtered_df) - 1) // page_size + 1
    page = st.number_input("رقم الصفحة", min_value=1, max_value=total_pages, value=1)
    
    start_idx = (page - 1) * page_size
    subset = filtered_df.iloc[start_idx : start_idx + page_size]

    # عرض البطاقات
    cols = st.columns(3)
    for i, (_, row) in enumerate(subset.iterrows()):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background-color: #fff; padding: 15px; border-radius: 10px; 
                        border-top: 5px solid #2196F3; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 15px;">
                <h4 style="margin-top:0;">👤 {row['name']}</h4>
                <p>الاستهلاك: <b>{row['consumption']:.2f} م³</b></p>
                <small>القراءة الحالية: {row['current_reading']}</small>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("لا توجد بيانات لعرضها.")

# --- 3. القائمة الجانبية (الإضافة) ---
with st.sidebar.form("add_form", clear_on_submit=True):
    st.header("إضافة مشترك")
    name = st.text_input("اسم المشترك")
    last = st.number_input("القراءة السابقة", format="%.4f")
    curr = st.number_input("القراءة الحالية", format="%.4f")
    submit = st.form_submit_button("إضافة")

if submit and name:
    conn = sqlite3.connect('village_water.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO subscribers (name, last_reading, current_reading) VALUES (?, ?, ?)', (name, last, curr))
    conn.commit()
    conn.close()
    st.success("تمت الإضافة!")
    st.rerun()
