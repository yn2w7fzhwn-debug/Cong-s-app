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
        background-color: #1f4e78;
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
st.write("Gestion des horaires, pauses et congés")

# Fichier de stockage local (CSV)
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
  df_data = df_final

# Section Historique / Export Fichier Coloré & Stylé
st.markdown("---")
st.subheader("📂 Historique & Fichier Tableur Coloré")
if not df_data.empty:
  st.dataframe(df_data)


  # Fonction de génération d'un fichier Excel stylé (openpyxl)
  def create_styled_excel(df):
    output = io.BytesIO()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Suivi Congés"

    # Activer le quadrillage
    ws.views.sheetView[0].showGridLines = True

    # Couleurs et styles
    header_fill = PatternFill(
        start_color="1F4E78", end_color="1F4E78", fill_type="solid"
    )
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

    zebra_fill = PatternFill(
        start_color="F2F5F8", end_color="F2F5F8", fill_type="solid"
    )
    white_fill = PatternFill(
        start_color="FFFFFF", end_color="FFFFFF", fill_type="solid"
    )

    border_thin = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9"),
    )

    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")

    # Écriture des en-têtes
    for col_num, header_title in enumerate(df.columns, 1):
      cell = ws.cell(row=1, column=col_num, value=header_title)
      cell.fill = header_fill
      cell.font = header_font
      cell.alignment = align_center
      cell.border = border_thin

    # Écriture des données avec alternance de couleurs (effet zébré)
    for row_num, row_data in enumerate(df.itertuples(index=False), 2):
      is_even = row_num % 2 == 0
      current_fill = zebra_fill if is_even else white_fill

      for col_num, val in enumerate(row_data, 1):
        cell = ws.cell(row=row_num, column=col_num, value=val)
        cell.fill = current_fill
        cell.border = border_thin
        # Centrer les dates, jours, statuts et heures ; aligner à gauche les commentaires
        if col_num in [1, 3, 4, 7, 8, 9, 10]:
          cell.alignment = align_center
        else:
          cell.alignment = align_left

    # Ajustement automatique de la largeur des colonnes
    for col in ws.columns:
      max_len = 0
      col_letter = get_column_letter(col[0].column)
      for cell in col:
        if cell.value:
          max_len = max(max_len, len(str(cell.value)))
      ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    wb.save(output)
    output.seek(0)
    return output


  excel_data = create_styled_excel(df_data)

  st.download_button(
      label="📥 Télécharger le fichier Excel coloré (.xlsx)",
      data=excel_data,
      file_name="mon_suivi_conges_colore.xlsx",
      mime="application/xlsx",
  )
else:
  st.info("Aucune donnée enregistrée pour le moment.")
