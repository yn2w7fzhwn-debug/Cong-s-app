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


  # Génération d'un fichier Excel stylé avec Pandas et XlsxWriter (couleurs pro, zébrage, grille visible)
  @st.cache_data
  func = lambda df: None  # Dummy for syntax if needed


  output = io.BytesIO()
  with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    df_data.to_excel(writer, sheet_name="Suivi Congés", index=False)
    workbook = writer.book
    worksheet = writer.sheets["Suivi Congés"]

    # Afficher le quadrillage
    worksheet.hide_gridlines(0)

    # Formats de style
    header_format = workbook.add_format({
        "bold": True,
        "font_color": "white",
        "bg_color": "#1F4E78",
        "align": "center",
        "valign": "center",
        "border": 1,
    })

    cell_format_center = workbook.add_format({
        "align": "center",
        "valign": "center",
        "border": 1,
    })

    cell_format_left = workbook.add_format({
        "align": "left", "valign": "center", "border": 1
    })

    zebra_format_center = workbook.add_format({
        "align": "center",
        "valign": "center",
        "bg_color": "#F2F5F8",
        "border": 1,
    })

    zebra_format_left = workbook.add_format({
        "align": "left", "valign": "center", "bg_color": "#F2F5F8", "border": 1
    })

    # Appliquer le format des en-têtes
    for col_num, value in enumerate(df_data.columns.values):
      worksheet.write(0, col_num, value, header_format)

    # Appliquer le format des lignes (zébrage + bordures + centrage)
    for row_idx in range(len(df_data)):
      is_even = row_idx % 2 != 0
      for col_idx, col_name in enumerate(df_data.columns):
        val = df_data.iloc[row_idx, col_idx]
        if pd.isna(val):
          val = ""

        # Choix du format selon la colonne et la ligne
        is_centered = col_idx in [0, 2, 3, 6, 7, 8, 9]

        if is_even:
          f = zebra_format_center if is_centered else zebra_format_left
        else:
          f = cell_format_center if is_centered else cell_format_left

        worksheet.write(row_idx + 1, col_idx, val, f)

    # Ajustement automatique des largeurs de colonnes
    for i, col in enumerate(df_data.columns):
      max_len = max(
          df_data[col].astype(str).map(len).max(), len(str(col))
      ) + 4
      worksheet.set_column(i, i, max(max_len, 12))

  excel_data = output.getvalue()

  st.download_button(
      label="📥 Télécharger le fichier Excel coloré & stylé (.xlsx)",
      data=excel_data,
      file_name="mon_suivi_conges_colore.xlsx",
      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  )
else:
  st.info("Aucune donnée enregistrée pour le moment.")

else:
  st.info("Aucune donnée enregistrée pour le moment.")
