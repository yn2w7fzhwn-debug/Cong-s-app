import datetime
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

# Section Historique & Téléchargement Excel Coloré Natif
st.markdown("---")
st.subheader("📂 Historique & Fichier Excel Coloré")
if not df_data.empty:
  st.dataframe(df_data)

  # Génération d'un fichier Excel stylé (en-têtes bleus #1F4E78, texte blanc, lignes zébrées, bordures) sans aucune dépendance externe
  xml_rows = []
  # Ligne d'en-tête
  header_cells = "".join([
      '<Cell ss:StyleID="Header"><Data ss:Type="String">'
      + str(col)
      + "</Data></Cell>"
      for col in df_data.columns
  ])
  xml_rows.append(f"<Row>{header_cells}</Row>")

  # Lignes de données avec zébrage
  for idx, row in enumerate(df_data.values):
    style_id = "CellZebra" if idx % 2 == 1 else "CellWhite"
    row_cells = "".join([
        f'<Cell ss:StyleID="{style_id}"><Data ss:Type="String">'
        + (str(val) if pd.notna(val) else "")
        + "</Data></Cell>"
        for val in row
    ])
    xml_rows.append(f"<Row>{row_cells}</Row>")

  excel_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:x="urn:schemas-microsoft-com:office:excel"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:html="http://www.w3.org/TR/REC-html40">
 <Styles>
  <Style ss:ID="Header">
   <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>
   <Borders>
    <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#D9D9D9"/>
    <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#D9D9D9"/>
    <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#D9D9D9"/>
    <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#D9D9D9"/>
   </Borders>
   <Interior ss:Color="#1F4E78" ss:Pattern="Solid"/>
   <Font ss:FontName="Calibri" ss:Size="11" ss:Bold="1" ss:Color="#FFFFFF"/>
  </Style>
  <Style ss:ID="CellWhite">
   <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>
   <Borders>
    <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#D9D9D9"/>
    <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#D9D9D9"/>
    <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#D9D9D9"/>
    <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#D9D9D9"/>
   </Borders>
   <Interior ss:Color="#FFFFFF" ss:Pattern="Solid"/>
   <Font ss:FontName="Calibri" ss:Size="11"/>
  </Style>
  <Style ss:ID="CellZebra">
   <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>
   <Borders>
    <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#D9D9D9"/>
    <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#D9D9D9"/>
    <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#D9D9D9"/>
    <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#D9D9D9"/>
   </Borders>
   <Interior ss:Color="#F2F5F8" ss:Pattern="Solid"/>
   <Font ss:FontName="Calibri" ss:Size="11"/>
  </Style>
 </Styles>
 <Worksheet ss:Name="Suivi Conges">
  <Table>
   {"".join(xml_rows)}
  </Table>
 </Worksheet>
</Workbook>"""

  st.download_button(
      label="📥 Télécharger le fichier Excel coloré (.xls)",
      data=excel_content.encode("utf-8-sig"),
      file_name="mon_suivi_conges_colore.xls",
      mime="application/vnd.ms-excel",
  )
else:
  st.info("Aucune donnée enregistrée pour le moment.")
