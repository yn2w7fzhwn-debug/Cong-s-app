# Section Historique & Téléchargement VRAI Excel .xlsx stylisé
st.markdown("---")
st.subheader("📂 Historique & Fichier Excel (.xlsx)")
if not df_data.empty:
  st.dataframe(df_data)

  # Création d'un vrai fichier Excel stylisé avec openpyxl
  output = io.BytesIO()
  with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df_data.to_excel(writer, index=False, sheet_name="Suivi")

  # Récupération et stylisation avancée avec openpyxl
  output.seek(0)
  import openpyxl
  from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

  wb = openpyxl.load_workbook(output)
  ws = wb.active

  # Style des en-têtes (Bleu pro, texte blanc, centré)
  header_fill = PatternFill(
      start_color="1F4E78", end_color="1F4E78", fill_type="solid"
  )
  header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
  align_center = Alignment(horizontal="center", vertical="center")
  thin_border = Border(
      left=Side(style="thin", color="D9D9D9"),
      right=Side(style="thin", color="D9D9D9"),
      top=Side(style="thin", color="D9D9D9"),
      bottom=Side(style="thin", color="D9D9D9"),
  )

  for col in range(1, len(df_data.columns) + 1):
    cell = ws.cell(row=1, column=col)
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = align_center
    cell.border = thin_border

  # Style des lignes de données (Zébrage et bordures)
  zebra_fill = PatternFill(
      start_color="F2F5F8", end_color="F2F5F8", fill_type="solid"
  )
  regular_font = Font(name="Calibri", size=11)

  for row in range(2, len(df_data) + 2):
    is_even = row % 2 == 0
    for col in range(1, len(df_data.columns) + 1):
      cell = ws.cell(row=row, column=col)
      cell.font = regular_font
      cell.alignment = align_center
      cell.border = thin_border
      if is_even:
        cell.fill = zebra_fill

  # Sauvegarde finale dans un buffer propre
  final_output = io.BytesIO()
  wb.save(final_output)
  excel_bytes = final_output.getvalue()

  st.download_button(
      label="📥 Télécharger le VRAI fichier Excel (.xlsx)",
      data=excel_bytes,
      file_name="mon_suivi_conges.xlsx",
      mime=(
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      ),
  )
else:
  st.info("Aucune donnée enregistrée pour le moment.")
