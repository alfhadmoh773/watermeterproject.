import streamlit as st
import pandas as pd
import sqlite3

# إعداد الصفحة
st.set_page_config(page_title="نظام عدادات المياه", layout="wide")

# الاتصال بقاعدة البيانات وإنشاء الجدول إذا لم يكن موجوداً
def init_db():
    conn = sqlite3.connect('village_water.db')
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
    conn.close()

init_db()

# دوال العمليات
def get_data():
    conn = sqlite3.connect('village_water.db')
    df = pd.read_sql_query("SELECT * FROM subscribers", conn)
    conn.close()
    return df

def delete_subscriber(sub_id):
    conn = sqlite3.connect('village_water.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM subscribers WHERE id = ?', (sub_id,))
    conn.commit()
    conn.close()

# الواجهة
st.title("💧 نظام إدارة عدادات المياه - لوحة التحكم")

# إحصائيات سريعة
df = get_data()
if not df.empty:
    df['consumption'] = df['current_reading'] - df['last_reading']
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المشتركين", len(df))
    col2.metric("إجمالي الاستهلاك", f"{df['consumption'].sum():.2f} م³")
    col3.metric("متوسط الاستهلاك", f"{df['consumption'].mean():.2f} م³")

st.markdown("---")

# البحث والتصفح
search = st.text_input("🔍 ابحث عن مشترك...")
if not df.empty:
    if search:
        filtered_df = df[df['name'].str.contains(search, case=False, na=False)]
    else:
        filtered_df = df

    # عرض البطاقات مع زر حذف لكل بطاقة
    cols = st.columns(3)
    for i, (_, row) in enumerate(filtered_df.iterrows()):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background-color: #fff; padding: 15px; border-radius: 10px; 
                        border-top: 5px solid #E91E63; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 15px;">
                <h4 style="margin:0;">👤 {row['name']}</h4>
                <p>الاستهلاك: <b>{row['consumption']:.2f} م³</b></p>
            </div>
            """, unsafe_allow_html=True)
            
            # زر الحذف
            if st.button(f"حذف {row['name']}", key=f"del_{row['id']}"):
                delete_subscriber(row['id'])
                st.rerun()

# القائمة الجانبية للإضافة
with st.sidebar.form("add_form", clear_on_submit=True):
    st.header("إضافة مشترك جديد")
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
