import datetime
import io
import os
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
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
st.write(
    "Gestion des horaires, pauses et congés (remplace Excel avec mise en"
    " forme)"
)

# Fichier de stockage local (CSV pour la mémoire de l'app)
DATA_FILE = "mon_suivi_conges_complet.csv"


def load_data():
  if os.path.exists(DATA_FILE):
    try:
      return pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    except Exception:
      return pd.DataFrame()
  return pd.DataFrame()


df_data = load_data()

# 1. Date de l'enregistrement
st.subheader("1. Date de l'enregistrement")
date_du_jour = st.date_input(
    "Date du jour", value=datetime.date.today(), format="DD/MM/YYYY"
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

# Enregistrement
if st.button("💾 Enregistrer la journée"):
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

  df_final.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
  st.success("✅ Enregistré avec succès !")
  df_data = df_final  # Met à jour l'affichage direct


# Fonction pour générer un fichier Excel stylisé (.xlsx)
def create_styled_excel(df):
  output = io.BytesIO()
  wb = openpyxl.Workbook()
  ws = wb.active
  ws.title = "Suivi Congés"

  # En-têtes et données
  headers = list(df.columns)
  ws.append(headers)

  for _, row in df.iterrows():
    ws.append(list(row))

  # Styles professionnels (Palette Bleu nuit / Muted)
  header_fill = PatternFill(
      start_color="1F4E78", end_color="1F4E78", fill_type="solid"
  )
  header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
  data_font = Font(name="Arial", size=10)
  thin_border = Border(
      left=Side(style="thin", color="D3D3D3"),
      right=Side(style="thin", color="D3D3D3"),
      top=Side(style="thin", color="D3D3D3"),
      bottom=Side(style="thin", color="D3D3D3"),
  )
  zebra_fill = PatternFill(
      start_color="F9FAFB", end_color="F9FAFB", fill_type="solid"
  )

  # Application du style sur l'en-tête
  for col_num in range(1, len(headers) + 1):
    cell = ws.cell(row=1, column=col_num)
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(
        horizontal="center", vertical="center", wrap_text=True
    )

  # Application du style sur les lignes de données
  for row_num in range(2, len(df) + 2):
    is_even = row_num % 2 == 0
    for col_num in range(1, len(headers) + 1):
      cell = ws.cell(row=row_num, column=col_num)
      cell.font = data_font
      cell.border = thin_border
      cell.alignment = Alignment(horizontal="center", vertical="center")
      if is_even:
        cell.fill = zebra_fill

  # Ajustement automatique de la largeur des colonnes
  for col in ws.columns:
    max_len = max(len(str(cell.value or "")) for cell in col)
    col_letter = get_column_letter(col[0].column)
    ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

  wb.save(output)
  output.seek(0)
  return output


# Section Historique / Export Excel (.xlsx stylisé)
st.markdown("---")
st.subheader("📂 Historique & Fichier Excel Pro")
if not df_data.empty:
  st.dataframe(df_data)

  excel_data = create_styled_excel(df_data)

  st.download_button(
      label="📥 Télécharger le VRAI fichier Excel mis en forme (.xlsx)",
      data=excel_data,
      file_name="mon_suivi_conges.xlsx",
      mime=(
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      ),
  )
else:
  st.info("Aucune donnée enregistrée pour le moment.")
