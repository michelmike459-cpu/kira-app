from flask import Flask, request, jsonify, render_template_string
import os, requests

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

HTML = """<!DOCTYPE html><html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>KIRA</title>
<style>body{background:#000;color:#fff;font-family:sans-serif;margin:0;padding:10px}#chat{height:75vh;overflow-y:auto;border:1px solid #333;border-radius:10px;padding:10px}.msg{background:#222;margin:8px;padding:10px;border-radius:15px}.user{background:#7c3aed;margin-left:40px;text-align:right}input{width:70%;padding:12px;border-radius:20px;border:none}button{padding:12px 20px;border-radius:20px;border:none;background:#7c3aed;color:#fff}</style>
</head><body><h3>⚡ KIRA - Bujumbura</h3><div id=chat><div class=msg>Yo Patron! KIRA est en ligne 🚀 Tape un message</div></div>
<div style=display:flex;gap:5px;position:fixed;bottom:10px;width:95%><input id=i placeholder='Parle à KIRA...'><button onclick=send()>Send</button></div>
<script>async function send(){let m=document.getElementById('i').value;if(!m)return;let c=document.getElementById('chat');c.innerHTML+=`<div class=msg user>${m}</div>`;document.getElementById('i').value='';let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});let d=await r.json();c.innerHTML+=`<div class=msg>${d.reply}</div>`;c.scrollTop=c.scrollHeight}</script></body></html>"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
        data = request.json
    user_msg = data.get("message","")
    if data.get("password") != os.environ.get("KIRA_PASSWORD"):
        return jsonify({"reply": "🔒 Accès refusé Patron."}), 401
    if not GROQ_API_KEY:
        return jsonify({"reply":"❌ GROQ_API_KEY manquante dans Render > Environment"})

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {
    "model": "openai/gpt-oss-20b",
    "messages": [
            {"role": "system", "content": "Tu es KIRA, IA cool de Bujumbura. Tu tutoies ton Patron, tu es rapide et drôle."},
            {"role": "user", "content": user_msg}
        ]
    }
    try:
        r = requests.post(GROQ_URL, json=data, headers=headers, timeout=30)
        j = r.json()
        print("GROQ REPLY:", j) # visible dans Render Logs
        if "error" in j:
            return jsonify({"reply": f"❌ Erreur GROQ: {j['error']['message']}"})
        return jsonify({"reply": j["choices"][0]["message"]["content"]})
    except Exception as e:
        return jsonify({"reply": f"❌ Erreur serveur: {e}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
