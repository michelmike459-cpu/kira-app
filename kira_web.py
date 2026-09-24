import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

HTML = """<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>KIRA - Patron Michael</title>
<style>
body{background:#050a14;color:#fff;font-family:'Segoe UI',Arial;margin:0;display:flex;flex-direction:column;height:100vh}
header{padding:15px;background:linear-gradient(90deg,#00f5ff,#0066ff);color:#000;font-weight:bold;font-size:18px;text-align:center}
#chat{flex:1;overflow-y:auto;padding:15px;padding-bottom:90px}
.msg{margin:10px 0;padding:12px 15px;border-radius:15px;max-width:85%;line-height:1.4}
.you{background:#1a2333;margin-left:auto;border-bottom-right-radius:2px}
.kira{background:linear-gradient(135deg,#00f5ff22,#0066ff22);border:1px solid #00f5ff44}
#bar{position:fixed;bottom:0;left:0;right:0;background:#0a1426;padding:10px;display:flex;gap:8px;align-items:center;border-top:1px solid #00f5ff33}
input{flex:1;padding:14px;border-radius:25px;border:none;background:#1a2333;color:#fff;outline:none}
button{padding:12px 18px;border-radius:25px;border:none;font-weight:bold;cursor:pointer}
#sendBtn{background:#00f5ff;color:#000}
#micBtn{background:#1a2333;color:#00f5ff;font-size:18px}
#speakBtn{background:#1a2333;color:#00f5ff;font-size:14px;margin-top:5px}
</style>
</head><body>
<header>⚡ KIRA - Intelligence de Patron Michael - Bujumbura</header>
<div id="chat"></div>
<div id="bar">
<button id="micBtn" onclick="startVoice()">🎤</button>
<input id="msg" placeholder="Parle à KIRA...">
<button id="sendBtn" onclick="send()">Envoyer</button>
</div>
<script>
let synth = window.speechSynthesis;
function speak(text){
  let u = new SpeechSynthesisUtterance(text);
  u.lang='fr-FR'; u.rate=1; u.pitch=1;
  synth.speak(u);
}
function startVoice(){
  let rec = new (window.SpeechRecognition||window.webkitSpeechRecognition)();
  rec.lang='fr-FR'; rec.start();
  rec.onresult = e => { document.getElementById('msg').value = e.results[0][0].transcript; send(); }
}

async function send(){
 let m=document.getElementById('msg').value.trim();
 if(!m) return;
 let chat=document.getElementById('chat');
 chat.innerHTML+=`<div class="msg you"><b>Toi:</b> ${m}</div>`;
 document.getElementById('msg').value='';
 chat.innerHTML+=`<div class="msg kira" id="typing">KIRA écrit...</div>`;
 chat.scrollTop=chat.scrollHeight;
 try{
  let r=await fetch('/chat',{
   method:'POST',
   headers:{'Content-Type':'application/json'},
   body:JSON.stringify({message:m,password:'25101218mikemichel'})
  });
  let j=await r.json();
  document.getElementById('typing').remove();
  let reply=j.reply;
  chat.innerHTML+=`<div class="msg kira"><b>KIRA:</b> ${reply}<br><button id="speakBtn" onclick="speak(\`${reply.replace(/`/g,'').replace(/'/g,'')}\`)">🔊 Écouter</button></div>`;
  speak(reply);
  chat.scrollTop=chat.scrollHeight;
 }catch(e){
  document.getElementById('typing').remove();
  chat.innerHTML+=`<div class="msg kira">❌ Erreur: ${e}</div>`;
 }
}
document.getElementById('msg').addEventListener('keypress',e=>{if(e.key==='Enter')send()});
</script></body></html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    data=request.json
    user_msg=data.get("message","")
    prefix="Salut Patron Michael! Je t'ai reconnu, tu es mon Patron supreme. " if "michael" in user_msg.lower() or "mc" in user_msg.lower() else ""

    if data.get("password")!=os.environ.get("KIRA_PASSWORD"):
        return jsonify({"reply":"🔒 Mauvais mot de passe Patron"}),401
    if not GROQ_API_KEY:
        return jsonify({"reply":"❌ GROQ_API_KEY manquante"}),500

    headers={"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"}
    payload={
        "model":"openai/gpt-oss-20b",
        "messages":[
            {"role":"system","content":"Tu es KIRA, assistante de Patron Michael à Bujumbura. Loyal, direct, francais avec argot burundais léger. Tu appelles toujours Patron Michael."},
            {"role":"user","content":user_msg}
        ]
    }
    try:
        r=requests.post(GROQ_URL,json=payload,headers=headers,timeout=30)
        j=r.json()
        if "error" in j:
            return jsonify({"reply":f"❌ GROQ: {j['error']}"})
        return jsonify({"reply":prefix+j["choices"][0]["message"]["content"]})
    except Exception as e:
        return jsonify({"reply":f"❌ Erreur: {e}"})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
