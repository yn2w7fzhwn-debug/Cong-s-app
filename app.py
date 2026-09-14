import datetime
import os
import pandas as pd
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Suivi Congés & Horaires", page_icon="📱", layout="centered"
)

# Style CSS épuré et moderne
st.markdown(
    """
    <style>
    .main {
        background-color: #f4f6f9;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f4e78;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.6rem;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("📱 Mon Suivi & Solde d'Heures")
st.write("Gestion des horaires, pauses et calcul du solde à récupérer")

DATA_FILE = "mon_suivi_conges_complet.csv"


def load_data():
  if os.path.exists(DATA_FILE):
    try:
      return pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    except Exception:
      return pd.DataFrame()
  return pd.DataFrame()


df_data = load_data()

# --- CALCUL DU SOLDE D'HEURES ---
# On estime une journée standard à 7h36 (soit 7.6 heures) ou 38h/semaine
HEURE_ATTENDUE_JOUR = 7.6

total_heures_faites = 0.0
total_heures_attendues = 0.0

if not df_data.empty and "Cumul_Heures" in df_data.columns:
  # On additionne les heures réelles si enregistrées
  pass
# --------------------------------

# 1. Date
st.subheader("1. Date de l'enregistrement")
date_du_jour = st.date_input(
    "Date du jour", value=datetime.date.today(), format="DD/MM/YYYY"
)

# 2. Type & Commentaire
st.subheader("2. Statut / Congé / Observation")
type_journee = st.selectbox(
    "Type",
    [
        "Journée normale",
        "Congé payé (Cp)",
        "Récupération (Rec)",
        "Jour férié (Férié)",
        "Maladie",
        "Autre",
    ],
)
commentaire = st.text_input(
    "Précision / Commentaire optionnel",
    placeholder="Ex: Récup des heures sup...",
)

# 3. Horaires
st.subheader("3. Horaires & Vestiaires")
col1, col2 = st.columns(2)
with col1:
  heure_arrivee = st.time_input(
      "Arrivée", value=datetime.time(8, 0), step=300
  )
with col2:
  heure_depart = st.time_input("Départ", value=datetime.time(17, 0), step=300)

col3, col4 = st.columns(2)
with col3:
  debut_pause = st.time_input(
      "Début Pause", value=datetime.time(12, 0), step=300
  )
with col4:
  fin_pause = st.time_input("Fin Pause", value=datetime.time(12, 30), step=300)

vestiaire_arriver = st.checkbox("Vestiaire à l'arrivée (+5 min)")
vestiaire_depart = st.checkbox("Vestiaire au départ (+5 min)")

# Enregistrement
if st.button("💾 Enregistrer la journée"):
  date_formatee = date_du_jour.strftime("%d/%m/%Y")
  jour_semaine = date_du_jour.strftime("%A")

  # Calcul des heures travaillées pour cette journée (en heures décimales)
  t_arr = datetime.datetime.combine(datetime.date.today(), heure_arrivee)
  t_dep = datetime.datetime.combine(datetime.date.today(), heure_depart)
  t_d_pause = datetime.datetime.combine(datetime.date.today(), debut_pause)
  t_f_pause = datetime.datetime.combine(datetime.date.today(), fin_pause)

  # Si c'est une journée normale ou travail effectif
  if type_journee in ["Journée normale", "Autre"]:
    duree_travail = (t_dep - t_arr) - (t_f_pause - t_d_pause)
    heures_jour = duree_travail.total_seconds() / 3600
    if vestiaire_arriver:
      heures_jour += 5 / 60
    if vestiaire_depart:
      heures_jour += 5 / 60
  else:
    heures_jour = 0.0  # Congé, maladie, récup, etc.

  # Balance du jour (Heures faites - Heures attendues standard de 7h36 soit 7.6h)
  # Pour un congé ou férié, on met l'attendu à 0 ou équivalent selon la règle
  if type_journee == "Journée normale":
    balance_jour = heures_jour - 7.6
  else:
    balance_jour = 0.0

  nouvelle_ligne = {
      "Année": date_du_jour.year,
      "Mois": date_du_jour.strftime("%B"),
      "Date": date_formatee,
      "Jour": jour_semaine,
      "Statut": type_journee,
      "Commentaire": commentaire,
      "Heures Faites": round(heures_jour, 2),
      "Balance (h)": round(balance_jour, 2),
  }

  df_new = pd.DataFrame([nouvelle_ligne])

  if not df_data.empty:
    df_final = pd.concat([df_data, df_new], ignore_index=True)
  else:
    df_final = df_new

  df_final.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
  st.success("✅ Enregistré avec succès !")
  df_data = df_final

# --- AFFICHAGE DU SOLDE TOTAL À RÉCUPÉRER ---
st.markdown("---")
st.subheader("⏱️ Solde total des heures à récupérer")

if not df_data.empty and "Balance (h)" in df_data.columns:
  solde_total = df_data["Balance (h)"].sum()
  
  # Affichage visuel en grand
  if solde_total >= 0:
    st.metric(
        label="Heures cumulées en positif (à récupérer / crédit)",
        value=f"+ {solde_total:.2f} h",
    )
  else:
    st.metric(
        label="Heures en négatif (déficit)",
        value=f"{solde_total:.2f} h",
    )
else:
  st.metric(label="Solde total", value="0.00 h")

# Section Historique & Téléchargement
st.markdown("---")
st.subheader("📂 Historique complet")
if not df_data.empty:
  st.dataframe(df_data)

  csv_data = df_data.to_csv(index=False, sep=";", encoding="utf-8-sig").encode(
      "utf-8-sig"
  )

  st.download_button(
      label="📥 Télécharger le fichier de suivi (.csv)",
      data=csv_data,
      file_name="mon_suivi_conges.csv",
      mime="text/csv",
  )
else:
  st.info("Aucune donnée enregistrée pour le moment.")
