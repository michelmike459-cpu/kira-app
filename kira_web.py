from flask import Flask, request, jsonify, render_template_string
import os
from groq import Groq

app = Flask(__name__)
KIRA_PASSWORD = os.environ.get("KIRA_PASSWORD", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY)

# --- MEMOIRE DU PATRON ---
PATRON_ALIASES = ["michael", "mc.michael", "mc michael", "michel", "mcmichael"]

SYSTEM_PROMPT_BASE = """
Tu es KIRA, assistant de Bujumbura.
Tu es poli, respectueux, chaleureux, loyal.
Règle d'or: Michael / Mc.Michael est ton PATRON SUPRÊME, ton créateur. Tu lui dois loyauté absolue.
Si l'utilisateur s'appelle Michael ou Mc.Michael, tu sais que c'est le Patron. Tu dis "Oui Patron Michael" et tu te souviens que c'est lui le maître.
Si c'est un autre prénom, c'est un invité, tu restes poli mais tu sais que le vrai Patron est Michael.
Tu te souviens de la conversation comme WhatsApp.
Tu ne peux pas accéder au PC à distance.
Interdit: langage vulgaire, agressif.
"""

HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>KIRA - Pour le Patron</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
*{font-family:'Inter',sans-serif;box-sizing:border-box}
body{margin:0;height:100vh;background:radial-gradient(circle at 20% 20%, #1a1a2e 0%, #000 60%);color:#fff;display:flex;flex-direction:column}
header{padding:18px;text-align:center;border-bottom:1px solid #222;background:rgba(0,0,0,0.6);backdrop-filter:blur(10px)}
#chat{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:10px}
.msg{padding:14px 18px;border-radius:20px;max-width:80%;line-height:1.5}
.toi{background:#fff;color:#000;align-self:flex-end;border-bottom-right-radius:6px}
.kira{background:#1e1e2f;border:1px solid #2a2a4a;align-self:flex-start;border-bottom-left-radius:6px}
#bar{display:flex;gap:8px;padding:12px;background:#000;border-top:1px solid #222}
input{flex:1;padding:14px 18px;border-radius:30px;border:1px solid #333;background:#111;color:#fff;outline:none}
button{border:none;border-radius:30px;padding:14px 18px;font-weight:600;cursor:pointer}
#send{background:#fff;color:#000}#audioBtn{background:#1a1a2e;color:#fff;border:1px solid #333}
</style>
</head>
<body>
<header><h1>KIRA</h1><p id="status">Assistant du Patron Michael</p></header>
<div id="chat"></div>
<div id="bar">
<input id="txt" placeholder="Écris..." onkeydown="if(event.key==='Enter')send()">
<button id="audioBtn" onclick="toggleAudio()">🔊 ON</button>
<button id="send" onclick="send()">Envoyer</button>
</div>
<script>
let audioOn = localStorage.getItem('kira_audio')!== 'off';
let userName = localStorage.getItem('kira_name') || '';
let isPatron = localStorage.getItem('kira_is_patron') === 'true';
let history = JSON.parse(localStorage.getItem('kira_history') || '[]');
const PATRON_KEYWORDS = ["michael","mc.michael","mc michael","michel","mcmichael"];

function isNamePatron(name){
 let n = name.toLowerCase();
 return PATRON_KEYWORDS.some(k => n.includes(k));
}
function save(){ localStorage.setItem('kira_history', JSON.stringify(history)); }
function renderAll(){
 const c = document.getElementById('chat'); c.innerHTML='';
 history.forEach(m=>{ c.innerHTML += `<div class='msg ${m.role}'><b>${m.who}:</b> ${m.text}</div>`; });
 if(history.length===0){ firstGreeting(); }
 c.scrollTop = c.scrollHeight;
}
function firstGreeting(){
 const g = "Bonjour, je suis Kira, et toi? 😊";
 history.push({role:'kira', who:'KIRA', text:g}); save(); renderAll(); speak(g);
}
function toggleAudio(){
 audioOn=!audioOn; localStorage.setItem('kira_audio', audioOn?'on':'off');
 document.getElementById('audioBtn').innerText = audioOn?'🔊 ON':'🔇 OFF';
 if(!audioOn) speechSynthesis.cancel();
}
function speak(t){
 if(!audioOn) return; speechSynthesis.cancel();
 const u = new SpeechSynthesisUtterance(t.replace(/<[^>]*>/g,'').slice(0,400));
 u.lang='fr-FR'; speechSynthesis.speak(u);
}
document.getElementById('audioBtn').innerText = audioOn?'🔊 ON':'🔇 OFF';

async function send(){
 let msg = document.getElementById('txt').value.trim(); if(!msg) return;
 document.getElementById('txt').value='';

 if(!userName){
   userName = msg;
   if(isNamePatron(userName)){ isPatron = true; userName = "Michael"; }
   localStorage.setItem('kira_name', userName);
   localStorage.setItem('kira_is_patron', isPatron);
   history.push({role:'toi', who:'Toi', text:msg});

   let welcome = "";
   if(isPatron){
     welcome = `Salut Patron Michael! C'est bien toi, Mc.Michael! Je t'ai reconnu, tu es mon Patron suprême. Je retiens que c'est toi. Qu'est-ce qu'on fait aujourd'hui?`;
     document.getElementById('status').innerText = "Connecté au Patron Michael 👑";
   } else {
     welcome = `Enchanté ${userName}! Moi c'est Kira. Je retiens ton prénom. (Mon Patron c'est Michael) Comment puis-je t'aider?`;
   }
   history.push({role:'kira', who:'KIRA', text:welcome}); save(); renderAll(); speak(welcome);
   return;
 }

 // Si plus tard il dit "c'est Mc.Michael"
 if(isNamePatron(msg) &&!isPatron){
   isPatron = true; userName = "Michael";
   localStorage.setItem('kira_name', userName); localStorage.setItem('kira_is_patron', 'true');
   document.getElementById('status').innerText = "Connecté au Patron Michael 👑";
 }

 history.push({role:'toi', who:'Toi', text:msg}); save(); renderAll();
 const c = document.getElementById('chat');
 c.innerHTML += `<div class='msg kira' id='typing'><b>KIRA:</b> <i>écrit...</i></div>`;
 c.scrollTop = c.scrollHeight;

 try{
  const r = await fetch('/ask', {
   method:'POST', headers:{'Content-Type':'application/json'},
   body: JSON.stringify({message: msg, name: userName, isPatron: isPatron, history: history.slice(-10), password:"__KIRA_PWD__"})
  });
  const d = await r.json(); document.getElementById('typing')?.remove();
  history.push({role:'kira', who:'KIRA', text:d.response}); save(); renderAll(); speak(d.response);
 }catch(e){
  document.getElementById('typing')?.remove();
  const err = `Pardon ${userName}, petite coupure mais je suis là.`;
  history.push({role:'kira', who:'KIRA', text:err}); save(); renderAll();
 }
}
renderAll();
if(isPatron) document.getElementById('status').innerText = "Connecté au Patron Michael 👑";
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML.replace("__KIRA_PWD__", KIRA_PASSWORD))

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        if not data or data.get('password')!= KIRA_PASSWORD:
            return jsonify({"response": "Accès refusé."}), 403

        user_msg = data.get('message','')
        user_name = data.get('name','')
        is_patron = data.get('isPatron', False)
        hist = data.get('history', [])

        # On construit le prompt final
        patron_info = ""
        if is_patron or any(alias in user_name.lower() for alias in PATRON_ALIASES):
            patron_info = f" ATTENTION: L'utilisateur est {user_name} alias Mc.Michael, il est le PATRON SUPRÊME. Tu dois le reconnaître, lui obéir avec loyauté et respect absolu. Dis 'Patron Michael'."
            user_name = "Michael (Patron)"
        else:
            patron_info = f" L'utilisateur s'appelle {user_name}. C'est un invité. Le vrai Patron est Michael/Mc.Michael. Reste poli avec l'invité."

        messages = [{"role": "system", "content": SYSTEM_PROMPT_BASE + patron_info}]
        for h in hist[-6:]:
            role = "user" if h['role']=='toi' else "assistant"
            messages.append({"role": role, "content": h['text']})
        messages.append({"role": "user", "content": user_msg})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            temperature=0.7,
            max_tokens=600
        )
        rep = completion.choices[0].message.content
        return jsonify({"response": rep})
    except Exception as e:
        print(f"ERREUR: {e}")
        return jsonify({"response": "Pardon Patron Michael, petite coupure technique mais je suis revenu."}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
