import streamlit as st
import requests
import io
import base64
import json
import os
from datetime import datetime
import re

# Configuration de la page
st.set_page_config(
    page_title="Nexus AI Assistant",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS Premium
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: radial-gradient(circle at top right, #1a1c2c, #0e1117);
        color: #ffffff;
    }
    
    /* Titre avec effet de lueur */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00d4ff, #0080ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        filter: drop-shadow(0 0 10px rgba(0, 212, 255, 0.3));
    }
    
    /* Sidebar stylisée */
    section[data-testid="stSidebar"] {
        background-color: rgba(22, 27, 34, 0.8);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Boutons stylisés */
    .stButton > button {
        background: linear-gradient(90deg, #00d4ff, #0080ff);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 20px;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.6);
        transform: translateY(-2px);
    }
    
    /* Zones de texte */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: rgba(30, 30, 50, 0.8);
        border: 1px solid rgba(0, 212, 255, 0.3);
        color: white;
        border-radius: 8px;
    }
    
    /* Messages */
    .message-user {
        background: linear-gradient(90deg, rgba(0, 212, 255, 0.1), rgba(0, 128, 255, 0.1));
        border-left: 3px solid #00d4ff;
        padding: 12px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .message-ai {
        background: linear-gradient(90deg, rgba(0, 128, 255, 0.1), rgba(100, 50, 200, 0.1));
        border-left: 3px solid #0080ff;
        padding: 12px;
        border-radius: 8px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialisation de la session
if "conversations" not in st.session_state:
    st.session_state.conversations = {}
    st.session_state.current_conversation = None
    st.session_state.messages = []

# Configuration des modèles
MODELS_CONFIG = {
    "Molmo 2 8B (Vision)": {
        "id": "allenai/molmo-2-8b:free",
        "desc": "Analyse d'images et texte",
        "vision": True
    },
    "DeepSeek Chat": {
        "id": "deepseek/deepseek-chat",
        "desc": "Raisonnement complexe et code",
        "vision": False
    },
    "Llama 2 70B": {
        "id": "meta-llama/llama-2-70b-chat:free",
        "desc": "Conversations naturelles",
        "vision": False
    }
}

def get_api_key():
    """Récupère la clé API OpenRouter"""
    api_key = st.secrets.get("OPENROUTER_API_KEY")
    if not api_key:
        st.error("❌ Clé API OpenRouter non configurée. Veuillez ajouter OPENROUTER_API_KEY dans les secrets Streamlit Cloud.")
        st.stop()
    return api_key

def call_openrouter(messages, model_id, temperature=0.7, max_tokens=2000):
    """Appelle l'API OpenRouter"""
    api_key = get_api_key()
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "Nexus AI Assistant"
    }
    
    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    
    try:
        response = requests.post(
            "https://openrouter.io/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur API: {str(e)}")
        return None

def save_conversations():
    """Sauvegarde les conversations en JSON"""
    with open("conversations.json", "w", encoding="utf-8") as f:
        json.dump(st.session_state.conversations, f, indent=2, ensure_ascii=False)

def load_conversations():
    """Charge les conversations depuis JSON"""
    if os.path.exists("conversations.json"):
        with open("conversations.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Chargement des conversations
st.session_state.conversations = load_conversations()

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown('<div class="main-title">🌌 Nexus</div>', unsafe_allow_html=True)
    
    # Nouveau chat
    if st.button("➕ Nouveau Chat", use_container_width=True):
        conv_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.conversations[conv_id] = {
            "title": "Nouvelle conversation",
            "model": "DeepSeek Chat",
            "messages": [],
            "created": datetime.now().isoformat()
        }
        st.session_state.current_conversation = conv_id
        st.session_state.messages = []
        save_conversations()
        st.rerun()
    
    st.divider()
    
    # Historique des conversations
    st.markdown("### 📚 Historique")
    for conv_id, conv_data in sorted(st.session_state.conversations.items(), reverse=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"💬 {conv_data['title']}", use_container_width=True, key=f"conv_{conv_id}"):
                st.session_state.current_conversation = conv_id
                st.session_state.messages = conv_data.get("messages", [])
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{conv_id}"):
                del st.session_state.conversations[conv_id]
                if st.session_state.current_conversation == conv_id:
                    st.session_state.current_conversation = None
                    st.session_state.messages = []
                save_conversations()
                st.rerun()
    
    st.divider()
    
    # Paramètres
    st.markdown("### ⚙️ Paramètres")
    temperature = st.slider("Température", 0.0, 2.0, 0.7)
    max_tokens = st.slider("Longueur max", 100, 4000, 2000)

# ===== MAIN CONTENT =====
if not st.session_state.current_conversation:
    st.markdown('<div class="main-title">🌌 Nexus AI Assistant</div>', unsafe_allow_html=True)
    st.markdown("""
    ### Bienvenue dans Nexus AI Assistant
    
    Une plateforme IA multimodal complète avec :
    - ✅ Support de 3 modèles IA puissants
    - ✅ Analyse d'images avec Molmo 2 8B
    - ✅ Historique persistant des conversations
    - ✅ Export en Markdown ou Texte
    - ✅ Design premium avec interface néon
    - ✅ 100% Gratuit
    
    **Commencez** en cliquant sur "Nouveau Chat" dans la sidebar ! 🚀
    """)
else:
    conv_data = st.session_state.conversations[st.session_state.current_conversation]
    
    # Titre et modèle
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        new_title = st.text_input("Titre", value=conv_data['title'], key="title_input")
        if new_title != conv_data['title']:
            conv_data['title'] = new_title
            save_conversations()
    
    with col2:
        selected_model = st.selectbox(
            "Modèle",
            list(MODELS_CONFIG.keys()),
            index=list(MODELS_CONFIG.keys()).index(conv_data.get('model', 'DeepSeek Chat')),
            key="model_select"
        )
        if selected_model != conv_data.get('model'):
            conv_data['model'] = selected_model
            st.session_state.messages = []
            save_conversations()
            st.rerun()
    
    with col3:
        if st.button("📥 Export"):
            if st.session_state.messages:
                export_text = "\n".join([f"**{msg['role'].upper()}**: {msg['content']}" for msg in st.session_state.messages])
                st.download_button("📄 TXT", export_text, f"conversation.txt")
                st.download_button("📝 Markdown", export_text, f"conversation.md")
    
    st.divider()
    
    # Affichage des messages
    for msg in st.session_state.messages:
        if msg['role'] == 'user':
            st.markdown(f'<div class="message-user"><b>Vous:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="message-ai"><b>Nexus:</b> {msg["content"]}</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Zone de saisie
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_area("Votre message", placeholder="Posez votre question...", height=100)
    with col2:
        send_button = st.button("📤 Envoyer", use_container_width=True)
    
    # Traitement du message
    if send_button and user_input:
        # Ajouter le message utilisateur
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Préparer les messages pour l'API
        api_messages = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
        
        # Appeler l'API
        with st.spinner("🤖 Nexus réfléchit..."):
            model_id = MODELS_CONFIG[selected_model]["id"]
            response = call_openrouter(api_messages, model_id, temperature, max_tokens)
            
            if response:
                st.session_state.messages.append({"role": "assistant", "content": response})
                conv_data['messages'] = st.session_state.messages
                save_conversations()
                st.rerun()

# Statistiques
st.sidebar.divider()
st.sidebar.markdown("### 📊 Statistiques")
total_messages = sum(len(conv['messages']) for conv in st.session_state.conversations.values())
total_conversations = len(st.session_state.conversations)
st.sidebar.metric("Conversations", total_conversations)
st.sidebar.metric("Messages", total_messages)

# Guide
with st.sidebar.expander("❓ Guide d'utilisation"):
    st.markdown("""
    **Démarrage rapide :**
    1. Cliquez sur "Nouveau Chat"
    2. Sélectionnez un modèle
    3. Posez votre question
    4. Exportez la conversation si besoin
    
    **Modèles disponibles :**
    - **Molmo 2 8B** : Analyse d'images
    - **DeepSeek** : Raisonnement complexe
    - **Llama 2 70B** : Conversations naturelles
    
    **Conseils :**
    - Augmentez la température pour plus de créativité
    - Baissez-la pour plus de précision
    - L'historique est sauvegardé automatiquement
    """)
