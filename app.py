import streamlit as st
import pandas as pd
import sqlite3

# إعداد الصفحة لتكون بوضع العرض الواسع
st.set_page_config(page_title="نظام عدادات المياه", layout="wide")

st.title("💧 نظام إدارة عدادات المياه")

# الاتصال بقاعدة البيانات
def get_data():
    try:
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
        df = pd.read_sql_query("SELECT * FROM subscribers", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"خطأ في الاتصال: {e}")
        return pd.DataFrame()

# عرض البيانات بنظام البطاقات
df = get_data()
st.subheader("لوحة بيانات المشتركين")

if not df.empty:
    df['consumption'] = df['current_reading'] - df['last_reading']
    
    # تقسيم الشاشة لثلاثة أعمدة
    cols = st.columns(3)
    
    for i, row in df.iterrows():
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background-color: #f9f9f9; padding: 20px; border-radius: 15px; 
                        border-left: 5px solid #2196F3; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); 
                        margin-bottom: 20px;">
                <h4 style="margin: 0; color: #333;">👤 {row['name']}</h4>
                <hr>
                <p style="margin: 5px 0;">القراءة السابقة: <b>{row['last_reading']}</b></p>
                <p style="margin: 5px 0;">القراءة الحالية: <b>{row['current_reading']}</b></p>
                <div style="margin-top: 15px; padding: 10px; background: #e3f2fd; 
                            border-radius: 8px; text-align: center; font-weight: bold; color: #1565C0;">
                    الاستهلاك: {row['consumption']:.2f} م³
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("قاعدة البيانات فارغة، استخدم القائمة الجانبية لإضافة مشترك.")

# نموذج الإضافة
with st.sidebar.form("add_form", clear_on_submit=True):
    st.header("إضافة مشترك جديد")
    name = st.text_input("اسم المشترك")
    last = st.number_input("القراءة السابقة", format="%.4f")
    curr = st.number_input("القراءة الحالية", format="%.4f")
    submit = st.form_submit_button("حفظ البيانات")

if submit:
    if name:
        conn = sqlite3.connect('village_water.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO subscribers (name, last_reading, current_reading) VALUES (?, ?, ?)', (name, last, curr))
        conn.commit()
        conn.close()
        st.success("تمت الإضافة بنجاح!")
        st.rerun() # تحديث الصفحة فوراً لرؤية البطاقة الجديدة
    else:
        st.warning("يرجى إدخال اسم المشترك على الأقل.")
