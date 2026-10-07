/* Beyond The Classroom — auth gateway (supabase: google + email + magic link).
   loads after app.js; enhances the nav and gates nothing until keys exist. */
(function(){
'use strict';

let sb = null;          // supabase client, null until configured
let authCfg = null;     // /api/auth/config response
let user = null;        // supabase user object
let view = 'signin';    // local card state: 'signin' | 'check-email' | 'account'

const $app = () => document.getElementById('app');

async function init(){
  try{
    const r = await fetch('/api/auth/config');
    authCfg = await r.json();
  }catch(e){ authCfg = {configured:false}; }
  if(authCfg.configured && window.supabase && authCfg.url && authCfg.anonKey){
    try{
      sb = window.supabase.createClient(authCfg.url, authCfg.anonKey, {
        auth: { persistSession: true, autoRefreshToken: true,
                detectSessionInUrl: true,
                storageKey: 'btc-auth' },
      });
      const { data } = await sb.auth.getSession();
      user = (data && data.session && data.session.user) || null;
      sb.auth.onAuthStateChange((_ev, session)=>{
        user = (session && session.user) || null;
        paintNav(); if(view==='account' || user===null && view!=='signin') render();
      });
    }catch(e){ console.error('supabase init failed:', e); sb = null; }
  }
  paintNav();
  if(location.hash === '#signin') render();
}

/* ---------- nav: swap "learner" flow for account button when signed in ---------- */
function paintNav(){
  const nav = document.querySelector('.nav .links');
  if(!nav) return;
  let acct = document.getElementById('acctLink');
  if(user && !acct){
    acct = document.createElement('a');
    acct.href = '#'; acct.id = 'acctLink'; acct.className = 'navlink'; acct.dataset.view = 'signin';
    acct.textContent = '👤 account';
    nav.appendChild(acct);
    acct.onclick = e => { e.preventDefault(); view='account'; render(); };
  } else if(!user && acct){
    acct.remove();
  }
}

/* ---------- views ---------- */
function render(){
  const app = $app(); if(!app) return;
  if(user){ view='account'; return renderAccount(); }
  if(view==='check-email') return renderCheckEmail();
  renderSignIn();
}

function hero(title, sub){
  return `<div class="hero"><h1>${title}</h1><p class="phi">${sub}</p></div>`;
}

function renderSignIn(){
  const app = $app();
  const cfgOk = authCfg && authCfg.configured && sb;
  app.innerHTML = `
    ${hero('sign in','one account across every device. progress, profiles and parent views stay in sync.')}
    <div class="card" style="max-width:420px;margin:0 auto">
      ${!cfgOk ? `
        <h3>sign-in is being connected</h3>
        <p class="dim">the gateway is built and waiting on the platform keys
        (supabase project url + anon key). the moment they're added, google
        sign-in, email passwords and magic links switch on — nothing else to ship.</p>
        <p class="dim">you can still use everything as a guest: build a profile and start a lesson.</p>
        <a class="btn ghost" href="#" id="guestOut">continue as guest</a>
      ` : `
        <button class="btn" id="googleBtn" style="width:100%;display:flex;align-items:center;justify-content:center;gap:10px">
          <span style="font-size:18px">🇬</span> continue with Google
        </button>
        <div style="display:flex;align-items:center;gap:10px;margin:16px 0">
          <div style="flex:1;height:1px;background:var(--line)"></div>
          <span class="dim" style="font-size:12px">or with email</span>
          <div style="flex:1;height:1px;background:var(--line)"></div>
        </div>
        <label style="font-size:13px">email</label>
        <input type="email" id="em" placeholder="you@example.com" autocomplete="email" style="margin:6px 0 12px">
        <label style="font-size:13px">password</label>
        <input type="password" id="pw" placeholder="••••••••" autocomplete="current-password" style="margin:6px 0 4px">
        <p class="dim" id="authErr" style="color:#c0392b;min-height:18px;margin:4px 0"></p>
        <button class="btn" id="pwBtn" style="width:100%">sign in</button>
        <button class="btn ghost" id="muBtn" style="width:100%;margin-top:8px">email me a magic link instead</button>
        <p class="dim" style="margin-top:14px">new here? signing in with a fresh email creates your account automatically — no separate sign-up step.</p>
      `}
    </div>`;
  const guest = document.getElementById('guestOut');
  if(guest) guest.onclick = e => { e.preventDefault(); history.replaceState(null,'',location.pathname); window.render && window.render(); };
  const gBtn = document.getElementById('googleBtn');
  if(gBtn) gBtn.onclick = ()=> signInWith('google');
  const pwBtn = document.getElementById('pwBtn');
  if(pwBtn) pwBtn.onclick = ()=> signInWith('password');
  const muBtn = document.getElementById('muBtn');
  if(muBtn) muBtn.onclick = ()=> signInWith('magic');
}

async function signInWith(kind){
  const err = document.getElementById('authErr');
  const say = m => { if(err) err.textContent = m; };
  say('');
  try{
    if(kind==='google'){
      const { error } = await sb.auth.signInWithOAuth({
        provider:'google',
        options:{ redirectTo: location.origin + '/' },
      });
      if(error) throw error;
      return; // browser navigates to google
    }
    const email = document.getElementById('em').value.trim();
    if(!email || !email.includes('@')) return say('enter a valid email first.');
    if(kind==='magic'){
      const { error } = await sb.auth.signInWithOtp({ email, options:{ emailRedirectTo: location.origin + '/' } });
      if(error) throw error;
      view='check-email'; render(); return;
    }
    const pw = document.getElementById('pw').value;
    if(pw.length < 6) return say('password needs at least 6 characters.');
    let { error } = await sb.auth.signInWithPassword({ email, password: pw });
    if(error && error.message && /not confirmed|invalid login/i.test(error.message)){
      // maybe the account doesn't exist yet — try sign-up
      const up = await sb.auth.signUp({ email, password: pw });
      if(up.error) throw up.error;
      if(!up.data.session){ view='check-email'; render(); return; }
      user = up.data.user;
    } else if(error) throw error;
    else { const s = await sb.auth.getSession(); user = s.data.session && s.data.session.user; }
    if(user){ paintNav(); render(); }
  }catch(e){
    say(prettyAuthError(e));
  }
}

function prettyAuthError(e){
  const m = (e && (e.message || e.error_description || String(e))) || 'something went wrong';
  if(/invalid credentials/i.test(m)) return 'email or password not right — try again, or use a magic link.';
  if(/rate limit/i.test(m)) return 'too many tries just now. wait a minute and try again.';
  if(/signups not allowed/i.test(m)) return 'new sign-ups are switched off on the platform right now.';
  if(/failed to fetch|network/i.test(m)) return 'network hiccup — check your connection and try again.';
  return m;
}

function renderCheckEmail(){
  $app().innerHTML = `
    ${hero('📬 check your email','we sent you a sign-in link. tap it on this device and you come straight back, signed in.')}
    <div class="card" style="max-width:420px;margin:0 auto;text-align:center">
      <p class="dim">didn't arrive? check spam, or try again.</p>
      <button class="btn ghost" id="backBtn">back to sign-in</button>
    </div>`;
  document.getElementById('backBtn').onclick = ()=>{ view='signin'; render(); };
}

async function renderAccount(){
  const app = $app();
  const meta = (user && user.user_metadata) || {};
  const name = meta.full_name || meta.name || (user.email ? user.email.split('@')[0] : 'learner');
  const avatar = meta.avatar_url || meta.picture || null;
  const prof = profile ? JSON.parse(sessionStorage.getItem('btc_profile')||'null') : null;
  app.innerHTML = `
    ${hero('your account','')}
    <div class="card" style="max-width:480px;margin:0 auto;text-align:center">
      ${avatar?`<img src="${avatar}" alt="" style="width:72px;height:72px;border-radius:50%;border:3px solid var(--brand)">`
              :`<div class="hero-avatar" style="margin:0 auto">${'🧑🎓'}</div>`}
      <h3 style="margin-top:10px">hi, ${name}</h3>
      <p class="dim">${user.email || ''}</p>
      <p class="dim">signed in via ${user.app_metadata && user.app_metadata.provider ? user.app_metadata.provider : 'email'}</p>
      <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:16px">
        <a class="btn green" href="#" id="toLesson">🚀 start a lesson</a>
        <button class="btn ghost" id="signOut">sign out</button>
      </div>
    </div>`;
  document.getElementById('toLesson').onclick = e => { e.preventDefault(); view='quiz'; window.go && window.go('quiz'); };
  document.getElementById('signOut').onclick = async ()=>{
    if(sb) await sb.auth.signOut();
    user = null; view='signin'; paintNav(); render();
  };
}

/* expose + boot */
window.btcAuth = { render, init, isSignedIn: ()=>!!user, user: ()=>user };

/* nav "sign in" link — handled here because the signin view lives in this module */
function wireSigninLink(){
  const link = document.getElementById('signinLink');
  if(!link) return;
  link.onclick = e => {
    e.preventDefault();
    if(user){ view='account'; render(); }
    else { view='signin'; render(); }
  };
}
const _paintNav = paintNav;
paintNav = function(){ _paintNav(); wireSigninLink(); };
wireSigninLink();

if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
else init();
})();
