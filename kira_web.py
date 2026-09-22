from flask import Flask, request
import os
app = Flask(__name__)
HTML = """
<html><head>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<meta name="apple-mobile-web-app-capable" content="yes">
<link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/4712/4712027.png">
<link rel="manifest" href="/manifest.json">
<title>KIRA</title>
<style>body{font-family:sans-serif;background:#0f172a;color:white;padding:15px}.box{background:#1e293b;padding:15px;border-radius:15px}input{width:100%;padding:12px;border-radius:10px;border:none;margin-bottom:10px}button{padding:12px;border:none;border-radius:10px;font-weight:bold;margin:2px}.btn-blue{background:#38bdf8;width:48%}.btn-orange{background:#f97316;width:48%}.msg{background:#334155;padding:10px;margin:8px 0;border-radius:10px}</style>
</head><body>
<h3>⚡ KIRA ONLINE</h3>
<div class="box">
<input id="q" placeholder="Parle à KIRA...">
<button class="btn-blue" onclick="ask()">Envoyer</button>
<button class="btn-orange" onclick="speakLast()">🔊</button>
<div id="chat"></div>
</div>
<script>
let lastKira="";
function speak(text){ lastKira=text; speechSynthesis.cancel(); let u=new SpeechSynthesisUtterance(text); u.lang='fr-FR'; u.pitch=1.3; u.rate=0.95; speechSynthesis.speak(u); }
function speakLast(){ if(lastKira) speak(lastKira); }
function ask(){
 let qq=document.getElementById('q').value; if(!qq) return;
 let c=document.getElementById('chat'); c.innerHTML+=`<div class='msg'><b>Toi:</b> ${qq}</div>`;
 fetch('/ask?question='+encodeURIComponent(qq)).then(r=>r.text()).then(t=>{ c.innerHTML+=`<div class='msg'><b>KIRA:</b> ${t}</div>`; speak(t); });
 document.getElementById('q').value='';
}
</script></body></html>
"""
@app.route("/")
def home(): return HTML
@app.route("/manifest.json")
def manifest(): return '{"name":"KIRA","short_name":"KIRA","start_url":"/","display":"standalone","background_color":"#0f172a","theme_color":"#ec4899","icons":[{"src":"https://cdn-icons-png.flaticon.com/512/4712/4712027.png","sizes":"512x512","type":"image/png"}]}', 200, {'Content-Type':'application/json'}
@app.route("/ask")
def ask_route():
 q=request.args.get('question','')
 return f"Oui Patron ! Je suis en ligne 24h/24 maintenant ! Tu as dit : {q}. Et ton PC peut etre eteint."
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0',port=port)