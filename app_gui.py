"""Fieldwire to Teams - Streamlit GUI Application"""
import streamlit as st
import requests
import json
from datetime import datetime
import time
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(
    page_title="Fieldwire to Teams",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stCard {
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 5px;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("📄 Fieldwire ↔️ Teams Integration")
st.markdown("""Automātiski skaisti formatēti Task atjauninājumi uz Microsoft Teams kanālu.""")

# Sidebar
with st.sidebar:
    st.header("⚙️ Konfigurācija")
    st.markdown("---")
    
    api_token = st.text_input(
        "Fieldwire API Token",
        value=os.getenv('FIELDWIRE_API_TOKEN', ''),
        type="password",
        help="Ņemiet no Fieldwire Account Settings"
    )
    
    region = st.selectbox(
        "API Regionāls",
        ["us", "eu"],
        help="ASV vai Eiropas serveri"
    )
    
    webhook_url = st.text_input(
        "Teams Webhook URL",
        value=os.getenv('TEAMS_WEBHOOK_URL', ''),
        type="password",
        help="Microsoft Teams Incoming Webhook"
    )
    
    st.markdown("---")
    st.info("📄 Lietotāja palidziba pie labās puses")

# Main Content
tabs = st.tabs(["TestJSON", "Projekti", "Logu Redaktārs", "Par aplikāciju"])

# Tab 1: Test
with tabs[0]:
    st.header("Testēt Savienojumu")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. JWT Token")
        if st.button("Testēt Fieldwire Autentifikāciju", key="test_jwt"):
            if not api_token:
                st.error("\u26a0️ API token nav ievadīts!")
            else:
                try:
                    with st.spinner("Testēju JWT token..."):
                        headers = {
                            "accept": "application/json",
                            "content-type": "application/json"
                        }
                        base_url = f"https://client-api.super.fieldwire.com" if region == "us" else "https://client-api.fieldwire.eu"
                        
                        response = requests.post(
                            f"{base_url}/api_keys/jwt",
                            json={"api_token": api_token},
                            headers=headers,
                            timeout=10
                        )
                        
                        if response.status_code == 201:
                            data = response.json()
                            st.success("\u2705 JWT Token Sekmīgi Iegūts!")
                            st.json({
                                "access_token": data.get('access_token')[:50] + "...",
                                "expires_at": data.get('expires_at')
                            })
                            st.session_state.jwt_token = data.get('access_token')
                            st.session_state.base_url = base_url
                        else:
                            st.error(f"\u274c Kļūda: {response.status_code}")
                            st.code(response.text)
                except Exception as e:
                    st.error(f"\u274c Savienojuma Kļūda: {str(e)}")
    
    with col2:
        st.subheader("2. Teams Webhook")
        if st.button("Testēt Teams Savienojumu", key="test_teams"):
            if not webhook_url:
                st.error("\u26a0️ Teams Webhook URL nav ievadīts!")
            else:
                try:
                    with st.spinner("Testēju Teams webhuku..."):
                        test_card = {
                            "type": "message",
                            "attachments": [
                                {
                                    "contentType": "application/vnd.microsoft.card.adaptive",
                                    "content": {
                                        "\$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                                        "type": "AdaptiveCard",
                                        "version": "1.4",
                                        "body": [
                                            {
                                                "type": "TextBlock",
                                                "text": "\ud83d\udcc4 Fieldwire to Teams Integration",
                                                "weight": "bolder",
                                                "size": "large",
                                                "color": "accent"
                                            },
                                            {
                                                "type": "TextBlock",
                                                "text": "Test Ziņojums - Savienojums Veiksmīgs!",
                                                "spacing": "medium"
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                        
                        response = requests.post(
                            webhook_url,
                            json=test_card,
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            st.success("\u2705 Test Ziņojums Nosūtīts Teams!")
                            st.info("Pārbaudiet savu Teams kanālu - jāredz test ziņojums")
                        else:
                            st.error(f"\u274c Kļūda: {response.status_code}")
                except Exception as e:
                    st.error(f"\u274c Savienojuma Kļūda: {str(e)}")

# Tab 2: Projekti
with tabs[1]:
    st.header("Fieldwire Projekti")
    
    if st.button("Ielādēt Projektus", key="load_projects"):
        if not api_token:
            st.error("\u26a0️ API token nav ievadīts!")
        elif 'jwt_token' not in st.session_state:
            st.error("\u26a0️ Vispirms testējiet JWT token")
        else:
            try:
                with st.spinner("Ielādēju projektus..."):
                    headers = {
                        "Authorization": f"Bearer {st.session_state.jwt_token}",
                        "accept": "application/json"
                    }
                    
                    response = requests.get(
                        f"{st.session_state.base_url}/projects",
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        projects = response.json()
                        st.success(f"\u2705 Atrasti {len(projects)} projekti")
                        
                        for i, proj in enumerate(projects, 1):
                            with st.expander(f"{i}. {proj.get('name', 'Unnamed')}"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**ID:** {proj.get('id')}")
                                    st.write(f"**Status:** {proj.get('status', 'N/A')}")
                                with col2:
                                    st.write(f"**Izveidots:** {proj.get('created_at', 'N/A')}")
                                    st.write(f"**Apraksts:** {proj.get('description', 'Nav')[:100]}...")
                    else:
                        st.error(f"\u274c Kļūda: {response.status_code}")
            except Exception as e:
                st.error(f"\u274c Kļūda: {str(e)}")

# Tab 3: Card Editor
with tabs[2]:
    st.header("Adaptive Card Redaktārs")
    
    card_json = st.text_area(
        "Rediģējiet Adaptive Card JSON",
        value="""{
  "\$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.4",
  "body": [
    {
      "type": "TextBlock",
      "text": "Task Nosaukums",
      "weight": "bolder",
      "size": "large"
    },
    {
      "type": "FactSet",
      "facts": [
        {"name": "Status:", "value": "In Progress"},
        {"name": "Assigned to:", "value": "John Doe"}
      ]
    }
  ]
}""",
        height=300,
        language="json"
    )
    
    if st.button("Pārskatīt Priekšskatījumu", key="preview_card"):
        try:
            card_data = json.loads(card_json)
            st.json(card_data)
            st.success("\u2705 JSON pareizs!")
        except json.JSONDecodeError as e:
            st.error(f"\u274c JSON Kļūda: {str(e)}")

# Tab 4: About
with tabs[3]:
    st.header("Par Aplikāciju")
    
    st.markdown("""
    ### 📄 Fieldwire to Teams Integration
    
    **Versija:** 1.0.0
    **Autors:** DeoxiD (2026)
    
    #### Iespējas:
    - ✅ JWT Autentifikācija ar Fieldwire API
    - ✅ Adaptive Cards Fieldwire Task atjauninājumiem
    - ✅ Microsoft Teams Webhook Integrācija
    - ✅ GUI Interfejs (Streamlit)
    - ✅ Modulāra Arhitektūra
    
    #### Lietošana:
    1. Ievadiet Fieldwire API token
    2. Pārbaudiet JWT un Teams savienojumus
    3. Ielādējiet projektus
    4. Rediģējiet Adaptive Cards pēc nepieciešamības
    5. Sūtiet uz Teams kanālu
    
    #### Dokumentācija:
    - GitHub: https://github.com/DeoxiD/fieldwire-to-teams
    - README: README.md fails repozitorijā
    
    ---
    Made with ❤️ in Riga, Latvia
    """)
    
    st.divider()
    
    st.info("📄 **Padoms:** Rediģējiet .env failu, lai saglabātu kredenciālus automātiski")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**👨‍💻 Izstrādātājs:** DeoxiD")
with col2:
    st.markdown("**📄 Versija:** 1.0.0")
with col3:
    st.markdown("**🛜 Valoda:** Python 3.8+")
