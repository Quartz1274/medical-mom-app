import streamlit as st
import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- إعدادات واجهة التطبيق ---
st.set_page_config(page_title="الرعاية الطبية للوالدة", page_icon="🩺", layout="centered")
st.title("🩺 السجل الطبي اليومي")
st.markdown("تطبيق عائلي لمتابعة الأدوية والضغط")
st.markdown("---")

# --- الحساب التلقائي للجرعات المتناوبة ---
base_date = datetime.date(2026, 7, 9) 
today = datetime.date.today()
delta_days = (today - base_date).days

is_levo_50 = (delta_days % 2 == 0)
is_nadloric = (delta_days % 2 == 0)

st.subheader(f"📅 تاريخ اليوم : {today.strftime('%d/%m/%Y')}")

# --- القسم الأول: قياسات الضغط ---
st.write("### 🩸 قياسات الضغط والنبض")
col1, col2 = st.columns(2)
with col1:
    tension_matin = st.text_input("ضغط الصباح (مثال: 120/80)")
    tension_16h = st.text_input("ضغط 16:00 (وقت الذروة)")
with col2:
    tension_soir = st.text_input("ضغط المساء")
    pouls = st.number_input("النبض (bpm)", min_value=40, max_value=120, value=70)

st.markdown("---")

# --- القسم الثاني: الأدوية والروتين ---
st.write("### 💊 أدوية وروتين اليوم")

levo_label = "Levothyrox 50 µg" if is_levo_50 else "Levothyrox 25 µg"
levo_done = st.checkbox(f"07:00 - {levo_label} (على الريق)")

irbe_done = st.checkbox("08:00 - Irbésartan 300 mg")
collation_done = st.checkbox("10:00 - فطور خفيف (بدون تمر)")
repas_done = st.checkbox("15:00 - غداء (بدون ملح تماماً)")

aspegic_done = st.checkbox("15:30 - Aspégic 100 mg (بعد الأكل)")

if is_nadloric:
    nadloric_done = st.checkbox("15:30 - Nadloric 300 mg")
else:
    st.info("ℹ️ Nadloric 300 mg : راحة اليوم (غير مبرمج).")
    nadloric_done = False
    
amlor_done = st.checkbox("16:30 - Amlor 5 mg")
tisane_done = st.checkbox("18:15 - تيزانة نعناع")

# --- القسم الثالث: الملاحظات والحفظ ---
st.markdown("---")
notes = st.text_area("ملاحظات (أعراض، نوم، شكاوى...)")

# --- كود الحفظ الفعلي في جداول جوجل ---
if st.button("💾 حفظ البيانات ومشاركتها", type="primary"):
    try:
        # 1. إنشاء الاتصال مع جوجل شيتس
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # 2. قراءة البيانات السابقة من الجدول (مع ttl=0 لضمان جلب النسخة الأحدث)
        # تأكد أن اسم التبويب في جوجل شيتس هو "Sheet1" وإلا قم بتغييره هنا
        existing_data = conn.read(worksheet="Sheet1", ttl=0)
        
        # 3. تجميع بيانات اليوم في سطر جديد
        new_row = pd.DataFrame([{
            "التاريخ": today.strftime('%d/%m/%Y'),
            "ضغط الصباح": tension_matin,
            "ضغط 16:00": tension_16h,
            "ضغط المساء": tension_soir,
            "النبض": pouls,
            "Levothyrox": "تم" if levo_done else "لا",
            "Irbésartan": "تم" if irbe_done else "لا",
            "Aspégic": "تم" if aspegic_done else "لا",
            "Nadloric": "تم" if nadloric_done else "لا",
            "Amlor": "تم" if amlor_done else "لا",
            "ملاحظات": notes
        }])
        
        # 4. إضافة السطر الجديد إلى البيانات القديمة
        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
        
        # 5. إرسال البيانات المحدثة إلى جوجل شيتس
        conn.update(worksheet="Sheet1", data=updated_df)
        
        st.success("تم الحفظ بنجاح في جدول جوجل! يمكن لجميع الإخوة رؤية التحديث الآن.")
        st.balloons() # احتفال صغير بظهور البالونات عند الحفظ الحقيقي!
        
    except Exception as e:
        st.error("حدث خطأ أثناء الاتصال بالجدول. التفاصيل التقنية:")
        st.exception(e)
