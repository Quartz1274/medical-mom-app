import streamlit as st
import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ==========================================
# CONFIGURATION DE L'APPLICATION
# ==========================================
st.set_page_config(page_title="الرعاية الطبية للوالدة", page_icon="🩺", layout="centered")
st.title("🩺 السجل الطبي اليومي الموحد")
st.markdown("---")

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1wkLT95thxdlubjF1e6d7cVffMkX1M0LqFRCO22dzI5U"

tab_daily, tab_analysis = st.tabs(["📋 المتابعة اليومية", "📊 التحاليل الطبية"])

# ==========================================
# ONGLET 1 : SUIVI QUOTIDIEN SYNCHRONISÉ
# ==========================================
with tab_daily:
    today = datetime.date.today()
    today_str = today.strftime('%d/%m/%Y')
    
    # Calcul automatique des doses alternées
    base_date = datetime.date(2026, 7, 9) 
    delta_days = (today - base_date).days
    is_levo_50 = (delta_days % 2 == 0)
    is_nadloric = (delta_days % 2 == 0)
    
    st.subheader(f"📅 تاريخ اليوم : {today_str}")
    
    # Sélection de l'utilisateur
    utilisateur = st.selectbox("👤 من قام بالرعاية أو إدخال البيانات؟", 
                               ["اختر اسمك...", "أنا (Moi)", "أخي الأول", "أخي الثاني"])
    
    st.markdown("---")

    # CHARGEMENT DES DONNÉES EN TEMPS RÉEL
    conn = st.connection("gsheets", type=GSheetsConnection)
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Sheet1", ttl=0)
    except Exception:
        # Création des colonnes si le tableau est totalement vide
        colonnes = ["التاريخ", "ضغط الصباح", "ضغط 16:00", "ضغط المساء", "النبض", 
                    "Levothyrox", "Irbésartan", "فطور خفيف", "غداء", "Aspégic", "Nadloric", "Amlor", "تيزانة", "ملاحظات"]
        df = pd.DataFrame(columns=colonnes)

    # Vérifier s'il y a déjà des données pour aujourd'hui
    today_row = df[df["التاريخ"] == today_str]
    row_exists = not today_row.empty

    # Fonction pour récupérer l'état d'une case
    def check_task_status(column_name):
        if row_exists and column_name in today_row.columns:
            cell_value = str(today_row.iloc[0].get(column_name, ""))
            if "تم" in cell_value:
                return True, cell_value
        return False, ""

    # ==========================================
    # SECTION 1 : MÉDICAMENTS ET REPAS
    # ==========================================
    st.write("### 💊 أدوية وروتين اليوم")
    heure_actuelle = datetime.datetime.now().strftime('%H:%M')

    # Levothyrox
    levo_label = "Levothyrox 50 µg" if is_levo_50 else "Levothyrox 25 µg"
    levo_fait, levo_txt = check_task_status("Levothyrox")
    levo_done = st.checkbox(f"07:00 - {levo_label} (على الريق)", value=levo_fait, disabled=levo_fait)
    if levo_fait: st.caption(f"✅ {levo_txt}")

    # Irbésartan
    irbe_fait, irbe_txt = check_task_status("Irbésartan")
    irbe_done = st.checkbox("08:00 - Irbésartan 300 mg", value=irbe_fait, disabled=irbe_fait)
    if irbe_fait: st.caption(f"✅ {irbe_txt}")

    # Collation
    collat_fait, collat_txt = check_task_status("فطور خفيف")
    collat_done = st.checkbox("10:00 - فطور خفيف (بدون تمر)", value=collat_fait, disabled=collat_fait)
    if collat_fait: st.caption(f"✅ {collat_txt}")

    # Déjeuner
    repas_fait, repas_txt = check_task_status("غداء")
    repas_done = st.checkbox("15:00 - غداء (بدون ملح تماماً)", value=repas_fait, disabled=repas_fait)
    if repas_fait: st.caption(f"✅ {repas_txt}")

    # Aspégic
    asp_fait, asp_txt = check_task_status("Aspégic")
    aspegic_done = st.checkbox("15:30 - Aspégic 100 mg (بعد الأكل)", value=asp_fait, disabled=asp_fait)
    if asp_fait: st.caption(f"✅ {asp_txt}")

    # Nadloric
    if is_nadloric:
        nad_fait, nad_txt = check_task_status("Nadloric")
        nadloric_done = st.checkbox("15:30 - Nadloric 300 mg", value=nad_fait, disabled=nad_fait)
        if nad_fait: st.caption(f"✅ {nad_txt}")
    else:
        st.info("ℹ️ Nadloric 300 mg : راحة اليوم (غير مبرمج).")
        nadloric_done = False
        nad_fait, nad_txt = False, "لا"

    # Amlor
    amlor_fait, amlor_txt = check_task_status("Amlor")
    amlor_done = st.checkbox("16:30 - Amlor 5 mg", value=amlor_fait, disabled=amlor_fait)
    if amlor_fait: st.caption(f"✅ {amlor_txt}")

    # Tisane
    tisane_fait, tisane_txt = check_task_status("تيزانة")
    tisane_done = st.checkbox("18:15 - تيزانة نعناع", value=tisane_fait, disabled=tisane_fait)
    if tisane_fait: st.caption(f"✅ {tisane_txt}")

    st.markdown("---")

    # ==========================================
    # SECTION 2 : CONSTANTES ET NOTES
    # ==========================================
    st.write("### 🩸 قياسات الضغط والنبض")
    val_matin = str(today_row.iloc[0].get("ضغط الصباح", "")) if row_exists and pd.notna(today_row.iloc[0].get("ضغط الصباح")) else ""
    val_16h = str(today_row.iloc[0].get("ضغط 16:00", "")) if row_exists and pd.notna(today_row.iloc[0].get("ضغط 16:00")) else ""
    val_soir = str(today_row.iloc[0].get("ضغط المساء", "")) if row_exists and pd.notna(today_row.iloc[0].get("ضغط المساء")) else ""
    
    try:
        val_pouls = int(today_row.iloc[0].get("النبض", 70)) if row_exists and pd.notna(today_row.iloc[0].get("النبض")) else 70
    except ValueError:
        val_pouls = 70

    col1, col2 = st.columns(2)
    with col1:
        tension_matin = st.text_input("ضغط الصباح", value=val_matin)
        tension_16h = st.text_input("ضغط 16:00", value=val_16h)
    with col2:
        tension_soir = st.text_input("ضغط المساء", value=val_soir)
        pouls = st.number_input("النبض (bpm)", min_value=40, max_value=120, value=val_pouls)

    notes_anciennes = str(today_row.iloc[0].get("ملاحظات", "")) if row_exists and pd.notna(today_row.iloc[0].get("ملاحظات")) else ""
    notes = st.text_area("ملاحظات اليوم (أعراض، تفاصيل الوجبات...)", value=notes_anciennes)

    # ==========================================
    # BOUTON DE SAUVEGARDE INTELLIGENT
    # ==========================================
    if st.button("💾 حفظ وتحديث البيانات", type="primary", key="btn_daily"):
        if utilisateur == "اختر اسمك...":
            st.error("⚠️ من فضلك اختر اسمك أولاً من أعلى الصفحة قبل الحفظ!")
        else:
            try:
                # Fonction pour générer le texte de suivi
                def get_status(is_done, was_done, old_txt):
                    if was_done: return old_txt
                    if is_done: return f"تم (بواسطة {utilisateur} الساعة {heure_actuelle})"
                    return "لا"

                nouvelles_donnees = {
                    "التاريخ": today_str,
                    "ضغط الصباح": tension_matin,
                    "ضغط 16:00": tension_16h,
                    "ضغط المساء": tension_soir,
                    "النبض": pouls,
                    "Levothyrox": get_status(levo_done, levo_fait, levo_txt),
                    "Irbésartan": get_status(irbe_done, irbe_fait, irbe_txt),
                    "فطور خفيف": get_status(collat_done, collat_fait, collat_txt),
                    "غداء": get_status(repas_done, repas_fait, repas_txt),
                    "Aspégic": get_status(aspegic_done, asp_fait, asp_txt),
                    "Nadloric": get_status(nadloric_done, nad_fait, nad_txt) if is_nadloric else "لا",
                    "Amlor": get_status(amlor_done, amlor_fait, amlor_txt),
                    "تيزانة": get_status(tisane_done, tisane_fait, tisane_txt),
                    "ملاحظات": notes
                }

                if row_exists:
                    idx = df[df["التاريخ"] == today_str].index[0]
                    for clé, valeur in nouvelles_donnees.items():
                        df[clé] = df[clé].astype(object) # الحل الجذري لمشكلة 11/70
                        df.at[idx, clé] = valeur
                else:
                    new_row = pd.DataFrame([nouvelles_donnees])
                    df = pd.concat([df, new_row], ignore_index=True)

                conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Sheet1", data=df)
                st.success("تم تحديث البيانات بنجاح! ستظهر التعديلات عند باقي الإخوة فوراً.")
                st.balloons()
                st.rerun()
                
            except Exception as e:
                st.error("حدث خطأ أثناء الاتصال بالجدول.")
                st.exception(e)

# ==========================================
# ONGLET 2 : ANALYSES SANGUINES
# ==========================================
with tab_analysis:
    st.write("### 📊 تسجيل نتائج التحاليل الطبية")
    
    analysis_date = st.date_input("تاريخ إجراء التحليل", datetime.date.today())
    
    col_an1, col_an2 = st.columns(2)
    with col_an1:
        tsh_val = st.number_input("TSH (mIU/L)", min_value=0.0, value=2.5, step=0.1, format="%.2f")
        uric_val = st.number_input("حمض اليوريك Acide Urique (mg/L)", min_value=0.0, value=40.0, step=1.0)
    with col_an2:
        creat_val = st.number_input("الكرياتينين Créatinine (mg/L)", min_value=0.0, value=10.0, step=0.5)
        hemo_val = st.number_input("الهيموجلوبين Hémoglobine (g/dL)", min_value=0.0, value=12.0, step=0.1)

    if st.button("💾 حفظ نتائج التحاليل", type="primary", key="btn_analysis"):
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            try:
                existing_analyses = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Analyses", ttl=0)
            except Exception:
                existing_analyses = pd.DataFrame(columns=["التاريخ", "TSH", "الكرياتينين", "الهيموجلوبين", "حمض اليوريك"])
            
            new_analysis_row = pd.DataFrame([{
                "التاريخ": analysis_date.strftime('%d/%m/%Y'),
                "TSH": tsh_val,
                "الكرياتينين": creat_val,
                "الهيموجلوبين": hemo_val,
                "حمض اليوريك": uric_val
            }])
            
            updated_analyses = pd.concat([existing_analyses, new_analysis_row], ignore_index=True)
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Analyses", data=updated_analyses)
            st.success("تم حفظ نتائج التحاليل بنجاح!")
            st.balloons()
            
        except Exception as e:
            st.error("حدث خطأ أثناء حفظ التحاليل.")
            st.exception(e)

    st.markdown("---")
    st.write("### 📈 مخططات التطور")
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_show = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="Analyses", ttl=0)
        
        if not df_show.empty:
            st.dataframe(df_show, use_container_width=True)
            st.write("#### 📉 منحنى تطور TSH")
            st.line_chart(df_show, x="التاريخ", y="TSH")
            st.write("#### 📉 منحنى تطور حمض اليوريك")
            st.line_chart(df_show, x="التاريخ", y="حمض اليوريك")
        else:
            st.info("لا توجد تحاليل مسجلة بعد.")
    except Exception:
        st.info("لم يتم العثور على بيانات سابقة. سيظهر الجدول والمنحنيات هنا فور حفظ أول تحليل.")
