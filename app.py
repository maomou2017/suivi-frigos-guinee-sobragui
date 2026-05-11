import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from streamlit_js_eval import streamlit_js_eval

# 1. Configuration de la page
st.set_page_config(page_title="Suivi SOBRAGUI - MACAB FROID", page_icon="❄️", layout="wide")

# --- CHARGEMENT DES LOGOS ---
def charger_logos():
    try:
        col_logo1, col_vide, col_logo2 = st.columns([1, 2, 1])
        if os.path.exists("logo_macab.png"):
            with col_logo1: st.image("logo_macab.png", width=150)
        if os.path.exists("logo_sobragui.png"):
            with col_logo2: st.image("logo_sobragui.png", width=150)
    except: pass

charger_logos()
st.title("❄️ Système de Suivi - Parc 1200 Réfrigérateurs")
st.markdown("---")

# 2. Fonctions de chargement (AVEC correction accents latin-1)
@st.cache_data
def charger_referentiel():
    if os.path.exists("liste_frigos.csv"):
        # Ajout de l'encoding pour éviter l'erreur Unicode
        return pd.read_csv("liste_frigos.csv", sep=";", encoding="latin-1")
    return pd.DataFrame()

def charger_donnees():
    if os.path.exists("suivi_activites.csv"):
        return pd.read_csv("suivi_activites.csv", sep=";", encoding="latin-1")
    return pd.DataFrame()

df_ref = charger_referentiel()

# --- BARRE LATÉRALE ---
st.sidebar.header("📝 Nouvelle Intervention")

# BOUTON GPS (Ajouté)
if st.sidebar.button("📍 Localiser l'intervention"):
    loc = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition(pos => {return {lat: pos.coords.latitude, lon: pos.coords.longitude}})", key="gps")
    if loc:
        st.session_state.coords = f"{loc['lat']},{loc['lon']}"
        st.sidebar.success(f"Position capturée : {st.session_state.coords}")

# AUTOMATISATION DES INFOS
if not df_ref.empty:
    # On utilise "Code client" pour correspondre à votre fichier CSV
    code_client = st.sidebar.selectbox("Code Client", options=df_ref["Code client"].unique())
    ligne = df_ref[df_ref["Code client"] == code_client].iloc[0]
    
    st.sidebar.info(f"🏪 PDV : {ligne['PDV']}\n\n👤 Vendeur : {ligne['Vendeur']}\n\n🌍 Ville : {ligne['Ville']}")
else:
    st.sidebar.error("Fichier liste_frigos.csv introuvable sur GitHub.")

# SAISIE TECHNIQUE
type_act = st.sidebar.selectbox("Type d'activité", ["Dépannage", "Entretien"])
options = ["Compresseur", "Gaz", "Thermostat", "Ventilateur", "Nettoyage"] if type_act == "Dépannage" else ["Lavage", "Soufflage"]
actions = st.sidebar.multiselect("Actions effectuées", options)
tech = st.sidebar.text_input("Nom du Technicien")

# ENREGISTREMENT
if st.sidebar.button("💾 Enregistrer"):
    if tech and actions:
        df_actuel = charger_donnees()
        nouveau = {
            "Date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Code_Client": code_client,
            "PDV": ligne["PDV"],
            "Vendeur": ligne["Vendeur"],
            "Actions": ", ".join(actions),
            "Technicien": tech,
            "GPS": st.session_state.get('coords', "Non localisé")
        }
        df_final = pd.concat([df_actuel, pd.DataFrame([nouveau])], ignore_index=True)
        df_final.to_csv("suivi_activites.csv", index=False, sep=";", encoding="latin-1")
        st.sidebar.success("✅ Enregistré !")
        st.rerun()

# --- ESPACE ADMIN ---
st.sidebar.markdown("---")
if st.sidebar.checkbox("🔒 Voir les rapports"):
    if st.sidebar.text_input("Mot de passe", type="password") == "Sobragui2026":
        st.subheader("📊 Tableau de Bord")
        st.dataframe(charger_donnees(), use_container_width=True)
