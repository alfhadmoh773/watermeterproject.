import streamlit as st
import pandas as pd
import sqlite3

# إعداد الصفحة وتطبيق الألوان الفاتحة
st.set_page_config(page_title="نظام عدادات المياه", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
    .card {
        background-color: #FFFFFF;
        border: 1px solid #E9ECEF;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 15px;
        transition: 0.3s;
    }
    .card:hover { border-color: #007BFF; box-shadow: 0 4px 8px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #212529; }
</style>
""", unsafe_allow_html=True)

# دوال قاعدة البيانات
def init_db():
    conn = sqlite3.connect('village_water.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS subscribers 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, last_reading REAL, current_reading REAL)''')
    conn.commit()
    conn.close()

def get_data():
    conn = sqlite3.connect('village_water.db')
    df = pd.read_sql_query("SELECT * FROM subscribers", conn)
    conn.close()
    return df

init_db()

# الواجهة الرئيسية
st.title("💧 نظام إدارة عدادات المياه")

df = get_data()
if not df.empty:
    df['consumption'] = df['current_reading'] - df['last_reading']
    
    # الإحصائيات
    col1, col2, col3 = st.columns(3)
    col1.metric("المشتركين", len(df))
    col2.metric("إجمالي الاستهلاك", f"{df['consumption'].sum():.2f} م³")
    col3.metric("المتوسط", f"{df['consumption'].mean():.2f} م³")

st.markdown("---")

# البحث والتصفح
search = st.text_input("🔍 بحث عن مشترك...")
if not df.empty:
    filtered_df = df[df['name'].str.contains(search, case=False, na=False)] if search else df
    
    page_size = 6
    total_pages = (len(filtered_df) - 1) // page_size + 1
    page = st.number_input("الصفحة", min_value=1, max_value=total_pages, value=1)
    
    subset = filtered_df.iloc[(page-1)*page_size : page*page_size]
    
    cols = st.columns(3)
    for i, (_, row) in enumerate(subset.iterrows()):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card">
                <h4>👤 {row['name']}</h4>
                <p>الاستهلاك: <b>{row['consumption']:.2f} م³</b></p>
                <small>قراءة حالية: {row['current_reading']}</small>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"حذف {row['name']}", key=f"del_{row['id']}"):
                conn = sqlite3.connect('village_water.db')
                conn.execute('DELETE FROM subscribers WHERE id = ?', (row['id'],))
                conn.commit()
                conn.close()
                st.rerun()

# الإضافة
with st.sidebar.form("add_form", clear_on_submit=True):
    st.header("➕ إضافة مشترك")
    name = st.text_input("اسم المشترك")
    last = st.number_input("القراءة السابقة", format="%.4f")
    curr = st.number_input("القراءة الحالية", format="%.4f")
    if st.form_submit_button("حفظ"):
        if name:
            conn = sqlite3.connect('village_water.db')
            conn.execute('INSERT INTO subscribers (name, last_reading, current_reading) VALUES (?, ?, ?)', (name, last, curr))
            conn.commit()
            conn.close()
            st.rerun()
