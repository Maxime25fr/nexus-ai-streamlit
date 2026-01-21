# Déploiement de Nexus AI Assistant sur Render.com

## 🚀 Guide de Déploiement

### Étape 1 : Créer un compte Render
1. Allez sur [render.com](https://render.com)
2. Cliquez sur "Sign up"
3. Connectez-vous avec GitHub

### Étape 2 : Déployer l'Application Streamlit
1. Allez sur le dashboard Render
2. Cliquez sur "New +" → "Web Service"
3. Sélectionnez votre repository `nexus-ai-streamlit`
4. Configurez :
   - **Name** : `nexus-ai-assistant`
   - **Environment** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
   - **Plan** : `Free` (gratuit)

5. Cliquez sur "Create Web Service"

### Étape 3 : Ajouter les Secrets
1. Dans les paramètres de l'app Render
2. Allez à "Environment"
3. Ajoutez les variables :
   - **OPENROUTER_API_KEY** : `sk-or-v1-...` (votre clé API)
   - **PROXY_URL** : `https://nexus-ai-proxy.onrender.com` (sera créé à l'étape suivante)

### Étape 4 : Déployer le Serveur Proxy (Optionnel mais Recommandé)
1. Cliquez sur "New +" → "Web Service"
2. Sélectionnez votre repository `nexus-ai-streamlit`
3. Configurez :
   - **Name** : `nexus-ai-proxy`
   - **Environment** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn proxy_server:app`
   - **Plan** : `Free`

4. Ajoutez la variable d'environnement :
   - **OPENROUTER_API_KEY** : `sk-or-v1-...`

### Étape 5 : Mettre à Jour l'URL du Proxy
1. Une fois le proxy déployé, copiez son URL (ex: `https://nexus-ai-proxy.onrender.com`)
2. Retournez à l'app Streamlit
3. Mettez à jour la variable `PROXY_URL` avec cette URL

### Étape 6 : Voilà ! 🎉
Votre application est maintenant en ligne !

**URL de l'app** : `https://nexus-ai-assistant.onrender.com`

## 📝 Notes

- Les services gratuits de Render se mettent en veille après 15 minutes d'inactivité
- Le redémarrage prend quelques secondes
- Pour des performances optimales, passez à un plan payant

## 🔧 Dépannage

**L'app ne démarre pas ?**
- Vérifiez les logs dans Render
- Assurez-vous que `requirements.txt` est correct
- Vérifiez que les variables d'environnement sont configurées

**Le proxy ne répond pas ?**
- Vérifiez que la clé API OpenRouter est correcte
- Vérifiez que l'URL du proxy est mise à jour dans l'app Streamlit
