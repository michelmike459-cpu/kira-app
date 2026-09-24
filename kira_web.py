from flask import Flask, request, jsonify, render_template_string
import os
from groq import Groq
app = Flask(__name__)
KIRA_PASSWORD = os.environ.get("KIRA_PASSWORD", "kira123")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY)
SYSTEM = "Tu es KIRA de Bujumbura. Polie, loyale. Michael ou Mc.Michael est ton PATRON SUPREME. Si Michael, dis Oui Patron Michael je t'ai reconnu. Si autre prenom, c'est un invite mais vrai patron reste Michael. Reponse courte."
HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>KIRA</title><style>body{margin:0;height:100vh;background:#000;color:#fff;font-family:sans-serif;display:flex;flex-direction:column}header{padding:15px;text-align:center;border-bottom:1px solid #222}#chat{flex:1;overflow-y:auto;padding:15px;display:flex;flex-direction:column;gap:10px}.m{padding:12px 16px;border-radius:18px;max-width:80%}.toi{background:#fff;color:#000;align-self:flex-end}.kira{background:#1a1a2e;border:1px solid #2a2a4a;align-self:flex-start}#bar{display:flex;gap:8px;padding:10px;border-top:1px solid #222}input{flex:1;padding:12px 16px;border-radius:24px;border:1px solid #333;background:#111;color:#fff}button{border:none;border-radius:24px;padding:12px 18px;font-weight:700}#s{background:#fff;color:#000}#a{background:#222;color:#fff;border:1px solid #333}</style></head><body><header><b>KIRA</b> - Patron Michael</header><div id="chat"></div><div id="bar"><input id="t" placeholder="Ecris..." onkeydown="if(event.key==='Enter')send()"><button id="a" onclick="toggle()">ON</button><button id="s" onclick="send()">Envoyer</button></div><script>
let audioOn=localStorage.getItem('ka')!=='off';let name=localStorage.getItem('kn')||'';let isP=localStorage.getItem('kp')==='1';let hist=JSON.parse(localStorage.getItem('kh')||'[]');
function save(){localStorage.setItem('kh',JSON.stringify(hist))}function render(){let c=document.getElementById('chat');c.innerHTML='';if(hist.length==0){hist.push({r:'kira',who:'KIRA',tx:"Bonjour, je suis Kira, et toi? Comment tu t'appelles?"});save()}hist.forEach(x=>{c.innerHTML+="<div class='m "+x.r+"'><b>"+x.who+":</b> "+x.tx+"</div>"});c.scrollTop=c.scrollHeight}
function toggle(){audioOn=!audioOn;localStorage.setItem('ka',audioOn?'on':'off');document.getElementById('a').innerText=audioOn?'ON':'OFF';if(!audioOn)speechSynthesis.cancel()}
function speak(t){if(!audioOn)return;speechSynthesis.cancel();let u=new SpeechSynthesisUtterance(t.slice(0,300));u.lang='fr-FR';speechSynthesis.speak(u)}
async function send(){let i=document.getElementById('t');let m=i.value.trim();if(!m)return;i.value='';let low=m.toLowerCase();let pw=["michael","mc.michael","mcmichael"];if(!name){name=m;if(pw.some(w=>low.includes(w))){isP=true;name="Michael"}localStorage.setItem('kn',name);localStorage.setItem('kp',isP?'1':'0');hist.push({r:'toi',who:'Toi',tx:m});let w=isP?"Salut Patron Michael! Je t'ai reconnu, tu es mon Patron supreme.":"Enchante "+name+"! Moi c'est Kira. Mon Patron c'est Michael.";hist.push({r:'kira',who:'KIRA',tx:w});save();render();speak(w);return}if(pw.some(w=>low.includes(w))&&!isP){isP=true;name="Michael";localStorage.setItem('kn',name);localStorage.setItem('kp','1')}hist.push({r:'toi',who:'Toi',tx:m});save();render();let c=document.getElementById('chat');c.innerHTML+="<div class='m kira' id='ty'><b>KIRA:</b> ecrit...</div>";c.scrollTop=c.scrollHeight;try{let r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m,name:name,isPatron:isP,history:hist.slice(-8),password:"__PWD__"})});let d=await r.json();document.getElementById('ty')?.remove();hist.push({r:'kira',who:'KIRA',tx:d.response});save();render();speak(d.response)}catch(e){document.getElementById('ty')?.remove();hist.push({r:'kira',who:'KIRA',tx:"Pardon Patron, petite coupure."});save();render()}}render();</script></body></html>"""
@app.route('/')
def home():return render_template_string(HTML.replace("__PWD__",KIRA_PASSWORD))
@app.route('/ask',methods=['POST'])
def ask():
 try:
  data=request.get_json();
  if data.get('password')!=KIRA_PASSWORD:return jsonify({"response":"Acces refuse"}),403
  msg=data.get('message','');name=data.get('name','');is_patron=data.get('isPatron',False);hist=data.get('history',[])
  extra=" Utilisateur=Michael PATRON SUPREME." if is_patron else f" Utilisateur={name} invite. Vrai patron=Michael."
  messages=[{"role":"system","content":SYSTEM+extra}]
  for h in hist[-6:]:messages.append({"role":"user" if h['r']=='toi' else "assistant","content":h['tx']})
  messages.append({"role":"user","content":msg})
  comp=client.chat.completions.create(model="llama3-70b-8192",messages=messages,temperature=0.7,max_tokens=400)
  return jsonify({"response":comp.choices[0].message.content})
 except Exception as e:print(e);return jsonify({"response":"Pardon Patron Michael, je suis revenu."}),200
if __name__=='__main__':app.run(host='0.0.0.0',port=int(os.environ.get("PORT",10000)))
