import streamlit as st
from openai import OpenAI
from PIL import Image
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
    
    /* Bulles de chat */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px !important;
        padding: 20px !important;
        margin-bottom: 15px !important;
        transition: transform 0.2s ease;
    }
    
    .stChatMessage:hover {
        transform: translateY(-2px);
        border-color: rgba(0, 212, 255, 0.2) !important;
    }
    
    /* Boutons */
    .stButton>button {
        background: linear-gradient(135deg, #00d4ff 0%, #0080ff 100%);
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.2);
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(0, 212, 255, 0.4);
    }
    
    /* Descriptions */
    .model-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 15px;
        border-left: 4px solid #00d4ff;
        margin: 10px 0;
    }
    
    .model-desc {
        font-size: 0.85rem;
        color: #a0a0a0;
        line-height: 1.4;
    }
    
    /* Masquer les éléments inutiles */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Tabs personnalisées */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        color: #a0a0a0;
        border: 1px solid rgba(0, 212, 255, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 212, 255, 0.2);
        border-color: #00d4ff;
        color: #00d4ff;
    }
    </style>
    """, unsafe_allow_html=True)

# Configuration des modèles
MODELS_CONFIG = {
    "Molmo 2 8B": {
        "id": "allenai/molmo-2-8b:free",
        "desc": "L'expert en vision. Capable d'analyser, décrire et comprendre vos images avec une précision chirurgicale.",
        "vision": True
    },
    "GPT-OSS-120B": {
        "id": "deepseek/deepseek-chat",
        "desc": "Le titan du texte. Un modèle massif de 120B+ paramètres, exceptionnel pour la génération de contenu complexe, le code et le raisonnement profond.",
        "vision": False
    },
    "Llama 2 70B": {
        "id": "meta-llama/llama-2-70b-chat",
        "desc": "Modèle open-source puissant. Excellent pour les conversations naturelles et le raisonnement.",
        "vision": False
    }
}

def encode_image(image):
    """Encode une image en base64"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def load_conversations():
    """Charge les conversations depuis le fichier JSON"""
    if os.path.exists("conversations.json"):
        try:
            with open("conversations.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_conversations(conversations):
    """Sauvegarde les conversations dans un fichier JSON"""
    with open("conversations.json", "w", encoding="utf-8") as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)

def generate_conversation_title(message):
    """Génère un titre basé sur le premier message"""
    # Prendre les 50 premiers caractères
    title = message[:50].strip()
    if len(message) > 50:
        title += "..."
    return title or "Conversation"

def export_conversation(messages, format_type="txt"):
    """Exporte la conversation dans le format spécifié"""
    if format_type == "markdown":
        content = f"# Conversation Nexus AI\n\n"
        content += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"**Modèle:** {st.session_state.current_model}\n\n"
        content += "---\n\n"
        
        for msg in messages:
            if msg["role"] == "user":
                content += f"## Vous\n\n{msg['content']}\n\n"
            else:
                content += f"## Assistant\n\n{msg['content']}\n\n"
    else:
        content = "CONVERSATION NEXUS AI\n"
        content += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"Modèle: {st.session_state.current_model}\n"
        content += "=" * 50 + "\n\n"
        
        for msg in messages:
            role = "VOUS" if msg["role"] == "user" else "ASSISTANT"
            content += f"[{role}]\n{msg['content']}\n\n"
    
    return content

# Initialisation de l'état de session
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_model" not in st.session_state:
    st.session_state.current_model = "Molmo 2 8B"
if "conversations" not in st.session_state:
    st.session_state.conversations = load_conversations()
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None
if "show_settings" not in st.session_state:
    st.session_state.show_settings = False

# Barre latérale
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #00d4ff;'>🌌 Nexus Control</h2>", unsafe_allow_html=True)
    st.divider()
    
    # Onglets dans la sidebar
    sidebar_tab1, sidebar_tab2, sidebar_tab3 = st.tabs(["💬 Chat", "📚 Historique", "⚙️ Paramètres"])
    
    with sidebar_tab1:
        st.markdown("### Sélection du Modèle")
        new_model = st.selectbox(
            "Intelligence Artificielle",
            options=list(MODELS_CONFIG.keys()),
            index=list(MODELS_CONFIG.keys()).index(st.session_state.current_model),
            key="model_select"
        )
        
        if new_model != st.session_state.current_model:
            st.session_state.current_model = new_model
            st.session_state.messages = []
            st.rerun()
        
        model_info = MODELS_CONFIG[st.session_state.current_model]
        st.markdown(f"""
            <div class='model-card'>
                <div style='font-weight: 600; color: #ffffff; margin-bottom: 5px;'>{st.session_state.current_model}</div>
                <div class='model-desc'>{model_info['desc']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Upload d'image pour Molmo
        if model_info["vision"]:
            st.markdown("### 📸 Vision")
            uploaded_file = st.file_uploader("Analyser une image", type=["jpg", "jpeg", "png"], key="image_uploader")
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Image chargée", use_container_width=True)
                st.session_state.uploaded_image = image
            else:
                st.session_state.uploaded_image = None
        else:
            st.info("💡 Ce modèle est un expert textuel pur. Utilisez Molmo 2 8B pour l'analyse d'images.")
            st.session_state.uploaded_image = None
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Réinitialiser", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        with col2:
            if st.button("💾 Sauvegarder", use_container_width=True):
                if st.session_state.messages:
                    conv_id = st.session_state.current_conversation_id or str(len(st.session_state.conversations))
                    title = st.session_state.conversations.get(conv_id, {}).get("title") or generate_conversation_title(st.session_state.messages[0]["content"])
                    st.session_state.conversations[conv_id] = {
                        "title": title,
                        "model": st.session_state.current_model,
                        "messages": st.session_state.messages,
                        "created_at": datetime.now().isoformat()
                    }
                    save_conversations(st.session_state.conversations)
                    st.session_state.current_conversation_id = conv_id
                    st.success("✅ Conversation sauvegardée!")
    
    with sidebar_tab2:
        st.markdown("### 📚 Historique des Conversations")
        
        if st.session_state.conversations:
            for conv_id, conv_data in sorted(st.session_state.conversations.items(), key=lambda x: x[1].get("created_at", ""), reverse=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    if st.button(f"📝 {conv_data['title']}", use_container_width=True, key=f"load_{conv_id}"):
                        st.session_state.messages = conv_data["messages"]
                        st.session_state.current_model = conv_data.get("model", "Molmo 2 8B")
                        st.session_state.current_conversation_id = conv_id
                        st.rerun()
                
                with col2:
                    if st.button("📥", key=f"export_{conv_id}", help="Exporter"):
                        content = export_conversation(conv_data["messages"], "txt")
                        st.download_button(
                            label="TXT",
                            data=content,
                            file_name=f"{conv_data['title']}.txt",
                            mime="text/plain",
                            key=f"download_txt_{conv_id}"
                        )
                
                with col3:
                    if st.button("🗑️", key=f"delete_{conv_id}", help="Supprimer"):
                        del st.session_state.conversations[conv_id]
                        save_conversations(st.session_state.conversations)
                        st.rerun()
        else:
            st.info("Aucune conversation sauvegardée")
    
    with sidebar_tab3:
        st.markdown("### ⚙️ Paramètres")
        
        # Paramètres de température
        temperature = st.slider(
            "Température (Créativité)",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="Plus élevé = plus créatif, plus bas = plus déterministe"
        )
        st.session_state.temperature = temperature
        
        # Paramètres de max tokens
        max_tokens = st.slider(
            "Longueur max de réponse",
            min_value=100,
            max_value=4000,
            value=2000,
            step=100
        )
        st.session_state.max_tokens = max_tokens
        
        st.divider()
        st.markdown("### À Propos")
        st.info("""
        **Nexus AI Assistant v2.0**
        
        Application IA multimodal avec:
        - Support de multiples modèles
        - Analyse d'images (Molmo)
        - Historique persistant
        - Export de conversations
        
        Modèles gratuits via OpenRouter
        """)

# Récupération de la clé API
api_key = st.secrets.get("OPENROUTER_API_KEY")

if not api_key:
    st.error("⚠️ Configuration manquante : OPENROUTER_API_KEY")
    st.info("Veuillez configurer votre clé API OpenRouter dans les secrets Streamlit")
    st.stop()

# Initialisation du client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

# Interface principale
st.markdown("<h1 class='main-title'>🌌 Nexus AI Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e; margin-bottom: 2rem;'>L'intelligence artificielle, redéfinie.</p>", unsafe_allow_html=True)

# Onglets principaux
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Statistiques", "📖 Guide"])

with tab1:
    # Affichage des messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Zone de saisie
    if prompt := st.chat_input("Transmettez votre commande..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Préparation du contenu (Multimodal ou Texte seul)
            model_info = MODELS_CONFIG[st.session_state.current_model]
            
            if model_info["vision"] and hasattr(st.session_state, 'uploaded_image') and st.session_state.uploaded_image:
                content = [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{encode_image(st.session_state.uploaded_image)}"}
                    }
                ]
            else:
                content = prompt

            try:
                response = client.chat.completions.create(
                    model=model_info["id"],
                    messages=[{"role": "user", "content": content}],
                    stream=True,
                    temperature=st.session_state.get("temperature", 0.7),
                    max_tokens=st.session_state.get("max_tokens", 2000)
                )
                
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"❌ Nexus a rencontré une anomalie : {e}")

with tab2:
    st.markdown("### 📊 Statistiques de la Conversation")
    
    if st.session_state.messages:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Messages", len(st.session_state.messages))
        
        with col2:
            user_messages = sum(1 for m in st.session_state.messages if m["role"] == "user")
            st.metric("Vos messages", user_messages)
        
        with col3:
            assistant_messages = sum(1 for m in st.session_state.messages if m["role"] == "assistant")
            st.metric("Réponses IA", assistant_messages)
        
        with col4:
            total_chars = sum(len(m["content"]) for m in st.session_state.messages)
            st.metric("Caractères", total_chars)
        
        st.divider()
        
        # Export
        st.markdown("### 💾 Exporter la Conversation")
        col1, col2 = st.columns(2)
        
        with col1:
            txt_content = export_conversation(st.session_state.messages, "txt")
            st.download_button(
                label="📥 Télécharger en TXT",
                data=txt_content,
                file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            md_content = export_conversation(st.session_state.messages, "markdown")
            st.download_button(
                label="📥 Télécharger en Markdown",
                data=md_content,
                file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
    else:
        st.info("Aucune conversation en cours")

with tab3:
    st.markdown("""
    ### 📖 Guide d'Utilisation
    
    #### 🚀 Démarrage Rapide
    1. Sélectionnez un modèle IA dans la barre latérale
    2. Tapez votre message dans la zone de chat
    3. Appuyez sur Entrée pour envoyer
    
    #### 🎯 Modèles Disponibles
    - **Molmo 2 8B** : Expert en vision et analyse d'images
    - **GPT-OSS-120B** : Titan du texte pour raisonnement complexe
    - **Llama 2 70B** : Conversations naturelles et raisonnement
    
    #### 📸 Analyse d'Images
    - Disponible uniquement avec Molmo 2 8B
    - Formats supportés : JPG, JPEG, PNG
    - L'image sera analysée avec votre message
    
    #### 💾 Sauvegarde des Conversations
    - Cliquez sur "Sauvegarder" pour stocker la conversation
    - Accédez à l'historique dans l'onglet "Historique"
    - Exportez en TXT ou Markdown
    
    #### ⚙️ Paramètres
    - **Température** : Contrôle la créativité (0 = déterministe, 2 = très créatif)
    - **Longueur max** : Limite la taille des réponses
    
    #### 🔐 Sécurité
    - Toutes les conversations sont sauvegardées localement
    - Aucune donnée n'est envoyée à des serveurs externes sauf OpenRouter
    - Modèles gratuits via OpenRouter
    
    #### 💡 Conseils
    - Soyez spécifique dans vos questions
    - Utilisez des images claires pour l'analyse
    - Sauvegardez régulièrement vos conversations
    """)

st.markdown("---")
st.caption("🌌 Nexus AI Framework v2.0 | Sécurisé & Optimisé | Modèles Gratuits OpenRouter")
