"""
Serveur proxy Flask pour contourner les restrictions de Streamlit Cloud
"""
from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Récupérer la clé API OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint proxy pour appeler OpenRouter API"""
    try:
        data = request.json
        
        if not OPENROUTER_API_KEY:
            return jsonify({"error": "API key not configured"}), 500
        
        # Préparer les headers
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://nexus-ai-streamlit.streamlit.app/",
            "X-Title": "Nexus AI Assistant",
            "Content-Type": "application/json"
        }
        
        # Préparer le payload
        payload = {
            "model": data.get("model", "deepseek/deepseek-chat"),
            "messages": data.get("messages", []),
            "temperature": data.get("temperature", 0.7),
            "max_tokens": data.get("max_tokens", 2000),
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
        # Faire la requête à OpenRouter
        response = requests.post(
            "https://openrouter.io/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return jsonify({
                    "success": True,
                    "content": data["choices"][0]["message"]["content"]
                })
            else:
                return jsonify({"error": "Invalid API response"}), 500
        else:
            return jsonify({
                "error": f"API Error ({response.status_code}): {response.text}"
            }), response.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timeout"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Connection error"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
