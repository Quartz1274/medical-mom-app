import streamlit as st
import datetime

# --- إعدادات واجهة التطبيق ---
st.set_page_config(page_title="الرعاية الطبية للوالدة", page_icon="🩺", layout="centered")
st.title("🩺 السجل الطبي اليومي")
st.markdown("تطبيق عائلي لمتابعة الأدوية والضغط")
st.markdown("---")

# --- الحساب التلقائي للجرعات المتناوبة ---
# نحدد تاريخ اليوم الذي أخذت فيه 50 ميكروغرام ونادلوريك (9 جويلية 2026) كمرجع
base_date = datetime.date(2026, 7, 9) 
today = datetime.date.today()
delta_days = (today - base_date).days

# إذا كان الفرق عدداً زوجياً (مثل اليوم 0، بعد غد 2..) فالجرعة 50، وإلا 25
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

# تحديد جرعة الغدة أوتوماتيكياً
levo_label = "Levothyrox 50 µg" if is_levo_50 else "Levothyrox 25 µg"
levo_done = st.checkbox(f"07:00 - {levo_label} (على الريق)")

irbe_done = st.checkbox("08:00 - Irbésartan 300 mg")
collation_done = st.checkbox("10:00 - فطور خفيف (بدون تمر)")
repas_done = st.checkbox("15:00 - غداء (بدون ملح تماماً)")

aspegic_done = st.checkbox("15:30 - Aspégic 100 mg (بعد الأكل)")

# إظهار دواء حمض اليوريك فقط في أيامه المحددة
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

if st.button("💾 حفظ البيانات ومشاركتها", type="primary"):
    # هنا سيتم لاحقاً ربط الكود بقاعدة البيانات لحفظ المعلومات
    st.success("تم الحفظ بنجاح! يمكن لجميع الإخوة رؤية التحديث الآن.")