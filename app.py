import datetime
import os
import pandas as pd
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Suivi Congés & Horaires", page_icon="📱", layout="centered"
)

# Style CSS pour mobile-friendly
st.markdown(
    """
    <style>
    .main {
        background-color: #f4f6f9;
    }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.6rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("📱 Mon Suivi Mobile")
st.write("Gestion des horaires, pauses et congés (remplace Excel)")

# Fichier de stockage local (CSV)
DATA_FILE = "mon_suivi_conges_complet.csv"


# Fonction pour charger les données avec encodage utf-8-sig pour les accents Excel
def load_data():
  if os.path.exists(DATA_FILE):
    try:
      return pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    except Exception:
      return pd.DataFrame()
  return pd.DataFrame()


df_data = load_data()

# 1. Date de l'enregistrement (Format JJ/MM/AAAA visible)
st.subheader("1. Date de l'enregistrement")
date_du_jour = st.date_input(
    "Date du jour", value=datetime.date(2026, 9, 14), format="DD/MM/YYYY"
)

# 2. Statut / Congé / Observation
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

# 3. Horaires & Vestiaires
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

# Calculs automatiques
# (Logique de calcul simplifiée pour l'enregistrement)
if st.button("💾 Enregistrer la journée"):
  # Formater la date proprement au format JJ/MM/AAAA pour le fichier
  date_formatee = date_du_jour.strftime("%d/%m/%Y")
  jour_semaine = date_du_jour.strftime("%A")

  nouvelle_ligne = {
      "Année": date_du_jour.year,
      "Mois": date_du_jour.strftime("%B"),
      "Date": date_formatee,
      "Jour": jour_semaine,
      "Statut": type_journee,
      "Commentaire": commentaire,
      "Arrivée": heure_arrivee.strftime("%H:%M"),
      "Départ": heure_depart.strftime("%H:%M"),
      "Début Pause": debut_pause.strftime("%H:%M"),
      "Fin Pause": fin_pause.strftime("%H:%M"),
  }

  df_new = pd.DataFrame([nouvelle_ligne])

  if not df_data.empty:
    df_final = pd.concat([df_data, df_new], ignore_index=True)
  else:
    df_final = df_new

  # Sauvegarde avec utf-8-sig pour des accents parfaits dans Excel
  df_final.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
  st.success("✅ Enregistré avec succès !")

# Section Historique / Export Excel
st.markdown("---")
st.subheader("📂 Historique & Fichier Excel")
if not df_data.empty:
  st.dataframe(df_data)

  with open(DATA_FILE, "rb") as f:
    st.download_button(
        label="📥 Télécharger le fichier Excel complet",
        data=f,
        file_name="mon_suivi_conges.csv",
        mime="text/csv",
    )
else:
  st.info("Aucune donnée enregistrée pour le moment.")
