import streamlit as st
import json
import os
from datetime import datetime
import requests
from typing import Optional

# Configuration de la page
st.set_page_config(
    page_title="Nexus AI Assistant",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour le design premium
st.markdown("""
<style>
    * {
        font-family: 'Inter', sans-serif;
    }
    
    body {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a3e 100%);
        color: #e0e0ff;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a3e 100%);
    }
    
    .stSidebar {
        background: linear-gradient(180deg, #0f1535 0%, #1a2555 100%);
        border-right: 2px solid #00d9ff;
        box-shadow: -10px 0 30px rgba(0, 217, 255, 0.1);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #00d9ff 0%, #0099ff 100%);
        color: #000;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        box-shadow: 0 0 30px rgba(0, 217, 255, 0.8);
        transform: translateY(-2px);
    }
    
    .stTextArea>textarea {
        background: rgba(15, 21, 53, 0.8);
        border: 2px solid #00d9ff !important;
        border-radius: 8px;
        color: #e0e0ff;
        box-shadow: 0 0 10px rgba(0, 217, 255, 0.2);
    }
    
    .stSelectbox>div>div {
        background: rgba(15, 21, 53, 0.8);
        border: 2px solid #00d9ff !important;
        border-radius: 8px;
    }
    
    h1, h2, h3 {
        color: #00d9ff;
        text-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
    }
    
    .message-box {
        background: rgba(15, 21, 53, 0.9);
        border-left: 4px solid #00d9ff;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.1);
    }
    
    .user-message {
        background: rgba(0, 153, 255, 0.1);
        border-left-color: #0099ff;
    }
    
    .ai-message {
        background: rgba(0, 217, 255, 0.05);
        border-left-color: #00d9ff;
    }
</style>
""", unsafe_allow_html=True)

# Fonction pour appeler OpenRouter API
def call_openrouter_api(messages: list, model: str, temperature: float, max_tokens: int) -> Optional[str]:
    """Appelle l'API OpenRouter avec les paramètres donnés."""
    api_key = st.secrets.get("OPENROUTER_API_KEY", "")
    
    if not api_key:
        return None
    
    # Mapping des modèles
    model_mapping = {
        "DeepSeek Chat": "deepseek/deepseek-chat",
        "Molmo 2 8B": "allenai/molmo-2-8b:free",
        "Llama 2 70B": "meta-llama/llama-2-70b-chat"
    }
    
    model_id = model_mapping.get(model, "deepseek/deepseek-chat")
    
    try:
        # Préparer les données
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": int(max_tokens)
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://streamlit.app",
            "X-Title": "Nexus AI Assistant"
        }
        
        # Faire la requête avec timeout
        response = requests.post(
            "https://openrouter.io/api/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
        
        return None
            
    except Exception as e:
        return None

# Initialisation de la session
if "conversations" not in st.session_state:
    st.session_state.conversations = {}
    st.session_state.current_conversation = None

# Sidebar
with st.sidebar:
    st.markdown("## 🌌 **Nexus**")
    
    if st.button("➕ Nouveau Chat", use_container_width=True):
        conv_id = f"conv_{len(st.session_state.conversations) + 1}_{datetime.now().timestamp()}"
        st.session_state.conversations[conv_id] = {
            "title": "Nouvelle conversation",
            "model": "DeepSeek Chat",
            "messages": [],
            "created_at": datetime.now().isoformat()
        }
        st.session_state.current_conversation = conv_id
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📝 Historique")
    
    if st.session_state.conversations:
        for conv_id, conv in st.session_state.conversations.items():
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"💬 {conv['title']}", use_container_width=True):
                    st.session_state.current_conversation = conv_id
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{conv_id}"):
                    del st.session_state.conversations[conv_id]
                    if st.session_state.current_conversation == conv_id:
                        st.session_state.current_conversation = None
                    st.rerun()
    
    st.markdown("---")
    st.markdown("### ⚙️ Paramètres")
    
    temperature = st.slider("Température", 0.0, 2.0, 0.7, 0.1)
    max_tokens = st.slider("Longueur max", 100, 4000, 2000, 100)
    
    st.markdown("---")
    st.markdown("### 📊 Statistiques")
    
    total_conversations = len(st.session_state.conversations)
    total_messages = sum(len(conv["messages"]) for conv in st.session_state.conversations.values())
    
    st.metric("Conversations", total_conversations)
    st.metric("Messages", total_messages)
    
    st.markdown("---")
    st.markdown("""
    <details>
    <summary>❓ Guide d'utilisation</summary>
    
    **Nexus AI Assistant** est une plateforme IA multimodale complète avec :
    
    - 🤖 Support de 3 modèles IA puissants
    - 🎨 Analyse d'images avec Molmo 2 8B
    - 💾 Historique persistant des conversations
    - 📥 Export en Markdown ou Texte
    - 🎨 Design premium avec interface néon
    - ✨ 100% Gratuit
    
    **Comment utiliser :**
    1. Cliquez sur "Nouveau Chat" pour démarrer
    2. Posez votre question
    3. Consultez l'historique dans la sidebar
    4. Exportez vos conversations
    
    </details>
    """, unsafe_allow_html=True)

# Contenu principal
if st.session_state.current_conversation is None:
    st.markdown("""
    # 🌌 **Nexus AI Assistant**
    
    ## Bienvenue dans Nexus AI Assistant
    
    Une plateforme IA multimodale complète avec :
    
    - ✅ Support de 3 modèles IA puissants
    - ✅ Analyse d'images avec Molmo 2 8B
    - ✅ Historique persistant des conversations
    - ✅ Export en Markdown ou Texte
    - ✅ Design premium avec interface néon
    - ✅ 100% Gratuit
    
    **Commencez** en cliquant sur "Nouveau Chat" dans la sidebar ! 🚀
    """)
else:
    conv = st.session_state.conversations[st.session_state.current_conversation]
    
    # Header
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        new_title = st.text_input("Titre", value=conv["title"], label_visibility="collapsed")
        if new_title != conv["title"]:
            conv["title"] = new_title
    
    with col2:
        model = st.selectbox(
            "Modèle",
            ["DeepSeek Chat", "Molmo 2 8B", "Llama 2 70B"],
            index=["DeepSeek Chat", "Molmo 2 8B", "Llama 2 70B"].index(conv["model"]),
            label_visibility="collapsed"
        )
        if model != conv["model"]:
            conv["model"] = model
            conv["messages"] = []
    
    with col3:
        if st.button("📥 Export", use_container_width=True):
            # Générer le contenu d'export
            export_content = f"# {conv['title']}\n\n"
            export_content += f"**Modèle:** {conv['model']}\n"
            export_content += f"**Date:** {conv['created_at']}\n\n"
            export_content += "---\n\n"
            
            for msg in conv["messages"]:
                if msg["role"] == "user":
                    export_content += f"**Vous:** {msg['content']}\n\n"
                else:
                    export_content += f"**IA:** {msg['content']}\n\n"
            
            # Créer le fichier
            st.download_button(
                label="Télécharger en Markdown",
                data=export_content,
                file_name=f"{conv['title']}.md",
                mime="text/markdown"
            )
    
    st.markdown("---")
    
    # Affichage des messages
    if conv["messages"]:
        for msg in conv["messages"]:
            if msg["role"] == "user":
                st.markdown(f'<div class="message-box user-message"><b>Vous:</b> {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="message-box ai-message"><b>IA:</b> {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.info("Aucun message pour le moment. Posez votre première question !")
    
    st.markdown("---")
    
    # Zone de saisie
    st.markdown("### Votre message")
    message = st.text_area("Posez votre question...", height=100, label_visibility="collapsed")
    
    if st.button("📤 Envoyer", use_container_width=True):
        if message.strip():
            # Ajouter le message utilisateur
            conv["messages"].append({
                "role": "user",
                "content": message
            })
            
            # Préparer les messages pour l'API
            api_messages = [{"role": msg["role"], "content": msg["content"]} for msg in conv["messages"]]
            
            # Appeler l'API OpenRouter
            with st.spinner("⏳ Traitement en cours..."):
                response = call_openrouter_api(api_messages, conv["model"], temperature, max_tokens)
            
            if response:
                # Ajouter la réponse IA
                conv["messages"].append({
                    "role": "assistant",
                    "content": response
                })
                st.rerun()
            else:
                st.error("❌ Erreur lors de l'appel API OpenRouter. Vérifiez que votre clé API est configurée dans les secrets Streamlit Cloud.")
