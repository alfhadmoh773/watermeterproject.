import sqlite3
import pandas as pd

# 1. إنشاء/الاتصال بقاعدة البيانات
conn = sqlite3.connect('village_water.db')
cursor = conn.cursor()

# 2. إنشاء جدول المشتركين والعدادات
cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscribers (
        id INTEGER PRIMARY KEY,
        name TEXT,
        last_reading REAL,
        current_reading REAL
    )
''')

# 3. دالة لإضافة مشترك جديد
def add_subscriber(name, last_reading, current_reading):
    cursor.execute('INSERT INTO subscribers (name, last_reading, current_reading) VALUES (?, ?, ?)', 
                   (name, last_reading, current_reading))
    conn.commit()
    print(f"تمت إضافة المشترك: {name}")

# 4. دالة لتحليل الاستهلاك وكشف التسريب (بذكاء بسيط)
def analyze_usage():
    df = pd.read_sql_query("SELECT * FROM subscribers", conn)
    df['consumption'] = df['current_reading'] - df['last_reading']
    
    # تحديد حد أقصى (مثلاً 100 متر مكعب) للاعتبار كـ "تسريب"
    leak_threshold = 100
    df['status'] = df['consumption'].apply(lambda x: 'خطر تسريب!' if x > leak_threshold else 'طبيعي')
    
    return df

# تجربة البرنامج
add_subscriber('أحمد', 50, 60)
add_subscriber('سالم', 100, 250) # هذا سيظهر كخطر تسريب

results = analyze_usage()
print("\nتقرير استهلاك المياه:")
print(results)

# إغلاق الاتصال
conn.close()
