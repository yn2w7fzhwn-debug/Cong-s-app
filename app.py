import datetime
import io
import os
import pandas as pd
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Suivi Congés & Horaires", page_icon="📱", layout="centered"
)

# Style CSS épuré
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

DATA_FILE = "mon_suivi_conges_complet.csv"


def load_data():
  if os.path.exists(DATA_FILE):
    try:
      return pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    except Exception:
      return pd.DataFrame()
  return pd.DataFrame()


df_data = load_data()

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

# Section Historique & Téléchargement Excel Stylé
st.markdown("---")
st.subheader("📂 Historique & Fichier Excel Coloré")
if not df_data.empty:
  st.dataframe(df_data)

  # Génération d'un vrai fichier Excel avec openpyxl (En-têtes bleus #1F4E78, texte blanc, zébrage, bordures)
  output = io.BytesIO()
  try:
    import openpyxl
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
      df_data.to_excel(writer, sheet_name="Suivi Congés", index=False)
      workbook = writer.book
      worksheet = writer.sheets["Suivi Congés"]
      worksheet.views.sheetView[0].showGridLines = True

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

      for col_num, header_title in enumerate(df_data.columns, 1):
        cell = worksheet.cell(row=1, column=col_num, value=header_title)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = align_center
        cell.border = border_thin

      for row_num, row_data in enumerate(df_data.itertuples(index=False), 2):
        is_even = row_num % 2 == 0
        current_fill = zebra_fill if is_even else white_fill
        for col_num, val in enumerate(row_data, 1):
          cell = worksheet.cell(
              row=row_num, column=col_num, value=val if pd.notna(val) else ""
          )
          cell.fill = current_fill
          cell.border = border_thin
          cell.alignment = (
              align_center if col_num in [1, 3, 4, 7, 8, 9, 10] else align_left
          )

    excel_data = output.getvalue()
    st.download_button(
        label="📥 Télécharger le fichier Excel coloré (.xlsx)",
        data=excel_data,
        file_name="mon_suivi_conges_colore.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )
  except Exception as e:
    # Fallback propre si openpyxl rencontre un souci
    csv_data = df_data.to_csv(index=False, sep=";", encoding="utf-8-sig")
    st.download_button(
        label="📥 Télécharger le tableau (.csv)",
        data=csv_data.encode("utf-8-sig"),
        file_name="mon_suivi_conges.csv",
        mime="text/csv",
    )
else:
  st.info("Aucune donnée enregistrée pour le moment.")
