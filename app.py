import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# Configuration de la page
st.set_page_config(
    page_title="Suivi Parc SOBRAGUI - MACAB FROID",
    page_icon="❄️",
    layout="wide"
)

# --- SÉCURITÉ : MOT DE PASSE ADMIN ---
MOT_DE_PASSE_ADMIN = "Sobragui2026"

# --- CHARGEMENT DES LOGOS ET AFFICHAGE EN HAUT ---
def charger_logos():
    try:
        # On utilise des colonnes pour centrer ou aligner les logos
        col_logo1, col_vide, col_logo2 = st.columns([1, 2, 1])
        
        # Logo de l'entreprise qui maintient (MACAB)
        if os.path.exists("logo_macab.png"):
            img_macab = Image.open("logo_macab.png")
            with col_logo1:
                st.image(img_macab, width=150)
        
        # Logo du client (SOBRAGUI)
        if os.path.exists("logo_sobragui.png"):
            img_sobragui = Image.open("logo_sobragui.png")
            with col_logo2:
                # On utilise caption pour rappeler le nom complet
                st.image(img_sobragui, width=150, caption="Société des Boissons Rafraîchissantes de Guinée")
    except Exception as e:
        st.error(f"Erreur lors du chargement des logos : {e}")

# Affichage des logos
charger_logos()

# Titre de l'application
st.markdown("---")
st.title("❄️ Système de Suivi - Parc 1200 Réfrigérateurs")
st.subheader("Outil de maintenance professionnelle par MACAB FROID SARL")
st.markdown("---")

# --- FONCTIONS DE CHARGEMENT DE DONNÉES (Inchangé) ---
@st.cache_data
def charger_referentiel():
    if os.path.exists("liste_frigos.csv"):
        return pd.read_csv("liste_frigos.csv")
    else:
        return pd.DataFrame(columns=["ID_Frigo", "Responsable", "Zone"])

def charger_donnees():
    if os.path.exists("suivi_activites.csv"):
        df = pd.read_csv("suivi_activites.csv")
        df = df.drop_duplicates(subset=["ID_Frigo", "Type", "Action_Detaillee", "Technicien"], keep='last')
        df["N°"] = range(1, len(df) + 1)
        return df
    else:
        return pd.DataFrame(columns=["N°", "Date", "ID_Frigo", "Type", "Action_Detaillee", "Technicien", "Responsable", "Zone"])

# Chargement des bases
df_referentiel = charger_referentiel()

# --- BARRE LATÉRALE : SAISIE TECHNICIEN ---
st.sidebar.header("📝 Nouvelle Intervention")
st.sidebar.markdown("---")

if not df_referentiel.empty:
    id_frigo = st.sidebar.selectbox("ID du Réfrigérateur SOBRAGUI", options=df_referentiel["ID_Frigo"].unique())
    infos_frigo = df_referentiel[df_referentiel["ID_Frigo"] == id_frigo].iloc[0]
    resp_auto = infos_frigo["Responsable"]
    zone_auto = infos_frigo["Zone"]
    st.sidebar.info(f"📍 Responsable : {resp_auto}\n\n🌍 Zone : {zone_auto}")
else:
    st.sidebar.error("Fichier 'liste_frigos.csv' introuvable.")
    id_frigo = st.sidebar.text_input("ID du Réfrigérateur (Manuel)")
    resp_auto, zone_auto = "", ""

type_act = st.sidebar.selectbox("Type d'activité", ["Dépannage", "Entretien"])

if type_act == "Dépannage":
    action = st.sidebar.multiselect("Pièces remplacées", ["Compresseur", "Condensateur", "Ampoule", "Charge en gaz", "Thermostat", "Ventilateur", "Relais", "Déshydrateur"])
else:
    action = st.sidebar.multiselect("Actions effectuées", ["Débouchage", "Soufflage", "Lavage"])

tech = st.sidebar.text_input("Nom du Technicien MACAB FROID")

if st.sidebar.button("Enregistrer l'intervention"):
    signature = f"{id_frigo}-{type_act}-{'-'.join(action)}-{tech}"
    
    if 'derniere_signature' in st.session_state and st.session_state.derniere_signature == signature:
        st.sidebar.warning("⚠️ Déjà enregistré !")
    elif not tech or not action:
        st.sidebar.error("❌ Veuillez remplir le nom du technicien et les actions.")
    else:
        df_actuel = charger_donnees()
        nouveau_suivi = {
            "N°": len(df_actuel) + 1,
            "Date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "ID_Frigo": id_frigo,
            "Type": type_act,
            "Action_Detaillee": ", ".join(action),
            "Technicien": tech,
            "Responsable": resp_auto,
            "Zone": zone_auto
        }
        df_final = pd.concat([df_actuel, pd.DataFrame([nouveau_suivi])], ignore_index=True)
        df_final.to_csv("suivi_activites.csv", index=False)
        st.session_state.derniere_signature = signature
        st.sidebar.success("✅ Intervention enregistrée avec succès !")
        st.rerun()

# --- ACCÈS ADMINISTRATEUR (POUR LES 20 ADMINS DE MACAB/SOBRAGUI) ---
st.sidebar.markdown("---")
st.sidebar.header("🔐 Espace Administrateur")
mode_admin = st.sidebar.checkbox("Afficher le Tableau de Bord")

if mode_admin:
    pwd = st.sidebar.text_input("Mot de passe", type="password")
    if pwd == MOT_DE_PASSE_ADMIN:
        st.sidebar.success("Accès autorisé")
        
        # Affichage du Dashboard
        df_visu = charger_donnees()
        
        st.subheader("📊 Tableau de Bord - Vue Administrateur (MACAB/SOBRAGUI)")
        col1, col2 = st.columns(2)
        with col1:
            filtre_z = st.multiselect("Filtrer par Zone", options=df_visu["Zone"].unique())
        with col2:
            filtre_t = st.multiselect("Filtrer par Technicien", options=df_visu["Technicien"].unique())
            
        df_filtre = df_visu.copy()
        if filtre_z:
            df_filtre = df_filtre[df_filtre["Zone"].isin(filtre_z)]
        if filtre_t:
            df_filtre = df_filtre[df_filtre["Technicien"].isin(filtre_t)]

        st.dataframe(df_filtre, use_container_width=True, hide_index=True)
        
        # Bouton d'exportation
        csv = df_filtre.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exporter les données filtrées (CSV)", csv, "rapport_suivi_sobragui.csv", "text/csv")
        
    elif pwd != "":
        st.sidebar.error("Mot de passe incorrect")
else:
    st.info("👋 Bienvenue. Utilisez la barre latérale pour enregistrer une intervention sur un frigo SOBRAGUI. L'accès aux données globales est réservé aux administrateurs.")