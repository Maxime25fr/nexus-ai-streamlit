# 🌌 Nexus AI Assistant v2.0 - Streamlit Edition

Une application IA multimodal complète avec support de multiples modèles, analyse d'images, historique persistant et export de conversations.

## ✨ Fonctionnalités

- ✅ **Chat Multimodal** : Support de Molmo 2 8B (vision), DeepSeek (texte) et Llama 2 70B
- ✅ **Analyse d'Images** : Upload et analyse d'images avec Molmo 2 8B
- ✅ **Historique Persistant** : Sauvegarde locale des conversations en JSON
- ✅ **Export Flexible** : Téléchargement en TXT ou Markdown
- ✅ **Paramètres Avancés** : Contrôle de température et longueur de réponse
- ✅ **Design Premium** : Interface néon cyan/bleu avec effets de lueur
- ✅ **100% Gratuit** : Modèles OpenRouter sans coûts
- ✅ **Statistiques** : Suivi des messages et caractères
- ✅ **Guide Intégré** : Documentation complète dans l'app

## 🚀 Installation Locale

### Prérequis
- Python 3.8+
- pip

### Étapes

1. **Clonez le repository**
```bash
git clone https://github.com/yourusername/nexus-ai-streamlit.git
cd nexus-ai-streamlit
```

2. **Installez les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configurez votre clé API**
   - Créez un compte sur [OpenRouter.ai](https://openrouter.ai/)
   - Générez une clé API
   - Modifiez `.streamlit/secrets.toml` avec votre clé

4. **Lancez l'application**
```bash
streamlit run app.py
```

L'app s'ouvrira sur `http://localhost:8501`

## 🌐 Déploiement sur Streamlit Cloud

### Étapes de Publication

1. **Préparez votre repository GitHub**
   ```bash
   git add .
   git commit -m "Initial commit: Nexus AI Assistant"
   git push origin main
   ```

2. **Accédez à Streamlit Cloud**
   - Allez sur [share.streamlit.io](https://share.streamlit.io/)
   - Connectez-vous avec votre compte GitHub
   - Cliquez sur "New app"

3. **Configurez le déploiement**
   - **Repository** : Sélectionnez votre repo
   - **Branch** : `main`
   - **Main file path** : `app.py`

4. **Ajoutez les secrets**
   - Dans les paramètres de l'app, allez à "Secrets"
   - Ajoutez votre clé API :
   ```
   OPENROUTER_API_KEY = "sk-or-v1-YOUR_API_KEY"
   ```

5. **Déployez**
   - Cliquez sur "Deploy"
   - Attendez quelques secondes
   - Votre app est en ligne !

## 📊 Modèles Disponibles

| Modèle | Type | Cas d'Usage |
| :--- | :--- | :--- |
| **Molmo 2 8B** | Vision + Texte | Analyse d'images, descriptions visuelles |
| **DeepSeek Chat** | Texte | Raisonnement complexe, génération de code |
| **Llama 2 70B** | Texte | Conversations naturelles, créativité |

Tous les modèles sont **gratuits** via OpenRouter.

## 💾 Sauvegarde des Conversations

Les conversations sont automatiquement sauvegardées dans `conversations.json` :
- Format JSON structuré
- Métadonnées (titre, modèle, date)
- Historique complet des messages

## 🎨 Personnalisation

### Modifier les Couleurs
Éditez `.streamlit/config.toml` :
```toml
[theme]
primaryColor = "#00d4ff"  # Couleur principale
backgroundColor = "#0e1117"  # Fond
```

### Ajouter de Nouveaux Modèles
Dans `app.py`, ajoutez à `MODELS_CONFIG` :
```python
"Nouveau Modèle": {
    "id": "provider/model-id",
    "desc": "Description du modèle",
    "vision": False
}
```

## 🔐 Sécurité

- ✅ Clé API stockée de manière sécurisée dans les secrets Streamlit
- ✅ Aucune donnée sensible dans le code
- ✅ Conversations stockées localement
- ✅ HTTPS automatique sur Streamlit Cloud

## 📝 Structure du Projet

```
nexus-ai-streamlit/
├── app.py                    # Application principale
├── requirements.txt          # Dépendances Python
├── README.md                 # Ce fichier
├── .streamlit/
│   ├── config.toml          # Configuration Streamlit
│   └── secrets.toml         # Secrets locaux (à ignorer)
└── conversations.json       # Historique des conversations (généré)
```

## 🐛 Dépannage

### "OPENROUTER_API_KEY is not set"
- Vérifiez que votre clé est dans `.streamlit/secrets.toml` (local)
- Ou dans les secrets Streamlit Cloud (production)
- Redémarrez l'app

### Les images ne s'affichent pas
- Vérifiez que vous utilisez Molmo 2 8B
- Formats supportés : PNG, JPG, JPEG
- Taille max : ~5MB

### Erreur de connexion API
- Vérifiez votre connexion Internet
- Vérifiez que votre clé API est valide
- Consultez le quota OpenRouter

## 📚 Ressources

- [Documentation Streamlit](https://docs.streamlit.io/)
- [API OpenRouter](https://openrouter.ai/docs)
- [Modèles Disponibles](https://openrouter.ai/docs/models)

## 📄 Licence

Ce projet est fourni à titre d'exemple. Tous droits réservés.

## 🤝 Support

Pour toute question, veuillez ouvrir une issue sur GitHub.

---

**Version** : 2.0  
**Dernière mise à jour** : 21 Janvier 2026  
**Auteur** : Manus AI Agent  
**Status** : ✅ Prêt pour la production
