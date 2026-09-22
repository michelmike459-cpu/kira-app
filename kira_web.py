import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>KIRA</title><style>body{background:#0a0a0a;color:#fff;font-family:sans-serif;height:100vh;display:flex;flex-direction:column}.h{padding:15px;background:#111;border-bottom:1px solid #222;text-align:center;color:#a855f7;font-weight:bold} #c{flex:1;overflow:auto;padding:20px;display:flex;flex-direction:column;gap:10px}.m{max-width:85%;padding:12px 16px;border-radius:18px}.u{align-self:flex-end;background:#a855f7}.b{align-self:flex-start;background:#1e1e1e}.i{display:flex;padding:12px;gap:10px;background:#111} input{flex:1;padding:12px;border-radius:20px;border:1px solid #333;background:#1a1a1a;color:#fff} button{padding:10px 20px;border-radius:20px;border:0;background:#a855f7;color:#fff}</style></head><body><div class=h>⚡ KIRA - Bujumbura</div><div id=c><div class="m b">Yo Patron! KIRA est en ligne 🚀</div></div><div class=i><input id=t placeholder="Parle à Kira..." onkeydown="if(event.key==='Enter')send()"><button onclick="send()">OK</button></div><script>async function send(){let i=document.getElementById('t'),v=i.value.trim();if(!v)return;let c=document.getElementById('c');c.innerHTML+=`<div class='m u'>${v}</div>`;i.value='';c.innerHTML+=`<div class='m b' id='w'>...</div>`;let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:v})});let d=await r.json();document.getElementById('w').remove();c.innerHTML+=`<div class='m b'>${d.reply}</div>`;c.scrollTop=c.scrollHeight}</script></body></html>"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat(): 
    try:
        msg = request.json.get("message","")
        if not GROQ_API_KEY:
            return jsonify({"reply":"Ajoute GROQ_API_KEY dans Render > Environment"})
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"}
        data = {"model":"llama-3.3-70b-versatile","messages":[{"role":"system","content":"Tu es KIRA, IA de Bujumbura, cool, drôle, tu tutoies."},{"role":"user","content":msg}]}
        r = requests.post(GROQ_URL, json=data, headers=headers, timeout=30)
        ans = r.json()["choices"][0]["message"]["content"]
        return jsonify({"reply": ans})
    except Exception as e:
        return jsonify({"reply": f"Erreur: {e}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
