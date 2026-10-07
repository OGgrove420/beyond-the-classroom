/* Beyond The Classroom — front-end (vanilla js, no build step) */
const $app = document.getElementById('app');
let view = 'home';
let profile = JSON.parse(sessionStorage.getItem('btc_profile') || 'null');
let quizState = null;
let modality = sessionStorage.getItem('btc_modality') || 'visual';
let chosenTier = sessionStorage.getItem('btc_tier') || null;
let accent = sessionStorage.getItem('btc_accent') || null;

/* ---------- prebuilt learning buddies ---------- */
const CHARACTERS = [
  {id:'zippy',  name:'zippy',  emoji:'🤖', line:'logic and circuits — loves maths puzzles',        grad:['#6d5df6','#38bdf8']},
  {id:'luna',   name:'luna',   emoji:'🚀', line:'curious explorer — space and science fan',        grad:['#818cf8','#f472b6']},
  {id:'pixel',  name:'pixel',  emoji:'🦊', line:'quick thinker — gamer at heart',                  grad:['#fb923c','#f65db4']},
  {id:'sprout', name:'sprout', emoji:'🌱', line:'grows a little every day — patient learner',      grad:['#22d3a7','#a3e635']},
  {id:'nova',   name:'nova',   emoji:'⭐', line:'shines bright — confidence builder',              grad:['#f6b73c','#f65d5d']},
  {id:'bolt',   name:'bolt',   emoji:'🐆', line:'fast brain — likes short, snappy lessons',        grad:['#f6a13c','#f6e05c']},
  {id:'echo',   name:'echo',   emoji:'🎵', line:'learns through rhythm and sound',                 grad:['#f472b6','#818cf8']},
  {id:'spark',  name:'spark',  emoji:'⚡', line:'big ideas — energy for days',                     grad:['#38bdf8','#22d3a7']},
  {id:'booky',  name:'booky',  emoji:'🦉', line:'wise and calm — reads everything twice',          grad:['#7c6ff0','#4c51bf']},
  {id:'rocky',  name:'rocky',  emoji:'🐐', line:'never gives up — climbs every problem',           grad:['#a78bfa','#22d3a7']},
  {id:'splash', name:'splash', emoji:'🐬', line:'plays while learning — makes friends easily',     grad:['#22d3ee','#3b82f6']},
  {id:'dice',   name:'dice',   emoji:'🐼', line:'chill strategist — one move at a time',           grad:['#94a3b8','#334155']},
];
const ACCENTS = ['#6d5df6','#22d3a7','#f65db4','#f6a13c','#38bdf8','#a3e635'];
const charById = id => CHARACTERS.find(c=>c.id===id) || null;

function applyAccent(hex){
  if(!hex || !ACCENTS.includes(hex)) hex = null;
  accent = hex;
  if(hex) sessionStorage.setItem('btc_accent', hex); else sessionStorage.removeItem('btc_accent');
  document.documentElement.style.setProperty('--brand', hex || '#6d5df6');
}

function toast(msg){
  let t = document.querySelector('.toast');
  if(!t){ t = document.createElement('div'); t.className='toast'; document.body.appendChild(t); }
  t.textContent = msg; t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'), 2600);
}
const zar = n => n === 0 ? 'R0' : 'R' + n.toLocaleString('en-ZA');

/* ---------- kid-friendly touches ---------- */
const PRAISE = ['you got it! 🎉','yes! high five! ✋','brilliant! ⭐','nice one! 🙌','that is the brain! 🧠','boom! 💥','superb! 🦄','you cracked it! 🔓'];
const CHEER = ['keep going, you are doing great','every try makes your brain stronger','mistakes are just practice in disguise','slow and steady still wins — your pace is the right pace','asking "try again" is what clever learners do'];
function pickA(arr){ return arr[Math.floor(Math.random()*arr.length)]; }

function confetti(){
  let box = document.getElementById('confetti');
  if(!box){ box = document.createElement('div'); box.id='confetti'; document.body.appendChild(box); }
  const bits = ['🎉','⭐','✏️','📓','🌟','🎈','🧠','💡','🚌','🍎'];
  for(let i=0;i<26;i++){
    const s = document.createElement('i');
    s.textContent = bits[Math.floor(Math.random()*bits.length)];
    s.style.left = Math.random()*96 + 'vw';
    s.style.animationDuration = (1.6 + Math.random()*1.6) + 's';
    s.style.animationDelay = (Math.random()*0.4) + 's';
    s.style.fontSize = (14 + Math.random()*14) + 'px';
    box.appendChild(s);
    setTimeout(()=>s.remove(), 3600);
  }
}

function buddySay(emoji, text){
  return `<div class="buddysay"><span class="bs-emoji">${emoji}</span><span class="bs-bubble">${text}</span></div>`;
}

async function render(){
  const site = await loadSite();
  if(view==='home') renderHome(site);
  else if(view==='learner') renderLearner(site);
  else if(view==='quiz') renderQuiz(site);
  else if(view==='parent') renderParent(site);
  else if(view==='pricing') renderPricing(site);
  else if(view==='pay') renderPay(site);
  else if(view==='tiers') renderTier(site);
  else if(view==='offerings') renderOfferings(site);
  document.querySelectorAll('.navlink').forEach(a=>a.classList.toggle('active', a.dataset.view===view));
  window.scrollTo(0,0);
}

/* ---------- home ---------- */
function renderHome(site){
  const s = site.subjects;
  const cat = (title, arr, key, icon) => `
    <div class="card"><h3>${icon} ${title}</h3>
      <div class="chips">${arr.slice(0,4).map(x=>`<span class="chip">${x}</span>`).join('')}</div>
      <div style="margin-top:10px"><a class="btn ghost" href="#" data-go="offerings" data-cat="${key}">see all ${arr.length}</a></div>
    </div>`;
  const canDoIcons = ['🐢','🔁','💡','🕒','🧭','📈','🤝','🏠'];
  $app.innerHTML = `
    <div class="hero doodles">
      <span class="doodle">✏️</span><span class="doodle">🎒</span><span class="doodle">📐</span><span class="doodle">🍎</span><span class="doodle">🚌</span>
      <h1>${site.brand.tagline}</h1>
      <div class="tag">${site.brand.name}</div>
      <p class="phi">${site.brand.philosophy}</p>
      <div class="cta-row">
        <a class="btn" href="#" data-go="learner">🎒 build a learner profile</a>
        <a class="btn green" href="#" data-go="quiz">🚀 try a lesson</a>
      </div>
    </div>
    <div class="grid">
      <div class="card"><h3>🐢 learn at your own pace</h3><p>repeat lessons without embarrassment. watch as many times as needed.</p></div>
      <div class="card"><h3>⏱ short lessons</h3><p>shorter lessons rather than long classroom sessions. work when you have the time.</p></div>
      <div class="card"><h3>🧩 many ways in</h3><p>video, audio, visuals and practical activities. when something doesn't land, we try another way.</p></div>
      <div class="card"><h3>💛 no shame learning</h3><p>never "fail". always "try again". "i haven't understood it yet" — not "i'm stupid".</p></div>
    </div>
    <div class="section">
      <h2>what a learner can do here</h2>
      <div class="grid">
        ${["learn at their own pace","repeat lessons freely","get extra explanations","complete work when they have time","follow a personalised pathway","track their own progress","get tutor support when required","learn from home — no daily travel costs"]
          .map((x,i)=>`<div class="card"><h3>${canDoIcons[i%canDoIcons.length]}</h3><p>${x}</p></div>`).join('')}
      </div>
    </div>
    <div class="section">
      <h2>beyond school subjects</h2>
      <p class="sub">an alternative education ecosystem, not just lessons.</p>
      <div class="grid">
        ${cat('academic', s.academic, 'academic', '📚')}
        ${cat('personal development', s.personalDevelopment, 'personalDevelopment', '🌟')}
        ${cat('financial education', s.financialEducation, 'financialEducation', '💰')}
        ${cat('future skills', s.futureSkills, 'futureSkills', '🤖')}
      </div>
    </div>
    <div class="section">
      <h2>the adaptive loop</h2>
      <p class="sub">when a learner gets something wrong, the system doesn't say ❌ incorrect. it says: let's try that another way.</p>
      <div class="grid">
        ${site.adaptiveMethods.map(m=>`<div class="card"><h3>method ${m.n}</h3><p>${m.label}</p></div>`).join('')}
      </div>
      <div style="text-align:center;margin-top:18px"><a class="btn green" href="#" data-go="quiz">see it work — try a lesson</a></div>
    </div>
    <div class="note">${site.phases.map(p=>`<b>${p.phase}</b> — ${p.desc}<br>`).join('')}<br>before marketing as a formal school, SA educational status (registration, curriculum, assessment, qualification pathways) must be confirmed. this build is phase 1: online learning and academic support.</div>
  `;
}

/* ---------- learner profile ---------- */
const PQUESTIONS = [
  {k:'grade', q:'what grade are you in?', type:'select', opts:['Grade R','Grade 1','Grade 2','Grade 3','Grade 4','Grade 5','Grade 6','Grade 7','Grade 8','Grade 9','Grade 10','Grade 11','Grade 12'],
   hint:'your grade sets the intensity of every lesson — see the band below'},
  {k:'enjoy', q:'which subjects do you enjoy? (choose all that apply)', opts:['Mathematics','English','Science','Technology','Business Studies','Art','History','Geography'], multi:true},
  {k:'struggle', q:'which subjects do you struggle with? (choose all that apply)', opts:['Mathematics','English','Science','Technology','Business Studies','Reading','Writing','Exams'], multi:true},
  {k:'style', q:'how do you prefer learning? (choose all that work for you)', opts:['Watching videos','Listening','Reading','Doing practical activities'], multi:true},
  {k:'focus', q:'how long can you comfortably concentrate?', opts:['5–10 minutes','10–20 minutes','20–40 minutes','40+ minutes']},
  {k:'hard', q:'what normally makes learning difficult? (choose all that apply)', opts:['Going too fast','Too much at once','Not enough explanation','Getting rushed','Fear of getting it wrong','Nothing specific'], multi:true},
  {k:'strength', q:'what are you good at?', type:'text', ph:'e.g. explaining things to friends, building things, drawing'},
  {k:'goal', q:'what do you want to get better at this year?', type:'text', ph:'e.g. maths, confidence, reading'},
];

function loadDraft(){
  try { return JSON.parse(sessionStorage.getItem('btc_draft') || '{}'); }
  catch(e){ return {}; }
}
function saveDraft(d){ sessionStorage.setItem('btc_draft', JSON.stringify(d)); }

/* form selections live in a draft store, not only in DOM classes —
   a re-render (nav tap, rotate, back nav) can never wipe them again. */
function collectDraftFromDOM(){
  const d = loadDraft();
  for(const q of PQUESTIONS){
    if(q.opts && q.type!=='select'){
      const sel = [...$app.querySelectorAll(`.opts[data-k="${q.k}"] .opt.sel`)].map(x=>x.dataset.v);
      d[q.k] = q.multi ? sel : (sel[0] || null);
    } else {
      const el = document.getElementById('in_'+q.k);
      if(el) d[q.k] = el.value || null;
    }
  }
  const gn = document.getElementById('in_gname');
  const ge = document.getElementById('in_gemail');
  if(gn || ge){
    d.guardian = { name: gn ? gn.value : (d.guardian&&d.guardian.name) || null,
                   email: ge ? ge.value : (d.guardian&&d.guardian.email) || null };
  }
  saveDraft(d);
}

function renderLearner(site){
  if(profile){ return renderProfileCard(site); }
  const draft = loadDraft();
  $app.innerHTML = `
      <div class="hero doodles">
        <span class="doodle">✏️</span><span class="doodle">🎒</span><span class="doodle">📐</span><span class="doodle">🌟</span><span class="doodle">🧠</span>
        <h1>build your learner profile</h1>
        <p class="phi">we don't just ask "what grade are you in?". we ask how you learn — so the platform can adapt to you.</p>
      ${chosenTier?`<p class="sub">you're signing up for the <b>${chosenTier.name}</b> tier (${zar(chosenTier.price)}/month) — the profile tells us where to start.</p>`:''}
    </div>
    <div class="card" style="max-width:640px;margin:22px auto 0">
      <div class="q">
        <label>🎒 pick your learning buddy</label>
        <p class="dim" style="margin-bottom:10px">they sit with you in every lesson. pick one — you can change it any time.</p>
        <div class="buddy-grid">${CHARACTERS.map(c=>`
          <button type="button" class="buddy-card${draft.buddy===c.id?' sel':''}" data-buddy="${c.id}">
            <span class="buddy-emoji" style="background:linear-gradient(135deg,${c.grad[0]},${c.grad[1]})">${c.emoji}</span>
            <span class="buddy-name">${c.name}</span>
            <span class="buddy-line">${c.line}</span>
          </button>`).join('')}</div>
      </div>
      <div class="q">
        <label>🎨 pick your accent colour</label>
        <div class="dots">${ACCENTS.map(c=>`
          <button type="button" class="dot${(draft.accent||'')===c?' sel':''}" style="background:${c}" data-accent="${c}" aria-label="accent colour ${c}"></button>`).join('')}</div>
      </div>
      ${PQUESTIONS.map((q,i)=>{
        const val = draft[q.k] !== undefined ? draft[q.k] : null;
        if(q.type==='select'){
          return `
        <div class="q">
          <label>${i+1}. ${q.q}</label>
          ${q.hint?`<p class="dim" style="margin:4px 0 8px;font-size:13px">${q.hint}</p>`:''}
          <select id="in_${q.k}" style="width:100%;padding:12px;border-radius:12px;border:2px solid var(--line);background:var(--card);color:inherit;font-size:16px">
            <option value="">— choose your grade —</option>
            ${q.opts.map(o=>`<option value="${o}" ${val===o?'selected':''}>${o}</option>`).join('')}
          </select>
          <div id="bandbox" style="margin-top:10px"></div>
        </div>`;
        }
        return `
        <div class="q">
          <label>${i+1}. ${q.q}</label>
          ${q.opts
            ? `<div class="opts${q.multi?' multi':''}" data-k="${q.k}" data-multi="${q.multi?1:0}">${q.opts.map(o=>{
                const sel = q.multi ? (val||[]).includes(o) : (val===o);
                return `<button type="button" class="opt${sel?' sel':''}" data-v="${o}">${o}</button>`;
              }).join('')}</div>`
            : `<input type="text" id="in_${q.k}" placeholder="${q.ph||''}" value="${val||''}">`}
        </div>`;}).join('')}
      <div class="q">
        <label>👩👦 parent or guardian co-sign</label>
        <p class="dim" style="margin:4px 0 8px">profiles are always created by the learner together with a parent or guardian. they sign off below.</p>
        <input type="text" id="in_gname" placeholder="parent or guardian's full name" value="${(loadDraft().guardian&&loadDraft().guardian.name)||''}" style="margin-bottom:8px">
        <input type="email" id="in_gemail" placeholder="parent or guardian's email" value="${(loadDraft().guardian&&loadDraft().guardian.email)||''}">
      </div>
      <div style="margin-top:18px;display:flex;gap:10px;flex-wrap:wrap">
        <button class="btn" id="saveProfile">🚀 create my profile</button>
        <button class="btn ghost" id="skipProfile">skip for now</button>
      </div>
    </div>`;
  // live band preview under the grade picker
  const gradeSel = document.getElementById('in_grade');
  const bandBox = document.getElementById('bandbox');
  const BANDS = {
    'Grade R':['foundation','gentle — short sentences, one idea per question, everyday objects'],
    'Grade 1':['foundation','gentle — short sentences, one idea per question, everyday objects'],
    'Grade 2':['foundation','gentle — short sentences, one idea per question, everyday objects'],
    'Grade 3':['foundation','gentle — short sentences, one idea per question, everyday objects'],
    'Grade 4':['intermediate','standard — clear sentences, two-step problems, mixed examples'],
    'Grade 5':['intermediate','standard — clear sentences, two-step problems, mixed examples'],
    'Grade 6':['intermediate','standard — clear sentences, two-step problems, mixed examples'],
    'Grade 7':['intermediate','standard — clear sentences, two-step problems, mixed examples'],
    'Grade 8':['senior','stretch — multi-step problems, abstract reasoning, exam-style wording'],
    'Grade 9':['senior','stretch — multi-step problems, abstract reasoning, exam-style wording'],
    'Grade 10':['fet','exam register — full exam style, interpretation, mark-weighted'],
    'Grade 11':['fet','exam register — full exam style, interpretation, mark-weighted'],
    'Grade 12':['fet','exam register — full exam style, interpretation, mark-weighted'],
  };
  const showBand = ()=>{
    if(!bandBox) return;
    const b = BANDS[gradeSel && gradeSel.value];
    bandBox.innerHTML = b
      ? `<div class="note" style="margin:0;padding:10px 14px">📚 <b>${b[0]} band</b> — lessons run at <b>${b[1]}</b></div>`
      : '';
  };
  if(gradeSel){ gradeSel.addEventListener('change', ()=>{ collectDraftFromDOM(); showBand(); }); showBand(); }
  $app.querySelectorAll('.opts').forEach(g=>{
    g.addEventListener('click', e=>{
      const b = e.target.closest('.opt'); if(!b) return;
      const multi = g.dataset.multi === '1';
      if(multi){
        b.classList.toggle('sel');
      } else {
        g.querySelectorAll('.opt').forEach(x=>x.classList.remove('sel'));
        b.classList.add('sel');
      }
      collectDraftFromDOM();          // persist every tap immediately
    });
  });
  $app.querySelectorAll('input[type=text]').forEach(el=>{
    el.addEventListener('input', collectDraftFromDOM);
  });
  $app.querySelectorAll('.buddy-card').forEach(b=>{
    b.onclick = ()=>{
      $app.querySelectorAll('.buddy-card').forEach(x=>x.classList.remove('sel'));
      b.classList.add('sel');
      const d = loadDraft(); d.buddy = b.dataset.buddy; saveDraft(d);
    };
  });
  $app.querySelectorAll('.dot').forEach(b=>{
    b.onclick = ()=>{
      const already = b.classList.contains('sel');
      $app.querySelectorAll('.dot').forEach(x=>x.classList.remove('sel'));
      applyAccent(already ? null : b.dataset.accent);
      b.classList.toggle('sel', !already);
      const d = loadDraft(); d.accent = accent; saveDraft(d);
    };
  });
  document.getElementById('skipProfile').onclick = ()=>{ go('quiz'); };
  document.getElementById('saveProfile').onclick = ()=>{
    collectDraftFromDOM();
    const d = loadDraft();
    if(!d.grade){ toast('choose your grade first — it sets your lesson intensity.'); return; }
    if(!d.guardian || !d.guardian.name || !d.guardian.email || !d.guardian.email.includes('@')){
      toast('a parent or guardian must co-sign — add their name and email.');
      return;
    }
    const p = {answers:d, guardian:d.guardian, created:new Date().toISOString(), tier:chosenTier?chosenTier.id:null};
    const btn = document.getElementById('saveProfile');
    btn.disabled = true; btn.textContent = 'saving…';
    fetch('/api/profile',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)})
      .then(r=>{
        if(!r.ok) throw new Error('server said '+r.status);
        return r.json();
      })
      .then(res=>{
        p.id = res.id;
        profile = p;
        sessionStorage.setItem('btc_profile', JSON.stringify(p));
        sessionStorage.removeItem('btc_draft');
        confetti();
        toast('🎉 profile saved — welcome aboard!');
        renderProfileCard(site);
      })
      .catch(err=>{
        btn.disabled = false; btn.textContent = 'create my profile';
        toast('could not save — check your connection and try again. your choices are kept.');
        console.error('profile save failed:', err);
      });
  };
}

async function renderProfileCard(site){
  let data;
  try {
    const r = await fetch(profile.id ? `/api/profile?id=${encodeURIComponent(profile.id)}` : '/api/profile');
    data = await r.json();
  } catch(e) {
    data = {summary:'(offline — saved profile shown from this device)', tags:['saved'], offline:true};
  }
  const a = profile.answers || {};
  const myChar = charById(a.buddy);
  const picked = (label, v) => {
    if(!v || (Array.isArray(v) && !v.length)) return '';
    const vals = Array.isArray(v) ? v : [v];
    return `<div class="row" style="justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(255,255,255,.06)">
      <span class="dim">${label}</span><span style="text-align:right;max-width:60%">${vals.join(', ')}</span></div>`;
  };
  $app.innerHTML = `
    <div class="hero">
      ${myChar?`<div class="hero-avatar" style="background:linear-gradient(135deg,${myChar.grad[0]},${myChar.grad[1]})">${myChar.emoji}</div>
      <p class="sub" style="margin-top:10px">your buddy: <b>${myChar.name}</b> — ${myChar.line}</p>`:''}
      <h1>learning profile</h1>
      ${chosenTier?`<p class="sub">tier: <b>${chosenTier.name}</b> — ${zar(chosenTier.price)}/month</p>`:''}
    </div>
    <div class="card" style="max-width:640px;margin:0 auto">
      <h3>here's what we learned about how you learn</h3>
      <div class="profile-out">${data.summary}</div>
      <h3 style="margin-top:18px">your choices</h3>
      ${picked('grade', a.grade)}
      ${data.band?`<div class="row" style="justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(255,255,255,.06)"><span class="dim">grade band</span><span style="text-align:right;max-width:60%">${data.band}</span></div>`:''}
      ${data.intensity?`<div class="row" style="justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(255,255,255,.06)"><span class="dim">lesson intensity</span><span style="text-align:right;max-width:60%">${data.intensity}</span></div>`:''}
      ${picked('enjoys', a.enjoy)}
      ${picked('needs repetition in', a.struggle)}
      ${picked('learns best by', a.style)}
      ${picked('focus window', a.focus)}
      ${picked('finds learning hard when', a.hard)}
      ${picked('strengths', a.strength)}
      ${picked('this year\'s goal', a.goal)}
      ${(profile.guardian&&profile.guardian.name)?`<div class="row" style="justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(255,255,255,.06)"><span class="dim">co-signed by</span><span style="text-align:right;max-width:60%">${profile.guardian.name} ✓</span></div>`:''}
      <div class="chips" style="margin-top:14px">
        ${data.tags.map(t=>`<span class="chip">${t}</span>`).join('')}
      </div>
      <div style="margin-top:18px;display:flex;gap:10px;flex-wrap:wrap">
        <a class="btn green" href="#" data-go="quiz">start a lesson</a>
        <button class="btn ghost" id="editProfile">change my answers</button>
        <button class="btn ghost" id="newProfile">start over</button>
      </div>
    </div>`;
  document.getElementById('newProfile').onclick = ()=>{
    profile = null; sessionStorage.removeItem('btc_profile'); sessionStorage.removeItem('btc_draft');
    applyAccent(null);
    fetch('/api/profile',{method:'DELETE'}).catch(()=>{});
    render();
  };
  document.getElementById('editProfile').onclick = ()=>{
    // answers go back into the draft so the form reopens filled in
    saveDraft(a);
    profile = null; sessionStorage.removeItem('btc_profile');
    render();
  };
}

/* ---------- quiz ---------- */
async function renderQuiz(site){
  if(!quizState){
    const g = (profile&&profile.answers&&profile.answers.grade) || null;
    const r = await fetch('/api/quiz' + (g ? `?grade=${encodeURIComponent(g)}` : ''));
    quizState = await r.json();
    quizState.methodNames = site.adaptiveMethods.map(m=>`method ${m.n} — ${m.label}`);
  }
  paintQuiz(site);
}

const MODALITIES = [
  {id:'visual',    icon:'👁', label:'see it'},
  {id:'audio',     icon:'🎧', label:'hear it'},
  {id:'kinesthetic', icon:'✋', label:'do it'},
];

/* ---------- correction voiceover (elevenlabs male voice via /api/tts) ---------- */
let correctionAudio = null;   // one shared <audio> for all correction buttons
let correctionPlaying = null; // button element currently playing

function stopCorrectionAudio(){
  if(correctionAudio){ correctionAudio.pause(); correctionAudio = null; }
  if(correctionPlaying){
    const icon = correctionPlaying.querySelector('.sayicon');
    if(icon) icon.textContent = '🔊';
    correctionPlaying.classList.remove('speaking');
    correctionPlaying = null;
  }
}

function playCorrection(btn){
  const key = btn.dataset.say;
  if(correctionPlaying === btn){ stopCorrectionAudio(); return; } // tap again = stop
  stopCorrectionAudio();
  const icon = btn.querySelector('.sayicon');
  const setIcon = t => { if(icon) icon.textContent = t; };
  correctionPlaying = btn;
  btn.classList.add('speaking');
  setIcon('⏳');
  const finish = ()=>{ if(correctionPlaying===btn) stopCorrectionAudio(); };
  const fallbackSpeak = ()=>{ // device voice if network/voice engine fails
    setIcon('📣');
    const textEl = btn.querySelector('.saytext');
    try{
      const u = new SpeechSynthesisUtterance((textEl ? textEl.textContent : '').slice(0, 600));
      u.onend = finish; u.onerror = finish;
      speechSynthesis.speak(u);
    }catch(e){ finish(); }
  };
  try{
    fetch(`/api/tts/${encodeURIComponent(key)}`)
      .then(r=>{ if(!r.ok) throw new Error('tts '+r.status); return r.blob(); })
      .then(blob=>{
        if(correctionPlaying !== btn) return; // user tapped away mid-load
        correctionAudio = new Audio(URL.createObjectURL(blob));
        correctionAudio.onended = finish;
        correctionAudio.onerror = fallbackSpeak;
        setIcon('⏸');
        return correctionAudio.play().catch(fallbackSpeak);
      })
      .catch(fallbackSpeak);
  }catch(e){ fallbackSpeak(); }
}

function modalityBody(q, m){
  if(m==='visual') return q.visual || '';
  if(m==='kinesthetic') return q.kinesthetic || '';
  return ''; // audio handled by the player
}

async function paintAudio(q, m){
  const box = document.getElementById('modbody');
  if(!box) return;
  if(m!=='audio'){ box.innerHTML = modalityBody(q,m) ? `<p>${modalityBody(q,m)}</p>` : '<p class="dim">coming soon for this question.</p>'; return; }
  box.innerHTML = `<button class="btn green" id="playQ">▶ play the question</button>
    <div class="dim" style="margin-top:8px" id="audioNote">narrated voice reads the question and every option aloud.</div>
    <audio id="qaudio" preload="none"></audio>`;
  document.getElementById('playQ').onclick = async ()=>{
    const a = document.getElementById('qaudio');
    const btn = document.getElementById('playQ');
    btn.disabled = true; btn.textContent = 'loading voice…';
    try{
      const r = await fetch(`/api/tts/${q.id}`);
      if(!r.ok) throw new Error('tts unavailable');
      const blob = await r.blob();
      a.src = URL.createObjectURL(blob);
      a.onended = ()=>{ btn.disabled=false; btn.textContent='▶ play again'; };
      await a.play();
      btn.textContent = '⏸ playing…';
    }catch(err){
      // browser speech fallback — still audio, still works offline
      document.getElementById('audioNote').textContent = 'voice engine busy — using your device voice.';
      try{
        const u = new SpeechSynthesisUtterance(q.q + '. options: ' + q.options.join('. '));
        u.onend = ()=>{ btn.disabled=false; btn.textContent='▶ play again'; };
        speechSynthesis.speak(u);
      }catch(e2){
        btn.disabled=false; btn.textContent='▶ play the question';
        document.getElementById('audioNote').textContent = 'audio unavailable on this device.';
      }
    }
  };
}

function paintQuiz(site){
  const qs = quizState.questions;
  const done = quizState.idx >= qs.length;
  if(done){
    const correct = qs.filter(q=>q.correct).length;
    const attempts = qs.reduce((a,q)=>a+q.attempts,0);
    confetti();
    const endChar = charById((profile&&profile.answers||{}).buddy);
    $app.innerHTML = `
      <div class="hero"><h1>🎉 lesson complete!</h1></div>
      <div class="done" style="max-width:560px;margin:0 auto">
        ${endChar?`<div style="font-size:56px;line-height:1">${endChar.emoji}</div>
        ${buddySay(endChar.emoji, correct===qs.length ? 'PERFECT lesson! you are on fire! 🔥' : 'you worked through every single one. proud of you! 💪')}`:''}
        <div class="big">${correct}/${qs.length}</div>
        <p class="dim" style="margin-top:6px">first-try correct: ${correct} · total tries: ${attempts}</p>
        <p style="margin-top:12px">every question was eventually understood. that's the point. no score is final here — "try again" always leads to understanding.</p>
        <div style="margin-top:18px;display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
          <button class="btn" id="againQuiz">🔄 try a fresh lesson</button>
          <a class="btn ghost" href="#" data-go="parent">📊 see the parent view</a>
        </div>
      </div>`;
    document.getElementById('againQuiz').onclick = async ()=>{
      const r = await fetch('/api/quiz'); quizState = await r.json(); paintQuiz(site);
    };
    return;
  }
  const q = qs[quizState.idx];
  const pct = Math.round((quizState.idx / qs.length) * 100);
  const myChar = charById((profile&&profile.answers||{}).buddy);
  if(!MODALITIES.some(m=>m.id===modality)) modality='visual';
  $app.innerHTML = `
    <div style="max-width:640px;margin:0 auto">
      <div class="quiz-top">
        <span class="dim">📝 question ${quizState.idx+1} of ${qs.length}</span>
        <span class="dim">${quizState.intensity?`📚 ${quizState.band} band · ${quizState.intensity} intensity · `:''}${myChar?`${myChar.emoji} ${myChar.name} is with you`:quizState.topic}</span>
      </div>
      <div class="progress"><div style="width:${pct}%"></div></div>
      ${myChar ? buddySay(myChar.emoji, quizState.idx===0 ? 'hi! i\'m '+myChar.name+'. we\'ll take this one step at a time. 😊' : pickA(['take your time — no rush here.','read it again slowly. i\'m right here.','you\'ve got this. pick the one that feels right.'])) : ''}
      <div class="card">
        <div class="qq">🤔 ${q.q}</div>
        <p class="dim">${q.context||''}</p>
        <div class="modtabs">
          ${MODALITIES.map(m=>`
            <button class="modtab ${modality===m.id?'sel':''}" data-mod="${m.id}" title="${m.label}">
              <span class="modicon">${m.icon}</span> ${m.label}
            </button>`).join('')}
        </div>
        <div class="modbody" id="modbody"></div>
        <div class="answers">
          ${q.options.map((o,i)=>`
            <button class="ans
              ${q.answeredThisRound && i===q.answerIndex ? (q.correct?'correct':'wrong') : ''}"
              data-i="${i}" ${q.correct || (q.answeredThisRound && !q.wrong) ? 'disabled':''}>${o}</button>`).join('')}
        </div>
        ${q.rewrites && q.rewrites.length ? `<div class="retry">
          <h4>🧩 let's try that another way</h4>
          <p class="dim">tap any explanation to hear it read aloud:</p>
          ${q.rewrites.map((txt,i)=>`
            <button type="button" class="method saybtn" data-say="${q.id}:rw:${i}" aria-label="play correction ${i+1}">
              <span class="sayicon" aria-hidden="true">🔊</span>
              <span class="saytext"><b>${(quizState.methodNames||[])[i]||('method '+(i+1))}</b><br><span style="font-size:14px">${txt}</span></span>
            </button>`).join('')}
          ${q.answeredThisRound && !q.correct && q.answerIndex>-1 && (q.options||[])[q.answerIndex]!==undefined ? `
            <button type="button" class="method saybtn whybtn" data-say="${q.id}:opt:${q.answerIndex}" aria-label="play why this option was wrong">
              <span class="sayicon" aria-hidden="true">🔊</span>
              <span class="saytext"><b>why "${q.options[q.answerIndex]}" isn't it</b><br><span style="font-size:14px">hear where that choice went wrong</span></span>
            </button>` : ''}
        </div>`:''}
      ${q.correct ? `<div class="yay">
          <h4>🎉 ${q.praise || pickA(PRAISE)}</h4>
          ${myChar ? buddySay(myChar.emoji, pickA(['we did it! next one?','see? your brain knew it.','high five! i knew you had this.']) ) : ''}
          <p class="dim">${pickA(CHEER)}</p></div>`:''}
      </div>
      <div style="margin-top:16px;text-align:center;display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
        ${q.correct
          ? `<button class="btn" id="nextQ">${quizState.idx+1>=qs.length?'🏁 finish lesson':'➡️ next question'}</button>`
          : q.answeredThisRound
            ? `<button class="btn green" id="retryQ">🔄 try again — you've got this</button>
               <button class="btn ghost" id="nextQ">skip for now</button>`
            : ''}
      </div>
    </div>`;
  $app.querySelectorAll('.modtab').forEach(b=>{
    b.onclick = ()=>{
      modality = b.dataset.mod;
      sessionStorage.setItem('btc_modality', modality);
      paintQuiz(site);
    };
  });
  paintAudio(q, modality);
  $app.querySelectorAll('.saybtn').forEach(b=>{
    b.onclick = ()=>playCorrection(b);
  });
  $app.querySelectorAll('.ans').forEach(b=>{
    b.onclick = ()=>{
      const i = +b.dataset.i;
      if(q.correct) return;
      fetch('/api/quiz/answer',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({questionId:q.id, grade:q.grade, choice:i, q:q.q, seen:(q.rewrites||[]).length})})
        .then(r=>r.json()).then(res=>{
          q.answeredThisRound = true;
          q.correct = !!res.correct; q.wrong = !res.correct;
          q.answerIndex = i; q.praise = res.praise;
          if(res.correct){ q.correctCount = (q.correctCount||0)+1; confetti(); }
          else { q.attempts = (q.attempts||0)+1; q.rewrites = [...(q.rewrites||[]), ...(res.rewrites||[])]; }
          paintQuiz(site);
        })
        .catch(()=>toast('network hiccup — tap your answer again.'));
    };
  });
  const nx = document.getElementById('nextQ');
  if(nx) nx.onclick = ()=>{ stopCorrectionAudio(); quizState.idx++; paintQuiz(site); };
  const rq = document.getElementById('retryQ');
  if(rq) rq.onclick = ()=>{ stopCorrectionAudio(); q.answeredThisRound = false; q.wrong = false; q.answerIndex = -1; paintQuiz(site); };
}

/* ---------- parent ---------- */
async function renderParent(site){
  const r = await fetch('/api/parent');
  const d = await r.json();
  $app.innerHTML = `
    <div class="hero"><h1>parent dashboard</h1>
      <p class="phi">visibility without pressure. see how learning is going this week.</p></div>
    <div class="stats">
      <div class="stat"><div class="n">${d.lessonsThisWeek}</div><div class="l">lessons this week</div></div>
      <div class="stat"><div class="n">${d.minutes}</div><div class="l">minutes learning</div></div>
      <div class="stat"><div class="n">${d.mastered}</div><div class="l">concepts mastered</div></div>
      <div class="stat"><div class="n">${d.tryAgainRate}%</div><div class="l">needed "try again"</div></div>
    </div>
    <div class="section">
      <h2>weekly progress</h2>
      <table>
        <tr><th>subject</th><th>lessons</th><th>status</th></tr>
        ${d.subjects.map(s=>`<tr><td>${s.name}</td><td>${s.lessons}</td>
          <td><span class="badge ${s.trend==='up'?'trend':'on'}">${s.trend==='up'?'▲ improving':s.status}</span></td></tr>`).join('')}
      </table>
    </div>
    <div class="section">
      <h2>insights</h2>
      <div class="grid">
        ${d.insights.map(i=>`<div class="card"><h3>${i.title}</h3><p>${i.body}</p></div>`).join('')}
      </div>
    </div>
    <div class="note">demo data — this is a test build. reports become real as learners use the platform. tiers from Plus upward include a monthly parent consultation.</div>
  `;
}

/* ---------- payment choice ---------- */
let payOrder = null;

async function renderPay(site){
  const t = site.tiers.find(x=>x.id===(payOrder&&payOrder.tier)) ||
            site.tiers.find(x=>x.id===(history.state&&history.state.tier));
  if(!t){ view='pricing'; return renderPricing(site); }
  if(t.price<=0){
    toast('the ' + t.name + ' tier is free — nothing to pay.');
    view='learner'; return renderLearner(site);
  }
  $app.innerHTML = `
    <div class="hero">
      <div class="tag">step 2 of 2 — pay securely</div>
      <h1>${t.name} — ${zar(t.price)}<small>/month</small></h1>
      <p class="phi">worldwide payments: pay by card/EFT (payfast) or crypto (any wallet, anywhere).</p>
    </div>
    <div class="card" style="max-width:640px;margin:0 auto">
      <div id="paychoice" style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px">
        <button class="btn" id="pfBtn">💳 payfast — card / instant EFT (ZAR)</button>
        <button class="btn green" id="cryptoBtn">🪙 crypto — ETH on Robinhood Chain</button>
      </div>
      <div id="paybody"><p class="dim">choose how you'd like to pay.</p></div>
    </div>`;
  document.getElementById('pfBtn').onclick = ()=>payfastFlow(t);
  document.getElementById('cryptoBtn').onclick = ()=>cryptoFlow(t);
}

async function payfastFlow(t){
  const body = document.getElementById('paybody');
  body.innerHTML = '<p class="dim">contacting payfast…</p>';
  try{
    const r = await fetch('/api/pay/intent',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({tier:t.id, method:'payfast', base_url:location.origin})});
    const d = await r.json();
    if(!r.ok){
      body.innerHTML = `<div class="note">💳 payfast is connected and ready on our side — it switches on the moment the merchant account keys go live. until then, crypto works worldwide today.</div>
        <button class="btn green" id="switchCrypto">🪙 pay with crypto instead</button>`;
      document.getElementById('switchCrypto').onclick = ()=>cryptoFlow(t);
      return;
    }
    // build and auto-submit the payfast hosted-checkout form
    const form = document.createElement('form');
    form.method = 'POST'; form.action = d.payfast.process_url;
    for(const [k,v] of Object.entries(d.payfast.fields)){
      const inp = document.createElement('input');
      inp.type='hidden'; inp.name=k; inp.value=v; form.appendChild(inp);
    }
    document.body.appendChild(form); form.submit();
  }catch(e){
    body.innerHTML = '<p class="dim">network hiccup — tap payfast again.</p>';
  }
}

async function cryptoFlow(t){
  const body = document.getElementById('paybody');
  body.innerHTML = '<p class="dim">getting a live ETH quote…</p>';
  try{
    const r = await fetch('/api/pay/intent',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({tier:t.id, method:'crypto'})});
    const d = await r.json();
    if(!r.ok){ body.innerHTML = `<p class="dim">${d.error||'could not start the order.'}</p>`; return; }
    payOrder = d;
    body.innerHTML = `
      <h3>🪙 pay ${d.eth_amount} ETH <span class="dim">(${zar(d.amount_zar)})</span></h3>
      <p class="dim">network: ${d.chain} (chain id ${d.chain_id}). send native ETH only — tokens sent on other chains cannot be recovered.</p>
      <label style="font-size:13px">send exactly this to the treasury:</label>
      <div style="display:flex;gap:8px;align-items:center;margin:8px 0 14px;flex-wrap:wrap">
        <input readonly value="${d.treasury}" id="treas" style="flex:1;min-width:200px;font-size:13px">
        <button class="btn ghost" id="copyTreas">📋 copy</button>
      </div>
      <label style="font-size:13px">amount (ETH):</label>
      <div style="display:flex;gap:8px;align-items:center;margin:8px 0 14px;flex-wrap:wrap">
        <input readonly value="${d.eth_amount}" id="ethamt" style="flex:1;min-width:120px">
        <button class="btn ghost" id="copyAmt">📋 copy</button>
      </div>
      <label style="font-size:13px">after paying, paste your transaction hash:</label>
      <input id="txhash" placeholder="0x… the tx hash from your wallet" style="margin:8px 0 12px">
      <button class="btn green" id="confirmTx" style="width:100%">✅ verify my payment</button>
      <p class="dim" style="margin-top:10px;font-size:12px">for every crypto payment we record the exact date-time, the ETH amount, and the ETH price at that moment — your SARS record. it is stored against the payment permanently.</p>
      <div id="payresult"></div>`;
    document.getElementById('copyTreas').onclick = ()=>{ navigator.clipboard.writeText(d.treasury); toast('treasury address copied 📋'); };
    document.getElementById('copyAmt').onclick = ()=>{ navigator.clipboard.writeText(String(d.eth_amount)); toast('amount copied 📋'); };
    document.getElementById('confirmTx').onclick = async ()=>{
      const hash = document.getElementById('txhash').value.trim();
      const res = document.getElementById('payresult');
      if(!hash.startsWith('0x') || hash.length < 20){ toast('paste the full transaction hash from your wallet first.'); return; }
      res.innerHTML = '<p class="dim">reading the chain…</p>';
      try{
        const cr = await fetch('/api/pay/confirm',{method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify({order_id:d.id, tx_hash:hash})});
        const cd = await cr.json();
        if(!cr.ok){ res.innerHTML = `<div class="note">⚠️ ${cd.error}</div>`; return; }
        const s = cd.sars || {};
        res.innerHTML = `
          <div class="yay"><h4>🎉 payment verified — welcome to ${t.name}!</h4>
          <p class="dim">sars record saved for this payment:</p>
          <table style="margin-top:8px">
            <tr><td class="dim">date & time (SAST)</td><td>${(s.paid_at||'').replace('T',' ').slice(0,19)}</td></tr>
            <tr><td class="dim">crypto received</td><td><b>${s.crypto_amount} ETH</b></td></tr>
            <tr><td class="dim">ETH price at payment</td><td>$${s.eth_price_usd_at_payment} (R${s.zar_per_eth_at_payment}/ETH)</td></tr>
            <tr><td class="dim">value at payment</td><td><b>R${Math.round(s.value_zar_at_payment*100)/100}</b></td></tr>
            <tr><td class="dim">tx</td><td style="font-size:11px">${cd.tx_hash}</td></tr>
          </table></div>
          <div style="margin-top:14px;display:flex;gap:10px;flex-wrap:wrap">
            <a class="btn green" href="#" data-go="learner">🎒 build the learner profile</a>
          </div>`;
        confetti();
      }catch(e2){
        res.innerHTML = '<p class="dim">network hiccup — tap verify again.</p>';
      }
    };
  }catch(e){
    body.innerHTML = '<p class="dim">network hiccup — tap crypto again.</p>';
  }
}

/* ---------- pricing ---------- */
function tierCard(x, site){
  return `
    <div class="card" style="${x.popular?'border-color:var(--brand2);box-shadow:0 0 30px rgba(34,211,167,.12)':''}">
      ${x.popular?'<span class="pill pop">most popular</span>':x.id==='discover'?'<span class="pill grey">free forever</span>':''}
      <h3 style="margin-top:8px">${x.name}</h3>
      <div class="price">${zar(x.price)}<small>/month</small></div>
      <p>${x.blurb}</p>
      <ul class="feat">${x.features.slice(0,5).map(f=>`<li>${f}</li>`).join('')}${x.features.length>5?`<li class="dim">+ ${x.features.length-5} more — see full tier</li>`:''}</ul>
      <div style="margin-top:14px;display:flex;gap:8px;flex-wrap:wrap">
        <a class="btn ${x.popular?'':'ghost'}" href="#" data-go="tiers" data-tier="${x.id}">full details</a>
        <a class="btn ${x.popular?'green':''}" href="#" data-go="learner" data-pick="${x.id}">choose ${x.name}</a>
      </div>
    </div>`;
}

function renderPricing(site){
  const t = site.tiers;
  $app.innerHTML = `
    <div class="hero"><h1>simple monthly tiers</h1>
      <p class="phi">start free. scale support when you need it. cancel anytime.</p></div>
    <div class="grid">
      ${t.map(x=>tierCard(x, site)).join('')}
    </div>
    <div class="section">
      <h2>beyond the tiers</h2>
      <table>
        <tr><th>revenue stream</th><th>pricing</th></tr>
        ${site.revenueStreams.map(r=>`<tr><td>${r.stream}</td><td>${r.zar}</td></tr>`).join('')}
      </table>
    </div>
    <div class="note">demo pricing for a test build — final pricing is the holder's call. sponsor-a-learner: a company sponsors a learner at R599/month, creating the social-impact component.</div>
  `;
}

/* ---------- tier detail pages ---------- */
function renderTier(site){
  const x = site.tiers.find(t=>t.id===view)
    || site.tiers.find(t=>t.id===(history.state&&history.state.tier));
  if(!x){ view='pricing'; return renderPricing(site); }
  const idx = site.tiers.indexOf(x);
  const prev = site.tiers[idx-1], next = site.tiers[idx+1];
  $app.innerHTML = `
    <div class="hero">
      <div class="tag">tier ${idx+1} of ${site.tiers.length}</div>
      <h1>${x.name}</h1>
      <div class="price" style="font-size:44px">${zar(x.price)}<small>/month</small></div>
      <p class="phi">${x.blurb}</p>
      <div class="cta-row">
        <a class="btn green" href="#" data-go="learner" data-pick="${x.id}">choose ${x.name}</a>
        <a class="btn ghost" href="#" data-go="pricing">compare all tiers</a>
      </div>
    </div>
    <div class="card" style="max-width:640px;margin:0 auto">
      <h3>everything in ${x.name}</h3>
      <ul class="feat">${x.features.map(f=>`<li>${f}</li>`).join('')}</ul>
      ${next?`<div style="margin-top:16px" class="dim">need more? <a href="#" data-go="tiers" data-tier="${next.id}" style="color:var(--brand)">${next.name}</a> adds: ${next.features.filter(f=>!x.features.includes(f)).slice(0,3).join(', ')}…</div>`:''}
    </div>
    <div style="margin-top:16px;display:flex;justify-content:space-between;max-width:640px;margin-left:auto;margin-right:auto">
      ${prev?`<a class="btn ghost" href="#" data-go="tiers" data-tier="${prev.id}">← ${prev.name}</a>`:'<span></span>'}
      ${next?`<a class="btn ghost" href="#" data-go="tiers" data-tier="${next.id}">${next.name} →</a>`:'<span></span>'}
    </div>
    <div class="note">demo pricing for a test build. cancel anytime. every tier includes the 3-way lessons: see it, hear it, do it.</div>
  `;
}

/* ---------- offerings (full subject catalogue) ---------- */
const CAT_META = {
  academic: {label:'academic subjects', blurb:'the school subjects, taught the adaptive way — every lesson in all three modalities.'},
  personalDevelopment: {label:'personal development', blurb:'the stuff school skips: mindset, confidence, emotional regulation.'},
  financialEducation: {label:'financial education', blurb:'money skills for life — budgeting, saving, debt, building something of your own.'},
  futureSkills: {label:'future skills', blurb:'what the next decade actually rewards: AI literacy, digital skills, selling, leading.'},
};

function renderOfferings(site){
  const s = site.subjects;
  const draft = loadDraft();
  const wantsHelp = draft.struggle || [];
  $app.innerHTML = `
    <div class="hero"><h1>everything we offer</h1>
      <p class="phi">an alternative education ecosystem, not just lessons.</p></div>
    ${Object.keys(CAT_META).map(key=>{
      const meta = CAT_META[key];
      const arr = s[key] || [];
      return `
      <div class="section" id="cat-${key}">
        <h2>${meta.label}</h2>
        <p class="sub">${meta.blurb}</p>
        <div class="grid">
          ${arr.map(name=>{
            const flagged = wantsHelp.includes(name);
            return `<div class="card" ${flagged?'style="border-color:var(--brand2)"':''}>
              <h3>${name}</h3>
              <p class="dim">${flagged?'your profile flagged this — the adaptive loop gives it extra attention.':'taught with visual, audio and hands-on paths in every lesson.'}</p>
            </div>`;}).join('')}
        </div>
      </div>`;
    }).join('')}
    <div class="section">
      <h2>how subjects are taught</h2>
      <div class="grid">
        <div class="card"><h3>👁 see it</h3><p>mind-picture walkthroughs on every question.</p></div>
        <div class="card"><h3>🎧 hear it</h3><p>the whole question and options read aloud — real narrated voice.</p></div>
        <div class="card"><h3>✋ do it</h3><p>hands-on activities: paper folds, coins, acting it out.</p></div>
      </div>
    </div>
    <div class="cta-row" style="text-align:center">
      <a class="btn" href="#" data-go="learner">🎒 match these to my learner</a>
      <a class="btn green" href="#" data-go="pricing">💰 see tier pricing</a>
    </div>
    <div class="note">demo catalogue for a test build — subject availability grows with each phase.</div>
  `;
}

/* ---------- routing ---------- */
function go(v, opts){
  if(v==='quiz' && !quizState) view='quiz'; else view=v;
  if(opts && opts.tier){ history.replaceState({tier:opts.tier}, ''); }
  render();
}
document.addEventListener('click', e=>{
  const a = e.target.closest('[data-go]');
  if(!a) return;
  e.preventDefault();
  // tier CTAs: priced tiers go to payment, free tier goes to the profile
  const pickId = a.dataset.pick;
  if(pickId){
    loadSite().then(site=>{
      chosenTier = site.tiers.find(t=>t.id===pickId) || null;
      sessionStorage.setItem('btc_tier', JSON.stringify(chosenTier));
      if(chosenTier && chosenTier.price>0){
        history.replaceState({tier:pickId}, '');
        view='pay';
        render();
      } else {
        go(a.dataset.go);
      }
    });
    return;
  }
  go(a.dataset.go, {tier:a.dataset.tier});
});
document.querySelectorAll('.navlink').forEach(a=>{
  a.onclick = e=>{ e.preventDefault(); view=a.dataset.view; if(a.dataset.view==='quiz'&&!quizState) view='quiz'; render(); };
});
// restore chosen tier on reload
try { chosenTier = JSON.parse(sessionStorage.getItem('btc_tier') || 'null'); } catch(e){ chosenTier = null; }
// restore accent colour: saved profile wins, session fallback otherwise
try { applyAccent((profile&&profile.answers&&profile.answers.accent) || sessionStorage.getItem('btc_accent')); } catch(e){}
render();
