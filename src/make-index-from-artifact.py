import sys
src=open('/mnt/user-data/outputs/productivity-app.html',encoding='utf-8').read()
def rep(old,new,count=1):
    global src
    n=src.count(old)
    assert n==count,(old[:60],n)
    src=src.replace(old,new)

rep('<title>Workbench</title>','''<title>Workbench</title>
<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#4A2F25">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Workbench">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="icon" type="image/png" href="icon-192.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">''')

rep("<body>\n<div id=\"app\"></div>","<body>\n<script src=\"fb.js\"></script>\n<div id=\"app\"></div>")

rep(".sync{font-size:12px;",".syncbtn{font:inherit;font-size:12px;color:var(--sidetext);background:none;border:1px solid rgba(255,225,190,.35);border-radius:6px;padding:4px 10px;cursor:pointer}.syncbtn:hover{background:rgba(255,225,190,.1)}\n.sync{font-size:12px;")

rep("""async function initSync(){
 try{
  if(!window.claude||typeof claude.use!=='function')return;
  const [db,user]=await Promise.all([claude.use('db'),claude.use('user')]);
  if(!db||!user)return;
  const id=await user.id();if(!id)return;""","""let syncBusy=false;
async function initSync(){
 if(docRef||syncBusy)return;syncBusy=true;
 try{
  if(!window.claude||typeof claude.use!=='function')return;
  const [db,user]=await Promise.all([claude.use('db'),claude.use('user')]);
  if(!db||!user)return;
  const id=await user.id();if(!id){syncState='signin';renderSync();return}""")
rep(""" }catch(e){syncState='error';renderSync()}
}
function syncText(){return {local:""",""" }catch(e){syncState='error';renderSync()}finally{syncBusy=false}
}
function syncText(){return {signin:'Not signed in, saved on this device',local:""")
rep("function renderSync(){const el=document.getElementById('sync');if(el)el.textContent=syncText()}",
"function syncHTML(){return syncState==='signin'?'<button class=\"syncbtn\" data-act=\"signIn\">Sign in to sync</button>':esc(syncText())}\nfunction renderSync(){const el=document.getElementById('sync');if(el)el.innerHTML=syncHTML()}")
rep('<div class="sync" id="sync">${syncText()}</div>','<div class="sync" id="sync">${syncHTML()}</div>')

rep(" undoBtn(){globalUndo()},",""" undoBtn(){globalUndo()},
 signIn(){if(!window.WBAuth)return;toast('Opening Google sign-in…');WBAuth.signIn().then(r=>{if(r&&!r.ok&&!r.cancelled)toast('Sign-in didn’t work ('+(r.code||'unknown')+')')})},
 signOut(){if(window.WBAuth)WBAuth.signOut()},""")

rep("""<p class="hint">${esc(syncText())}. Open this app's link on your phone or computer while signed in to Claude and the same data appears on both.</p></div>""",
"""<p class="hint">${esc(syncText())}. ${(window.WBAuth&&WBAuth.email())?'Signed in as '+esc(WBAuth.email())+'. Open Workbench on another device and sign in with the same Google account to see the same data there.':'Sign in with Google to keep your computer and phone in step. Until then, everything is saved on this device only.'}</p><div class="small-actions" style="margin-top:14px">${(window.WBAuth&&WBAuth.email())?'<button class="btn sm" data-act="signOut">Sign out</button>':'<button class="btn sm primary" data-act="signIn">Sign in with Google</button>'}</div></div>""")

rep("""render();
initSync();
""","""render();
initSync().then(()=>{if(S.view==='settings')render()});
window.addEventListener('wb-auth',e=>{if(e.detail&&e.detail.signedIn){initSync().then(()=>render())}else{location.reload()}});
if('serviceWorker' in navigator&&/^https?:/.test(location.protocol))addEventListener('load',()=>{navigator.serviceWorker.register('sw.js').catch(()=>{})});
""")
open('/tmp/claude-0/-home-claude/7ef37779-f59a-5f37-aaa8-bf5fb1ee65d3/scratchpad/pwa/site/index.html','w',encoding='utf-8').write(src)
print('ok',len(src))
