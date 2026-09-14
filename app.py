from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

# Configuration de la page pour mobile
st.set_page_config(
    page_title="Suivi Congés & Horaires", page_icon="📅", layout="centered"
)

# Style CSS mobile-friendly
st.markdown(
    """
    <style>
    .main {
        background-color: #f4f6f9;
    }
    .stButton>button {
        width: 100%;
        background-color: #007AFF;
        color: white;
        font-size: 18px;
        padding: 14px;
        border-radius: 12px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("📱 Mon Suivi Mobile")
st.write("Gestion des horaires, pauses et congés (remplace Excel)")

# 1. Sélection de la date
st.subheader("1. Date de l'enregistrement")
date_jour = st.date_input("Date du jour", value=datetime.today())
jour_semaine = date_jour.strftime("%A")
jours_fr = {
    "Monday": "Lundi",
    "Tuesday": "Mardi",
    "Wednesday": "Mercredi",
    "Thursday": "Jeudi",
    "Friday": "Vendredi",
    "Saturday": "Samedi",
    "Sunday": "Dimanche",
}
jour_fr = jours_fr.get(jour_semaine, jour_semaine)
st.info(f"🗓️ **{jour_fr} {date_jour.strftime('%d/%m/%Y')}**")

# 2. Statut / Type de journée (congés, gardes, etc.)
st.subheader("2. Statut / Congé / Observation")
type_entree = st.selectbox(
    "Type",
    [
        "Journée normale",
        "Rec (Récupération)",
        "Férié",
        "Garde",
        "Maladie",
        "Cp (Congé payé)",
        "D45",
        "D50",
        "Autre",
    ],
)
commentaire_libre = st.text_input("Précision / Commentaire optionnel", "")

# 3. Horaires et Pauses
st.subheader("3. Horaires & Vestiaires")

col1, col2 = st.columns(2)
with col1:
    heure_arrivee = st.time_input(
        "Arrivée", value=datetime.strptime("08:00", "%H:%M").time()
    )
    debut_pause = st.time_input(
        "Début Pause", value=datetime.strptime("12:00", "%H:%M").time()
    )
with col2:
    heure_depart = st.time_input(
        "Départ", value=datetime.strptime("17:00", "%H:%M").time()
    )
    fin_pause = st.time_input(
        "Fin Pause", value=datetime.strptime("13:00", "%H:%M").time()
    )

temps_vestiaire = st.selectbox(
    "Temps vestiaire", ["00:00:00", "00:10:00", "00:15:00"]
)

# --- CALCUL AUTOMATIQUE DU CUMUL JOUR ---
# Calcul de la durée de travail nette
dt_arrivee = datetime.combine(datetime.today(), heure_arrivee)
dt_depart = datetime.combine(datetime.today(), heure_depart)
dt_deb_pause = datetime.combine(datetime.today(), debut_pause)
dt_fin_pause = datetime.combine(datetime.today(), fin_pause)

# Si présence d'une pause valide
duree_totale = dt_depart - dt_arrivee
duree_pause = (
    (dt_fin_pause - dt_deb_pause) if dt_fin_pause > dt_deb_pause else timedelta(0)
)
duree_travail = duree_totale - duree_pause

if duree_travail.total_seconds() < 0:
    duree_travail = timedelta(0)

# Affichage du calcul en direct
hours, remainder = divmod(int(duree_travail.total_seconds()), 3600)
minutes, _ = divmod(remainder, 60)
cumul_jour_str = f"{hours:02d}:{minutes:02d}:00"

st.markdown(
    f"""
    <div style="background-color: #e3f2fd; padding: 10px; border-radius: 8px; text-align: center; color: #0d47a1;">
        <b>Cumul estimé pour cette journée : {cumul_jour_str}</b>
    </div>
""",
    unsafe_allow_html=True,
)

# 4. Bouton de Validation & Sauvegarde
st.markdown("<br>", unsafe_allow_html=True)
if st.button("💾 Enregistrer la journée"):
    nouvelle_ligne = {
        "Année": date_jour.year,
        "Mois": date_jour.strftime("%B"),
        "Date": date_jour.strftime("%Y-%m-%d"),
        "Jour": jour_fr,
        "Statut": type_entree,
        "Commentaire": commentaire_libre,
        "Arrivée": str(heure_arrivee),
        "Début Pause": str(debut_pause),
        "Fin Pause": str(fin_pause),
        "Départ": str(heure_depart),
        "Vestiaire": temps_vestiaire,
        "Cumul/Jour": cumul_jour_str,
    }

    df_nouveau = pd.DataFrame([nouvelle_ligne])

    # Enregistrement persistant dans un fichier CSV local
    fichier_csv = "suivi_conges_donnees.csv"
    try:
        df_existant = pd.read_csv(fichier_csv)
        # Éviter les doublons sur la même date si on ré-encode
        df_existant = df_existant[df_existant["Date"] != nouvelle_ligne["Date"]]
        df_final = pd.concat([df_existant, df_nouveau], ignore_index=True)
    except FileNotFoundError:
        df_final = df_nouveau

    # Trier par date
    df_final = df_final.sort_values(by="Date", ascending=False)
    df_final.to_csv(fichier_csv, index=False)
    st.success("✅ Enregistré avec succès dans votre base !")

# 5. Visualisation de l'historique et Soldes
st.markdown("---")
st.subheader("📊 Historique & Récapitulatif")

try:
    df_history = pd.read_csv("suivi_conges_donnees.csv")

    # Compteur rapide des types de congés / statuts encodés
    st.write("### 📌 Compteurs de vos statuts")
    if "Statut" in df_history.columns:
        compteurs = df_history["Statut"].value_counts()
        st.write(compteurs)

    st.write("### 📝 Dernières entrées")
    st.dataframe(
        df_history[
            ["Date", "Jour", "Statut", "Arrivée", "Départ", "Cumul/Jour"]
        ].head(10),
        use_container_width=True,
    )

    # Bouton de téléchargement pour récupérer un fichier CSV propre exploitable à tout moment
    csv_data = df_history.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Télécharger tout mon historique (CSV)",
        csv_data,
        "mon_suivi_conges_complet.csv",
        "text/csv",
    )

except FileNotFoundError:
    st.info("Aucune donnée enregistrée pour le moment. Encodez votre première journée !")
