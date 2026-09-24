import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Config & Variables d'environnement
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KIRA - Patron Michael</title>
    <style>
        * { box-sizing: border-box; }
        body { background: #050a14; color: #fff; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; }
        header { padding: 15px; background: linear-gradient(90deg, #00f5ff, #0066ff); color: #000; font-weight: bold; font-size: 18px; text-align: center; display: flex; justify-content: space-between; align-items: center; }
        #clearBtn { background: #000; color: #00f5ff; border: 1px solid #00f5ff; padding: 6px 12px; border-radius: 12px; font-size: 12px; cursor: pointer; }
        #chat { flex: 1; overflow-y: auto; padding: 15px; padding-bottom: 90px; }
        .msg { margin: 10px 0; padding: 12px 15px; border-radius: 15px; max-width: 85%; line-height: 1.4; word-wrap: break-word; }
        .you { background: #1a2333; margin-left: auto; border-bottom-right-radius: 2px; }
        .kira { background: linear-gradient(135deg, rgba(0,245,255,0.1), rgba(0,102,255,0.1)); border: 1px solid rgba(0,245,255,0.2); }
        #bar { position: fixed; bottom: 0; left: 0; right: 0; background: #0a1426; padding: 10px; display: flex; gap: 8px; align-items: center; border-top: 1px solid rgba(0,245,255,0.2); }
        input { flex: 1; padding: 14px; border-radius: 25px; border: none; background: #1a2333; color: #fff; outline: none; }
        button { padding: 12px 18px; border-radius: 25px; border: none; font-weight: bold; cursor: pointer; }
        #sendBtn { background: #00f5ff; color: #000; }
        #micBtn { background: #1a2333; color: #00f5ff; font-size: 18px; transition: all 0.3s ease; }
        #micBtn.recording { background: #ff0055; color: #fff; animation: pulse 1s infinite; }
        .speakBtn { background: #1a2333; color: #00f5ff; font-size: 12px; margin-top: 8px; border: 1px solid rgba(0,245,255,0.3); padding: 6px 12px; border-radius: 15px; cursor: pointer; display: inline-block; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    </style>
</head>
<body>
    <header>
        <span>⚡ KIRA - Intelligence de Patron Michael - Bujumbura</span>
        <button id="clearBtn" onclick="clearChat()">Réinitialiser</button>
    </header>
    
    <div id="chat"></div>
    
    <div id="bar">
        <button id="micBtn" onclick="startVoice()" title="Parler">🎤</button>
        <input id="msg" placeholder="Parle à KIRA..." autocomplete="off">
        <button id="sendBtn" onclick="send()">Envoyer</button>
    </div>

<script>
let synth = window.speechSynthesis;
let conversationHistory = [];

function speak(text) {
    if (synth.speaking) synth.cancel();
    let u = new SpeechSynthesisUtterance(text);
    u.lang = 'fr-FR';
    u.rate = 1;
    synth.speak(u);
}

function startVoice() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert("La reconnaissance vocale n'est pas supportée par votre navigateur.");
        return;
    }
    let rec = new SpeechRecognition();
    rec.lang = 'fr-FR';
    
    let micBtn = document.getElementById('micBtn');
    micBtn.classList.add('recording');

    rec.start();

    rec.onresult = e => { 
        document.getElementById('msg').value = e.results[0][0].transcript; 
        micBtn.classList.remove('recording');
        send(); 
    };

    rec.onerror = () => { micBtn.classList.remove('recording'); };
    rec.onend = () => { micBtn.classList.remove('recording'); };
}

function clearChat() {
    conversationHistory = [];
    document.getElementById('chat').innerHTML = '';
}

async function send() {
    let input = document.getElementById('msg');
    let m = input.value.trim();
    if (!m) return;

    let chat = document.getElementById('chat');
    
    let userDiv = document.createElement('div');
    userDiv.className = 'msg you';
    userDiv.textContent = `Toi: ${m}`;
    chat.appendChild(userDiv);
    
    input.value = '';

    let typingDiv = document.createElement('div');
    typingDiv.className = 'msg kira';
    typingDiv.id = 'typing';
    typingDiv.textContent = 'KIRA réfléchit...';
    chat.appendChild(typingDiv);
    chat.scrollTop = chat.scrollHeight;

    conversationHistory.push({"role": "user", "content": m});

    try {
        let r = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ history: conversationHistory })
        });
        
        let j = await r.json();
        let typ = document.getElementById('typing');
        if (typ) typ.remove();

        let kiraDiv = document.createElement('div');
        kiraDiv.className = 'msg kira';

        if (!r.ok) {
            kiraDiv.textContent = `❌ Erreur: ${j.reply || 'Problème serveur'}`;
            conversationHistory.pop();
        } else {
            let replyText = j.reply;
            kiraDiv.textContent = `KIRA: ${replyText}`;
            
            conversationHistory.push({"role": "assistant", "content": replyText});
            
            let speakBtn = document.createElement('button');
            speakBtn.className = 'speakBtn';
            speakBtn.textContent = '🔊 Écouter';
            speakBtn.onclick = () => speak(replyText);
            kiraDiv.appendChild(document.createElement('br'));
            kiraDiv.appendChild(speakBtn);

            speak(replyText);
        }
        
        chat.appendChild(kiraDiv);
        chat.scrollTop = chat.scrollHeight;
    } catch(e) {
        let typ = document.getElementById('typing');
        if (typ) typ.remove();
        let errDiv = document.createElement('div');
        errDiv.className = 'msg kira';
        errDiv.textContent = `❌ Erreur connexion: ${e.message}`;
        chat.appendChild(errDiv);
        conversationHistory.pop();
    }
}

document.getElementById('msg').addEventListener('keypress', e => {
    if (e.key === 'Enter') send();
});
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    history = data.get("history", [])

    if not history:
        return jsonify({"reply": "Aucun message reçu."}), 400

    if not GROQ_API_KEY:
        return jsonify({"reply": "Clé GROQ_API_KEY non configurée sur le serveur."}), 500

    system_prompt = {
        "role": "system",
        "content": (
            "Tu es KIRA, l'assistante virtuelle intelligente et exclusive de Patron Michael à Bujumbura. "
            "Tu es loyale, directe, polie mais décontractée, avec une très légère touche d'argot burundais (ex: 'Aho', 'Ça va patron'). "
            "Tu t'adresses toujours à l'utilisateur en l'appelant 'Patron' ou 'Patron Michael'."
        )
    }

    full_messages = [system_prompt] + history

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": full_messages,
        "temperature": 0.7,
        "max_tokens": 1024
    }

    try:
        r = requests.post(GROQ_URL, json=payload, headers=headers, timeout=20)
        j = r.json()

        if r.status_code != 200 or "error" in j:
            err_msg = j.get("error", {}).get("message", "Erreur inconnue Groq")
            return jsonify({"reply": f"Erreur GROQ: {err_msg}"}), 500

        bot_reply = j["choices"][0]["message"]["content"]
        return jsonify({"reply": bot_reply})

    except requests.exceptions.Timeout:
        return jsonify({"reply": "Délai d'attente dépassé (Timeout)."}), 504
    except Exception as e:
        return jsonify({"reply": f"Erreur serveur: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
