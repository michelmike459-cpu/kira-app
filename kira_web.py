from flask import Flask, request, jsonify, render_template_string
import os
from groq import Groq

app = Flask(__name__)
KIRA_PASSWORD = os.environ.get("KIRA_PASSWORD", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY)

PATRON_ALIASES = ["michael", "mc.michael", "mc michael", "mcmichael"]

SYSTEM_BASE = "Tu es KIRA de Bujumbura. Poli, loyal, chaleureux. Michael/Mc.Michael est ton PATRON SUPREME. Si le nom est Michael, dis Oui Patron Michael et souviens-toi. Si c'est un autre nom, c'est un invite mais le vrai Patron reste Michael. Pas de vulgarite. Reponds court et utile."

HTML_PAGE = """
<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>KIRA</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
*{font-family:Inter,sans-serif;box-sizing:border-box}
body{margin:0;height:100vh;background:radial-gradient(circle at 20% 20%, #1a1a2e, #000);color:#fff;display:flex;flex-direction:column}
header{padding:16px;text-align:center;border-bottom:1px solid #222;background:rgba(0,0,0,0.6)}
#chat{flex:1;overflow-y:auto;padding:18px;display:flex;flex-direction:column;gap:10px}
.msg{padding:12px 16px;border-radius:18px;max-width:82%;line-height:1.4}
.toi{background:#fff;color:#000;align-self:flex-end}
.kira{background:#1e1e2f;border:1px solid #2a2a4a;align-self:flex-start}
#bar{display:flex;gap:8px;padding:10px;background:#000;border-top:1px solid #222}
input{flex:1;padding:13px 16px;border-radius:24px;border:1px solid #333;background:#111;color:#fff;outline:none}
button{border:none;border-radius:24px;padding:12px 16px;font-weight:600;cursor:pointer}
#send{background:#fff;color:#000}#audioBtn{background:#222;color:#fff;border:1px solid #333}
</style></head><body>
<header><h1>KIRA</h1><p id="st">Assistant du Patron Michael</p></header>
<div id="chat"></div>
<div id="bar">
<input id="txt" placeholder="Ecris..." onkeydown="if(event.key==='Enter')send()">
<button id="audioBtn" onclick="toggleAudio()">🔊 ON</button>
<button id="send" onclick="send()">Envoyer</button>
</div>
<script>
let audioOn = localStorage.getItem('kira_audio')!=='off';
let userName = localStorage.getItem('kira_name')||'';
let isPatron = localStorage.getItem('kira_is_patron')==='true';
let history = JSON.parse(localStorage.getItem('kira_history')||'[]');
const PATRONS = ["michael","mc.michael","mc michael","mcmichael"];
function isPatronName(n){return PATRONS.some(k=>n.toLowerCase().includes(k));}
function save(){localStorage.setItem('kira_history',JSON.stringify(history));}
function render(){
 const c=document.getElementById('chat');c.innerHTML='';
 if(history.length===0){
   const g="Bonjour, je suis Kira, et toi? Comment tu t'appelles?";
   history.push({role:'kira',who:'KIRA',text:g});save();
 }
 history.forEach(m=>{c.innerHTML+=`<div class='msg ${m.role}'><b>${m.who}:</b> ${m.text}</div>`;});
 c.scrollTop=c.scrollHeight;
}
function toggleAudio(){
 audioOn=!audioOn;localStorage.setItem('kira_audio',audioOn?'on':'off');
 document.getElementById('audioBtn').innerText=audioOn?'🔊 ON':'🔇 OFF';
 if(!audioOn) speechSynthesis.cancel();
}
function speak(t){
 if(!audioOn) return; speechSynthesis.cancel();
 const u=new SpeechSynthesisUtterance(t.slice(0,350));u.lang='fr-FR';speechSynthesis.speak(u);
}
document.getElementById('audioBtn').innerText=audioOn?'🔊 ON':'🔇 OFF';
async function send(){
 let msg=document.getElementById('txt').value.trim();if(!msg) return;
 document.getElementById('txt').value='';
 if(!userName){
   userName=msg;if(isPatronName(userName)){isPatron=true;userName="Michael";}
   localStorage.setItem('kira_name',userName);localStorage.setItem('kira_is_patron',''+isPatron);
   history.push({role:'toi',who:'Toi',text:msg});
   let w=isPatron?`Salut Patron Michael! C'est bien toi Mc.Michael! Je t'ai reconnu, tu es mon Patron supreme. Je m'en souviendrai toujours.`:`Enchante ${userName}! Moi c'est Kira. Je retiens ton prenom. Mon Patron c'est Michael.`;
   history.push({role:'kira',who:'KIRA',text:w});save();render();speak(w);return;
 }
 if(isPatronName(msg)&&!isPatron){isPatron=true;userName="Michael";localStorage.setItem('kira_name',userName);localStorage.setItem('kira_is_patron','true');}
 history.push({role:'toi',who:'Toi',text:msg});save();render();
 const c=document.getElementById('chat');c.innerHTML+=`<div class='msg kira' id='typing'><b>KIRA:</b> <i>ecrit...</i></div>`;c.scrollTop=c.scrollHeight;
 try{
  const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg,name:userName,isPatron:isPatron,history:history.slice(-8),password:"__PWD__"})});
  const d=await r.json();document.getElementById('typing')?.remove();
  history.push({role:'kira',who:'KIRA',text:d.response});save();render();speak(d.response);
 }catch(e){
  document.getElementById('typing')?.remove();
  history.push({role:'kira',who:'KIRA',text:"Pardon Patron, petite coupure, je suis la."});save();render();
 }
}
render();if(isPatron)document.getElementById('st').innerText="Connecte au Patron Michael 👑";
</script></body></html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE.replace("__PWD__", KIRA_PASSWORD))

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        if not data or data.get('password')!= KIRA_PASSWORD:
            return jsonify({"response": "Acces refuse."}), 403
        user_msg = data.get('message','')
        user_name = data.get('name','Patron')
        is_patron = data.get('isPatron', False)
        hist = data.get('history', [])
        extra = " L'utilisateur est Michael le PATRON SUPREME. Loyauté absolue." if is_patron else f" L'utilisateur est {user_name}, invite. Le vrai Patron est Michael."
        messages = [{"role": "system", "content": SYSTEM_BASE + extra}]
        for h in hist[-6:]:
            role = "user" if h['role']=='toi' else "assistant"
            messages.append({"role": role, "content": h['text']})
        messages.append({"role": "user", "content": user_msg})
        comp = client.chat.completions.create(model="llama3-70b-8192", messages=messages, temperature=0.7, max_tokens=500)
        return jsonify({"response": comp.choices[0].message.content})
    except Exception as e:
        print(e)
        return jsonify({"response": "Pardon Patron Michael, petite coupure mais je suis revenu."}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
