import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

HTML = """<!DOCTYPE html><html><head><meta name=viewport content="width=device-width,initial-scale=1">
<style>body{background:#000;color:#fff;font-family:Arial;margin:0;padding:10px} #chat{margin-bottom:70px} #chat div{margin:8px 0;padding:8px;border-radius:8px;background:#111} h3{color:#0ff}</style>
</head><body><h3>⚡ KIRA - Bujumbura</h3><div id=chat></div>
<div style="display:flex;gap:5px;position:fixed;bottom:10px;left:10px;right:10px">
<input id="msg" style="flex:1;padding:12px;border-radius:20px;border:none" placeholder="Parle à KIRA...">
<button onclick="send()" style="padding:12px 20px;border-radius:20px;border:none;background:#0ff;font-weight:bold">Send</button>
</div>
<script>
async function send(){
 let m=document.getElementById('msg').value;
 if(!m) return;
 let chat=document.getElementById('chat');
 chat.innerHTML+=`<div><b>Toi:</b> ${m}</div>`;
 document.getElementById('msg').value='';
 try{
  let r=await fetch('/chat',{
   method:'POST',
   headers:{'Content-Type':'application/json'},
   body:JSON.stringify({message:m,password:'25101218Mikemichel'})
  });
  let j=await r.json();
  chat.innerHTML+=`<div><b>KIRA:</b> ${j.reply}</div>`;
  window.scrollTo(0,document.body.scrollHeight);
 }catch(e){
  chat.innerHTML+=`<div>❌ Erreur: ${e}</div>`;
 }
}
document.getElementById('msg').addEventListener('keypress',function(e){if(e.key==='Enter')send()});
</script></body></html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_msg = data.get("message", "")
    if data.get("password")!= os.environ.get("KIRA_PASSWORD"):
        return jsonify({"reply": "🔒 Accès refusé Patron. Mauvais mot de passe."}), 401
    if not GROQ_API_KEY:
        return jsonify({"reply": "❌ GROQ_API_KEY manquante sur Render"}), 500

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {"role": "system", "content": "Tu es KIRA, l'assistant de Patron à Bujumbura. Tu es loyal, direct, tu parles en français avec un peu d'argot burundais."},
            {"role": "user", "content": user_msg}
        ]
    }
    try:
        r = requests.post(GROQ_URL, json=payload, headers=headers, timeout=30)
        j = r.json()
        print("GROQ REPLY:", j)
        if "error" in j:
            return jsonify({"reply": f"❌ Erreur GROQ: {j['error']}"})
        return jsonify({"reply": j["choices"][0]["message"]["content"]})
    except Exception as e:
        return jsonify({"reply": f"❌ Erreur serveur: {e}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
