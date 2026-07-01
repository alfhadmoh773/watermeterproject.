import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# إعداد الصفحة
st.set_page_config(page_title="نظام إدارة المياه المطور", layout="wide")

# 1. إدارة قاعدة البيانات (Database Utility)
def get_db_connection():
    conn = sqlite3.connect('village_water.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS subscribers 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, last_reading REAL, current_reading REAL)''')
        conn.commit()

init_db()

@st.cache_data(ttl=60)
def load_data():
    with get_db_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM subscribers", conn)
        if not df.empty:
            df['consumption'] = df['current_reading'] - df['last_reading']
        return df

# 2. الواجهة الرئيسية
st.title("💧 نظام إدارة عدادات المياه - إصدار المحترفين")

df = load_data()

if not df.empty:
    # 3. تحليل متقدم (استخدام Plotly للرسوم التفاعلية)
    with st.expander("📊 تحليل الاستهلاك التفاعلي"):
        fig = px.bar(df, x='name', y='consumption', color='consumption', 
                     color_continuous_scale='RdYlGn_r', title="توزيع الاستهلاك بين المشتركين")
        st.plotly_chart(fig, use_container_width=True)

    # 4. البحث والفلترة
    search = st.text_input("🔍 بحث باسم المشترك...")
    filtered_df = df[df['name'].str.contains(search, case=False, na=False)] if search else df
    
    # تقسيم الصفحات
    page = st.number_input("رقم الصفحة", min_value=1, value=1)
    subset = filtered_df.iloc[(page-1)*6 : page*6]
    
    # عرض البطاقات
    cols = st.columns(3)
    for i, row in enumerate(subset.iterrows()):
        _, r = row
        with cols[i % 3]:
            with st.container(border=True):
                st.subheader(f"👤 {r['name']}")
                st.write(f"الاستهلاك: **{r['consumption']:.2f} م³**")
                
                # منطق تنبيه ذكي (يعتمد على متوسط استهلاك المشتركين)
                avg = df['consumption'].mean()
                if r['consumption'] > (avg * 1.5):
                    st.error("⚠️ استهلاك مرتفع جداً!")
                elif r['consumption'] > avg:
                    st.warning("⚠️ استهلاك فوق المتوسط")
                else:
                    st.success("✅ استهلاك طبيعي")

# 5. القائمة الجانبية (لوحة الإدارة)
with st.sidebar:
    st.header("⚙️ لوحة الإدارة")
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        pwd = st.text_input("كلمة مرور المدير:", type="password")
        if st.button("دخول"):
            if pwd == "12345": st.session_state.logged_in = True; st.rerun()
    else:
        st.success("أنت الآن في وضع المدير")
        if st.button("تسجيل خروج"): st.session_state.logged_in = False; st.rerun()
        
        # إضافة مشترك
        with st.form("add_form"):
            name = st.text_input("اسم المشترك")
            last = st.number_input("القراءة السابقة")
            curr = st.number_input("القراءة الحالية")
            if st.form_submit_button("إضافة"):
                with get_db_connection() as conn:
                    conn.execute('INSERT INTO subscribers (name, last_reading, current_reading) VALUES (?, ?, ?)', (name, last, curr))
                    conn.commit()
                st.rerun()
