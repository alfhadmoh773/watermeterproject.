import streamlit as st
import pandas as pd
import sqlite3

# إعداد الصفحة
st.set_page_config(page_title="نظام عدادات المياه", layout="wide")

# --- التصميم الخارجي (CSS) ---
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .card {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .card:hover { transform: translateY(-5px); border-color: #007BFF; }
    .metric-card { background: #fff; padding: 20px; border-radius: 15px; text-align: center; border: 1px solid #eee; }
    h1, h2, h3 { color: #2c3e50; }
</style>
""", unsafe_allow_html=True)

# --- دوال قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('village_water.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS subscribers 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, last_reading REAL, current_reading REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- واجهة التطبيق ---
st.title("💧 نظام إدارة عدادات المياه")

conn = sqlite3.connect('village_water.db')
df = pd.read_sql_query("SELECT * FROM subscribers", conn)
conn.close()

if not df.empty:
    df['consumption'] = df['current_reading'] - df['last_reading']
    
    # الإحصائيات في الأعلى
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='metric-card'><h3>{len(df)}</h3>مشترك</div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card'><h3>{df['consumption'].sum():.1f}</h3>إجمالي الاستهلاك</div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card'><h3>{df['consumption'].mean():.1f}</h3>متوسط الاستهلاك</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# البحث والتصفح
search = st.text_input("🔍 ابحث عن مشترك...")
filtered_df = df[df['name'].str.contains(search, case=False, na=False)] if search else df

page_size = 6
total_pages = (len(filtered_df) - 1) // page_size + 1
page = st.slider("اختر الصفحة", 1, max(1, total_pages), 1)

# عرض البطاقات
subset = filtered_df.iloc[(page-1)*page_size : page*page_size]
cols = st.columns(3)
for i, (_, row) in enumerate(subset.iterrows()):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="card">
            <h4>👤 {row['name']}</h4>
            <p>الاستهلاك: <b>{row['consumption']:.2f} م³</b></p>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"حذف {row['name']}", key=f"del_{row['id']}"):
            conn = sqlite3.connect('village_water.db')
            conn.execute('DELETE FROM subscribers WHERE id = ?', (row['id'],))
            conn.commit()
            conn.close()
            st.rerun()

# الإضافة
with st.sidebar:
    st.header("➕ إضافة مشترك")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("اسم المشترك")
        last = st.number_input("القراءة السابقة", format="%.4f")
        curr = st.number_input("القراءة الحالية", format="%.4f")
        if st.form_submit_button("حفظ البيانات"):
            if name:
                conn = sqlite3.connect('village_water.db')
                conn.execute('INSERT INTO subscribers (name, last_reading, current_reading) VALUES (?, ?, ?)', (name, last, curr))
                conn.commit()
                conn.close()
                st.rerun()
