/* Beyond The Classroom — front-end (vanilla js, no build step) */
const $app = document.getElementById('app');
let view = 'home';
let profile = JSON.parse(sessionStorage.getItem('btc_profile') || 'null');
let quizState = null;

function toast(msg){
  let t = document.querySelector('.toast');
  if(!t){ t = document.createElement('div'); t.className='toast'; document.body.appendChild(t); }
  t.textContent = msg; t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'), 2600);
}
const zar = n => n === 0 ? 'R0' : 'R' + n.toLocaleString('en-ZA');

async function render(){
  const site = await loadSite();
  if(view==='home') renderHome(site);
  else if(view==='learner') renderLearner(site);
  else if(view==='quiz') renderQuiz(site);
  else if(view==='parent') renderParent(site);
  else if(view==='pricing') renderPricing(site);
  document.querySelectorAll('.navlink').forEach(a=>a.classList.toggle('active', a.dataset.view===view));
  window.scrollTo(0,0);
}

/* ---------- home ---------- */
function renderHome(site){
  const s = site.subjects;
  const cat = (title, arr) => `
    <div class="card"><h3>${title}</h3>
      <div class="chips">${arr.map(x=>`<span class="chip">${x}</span>`).join('')}</div>
    </div>`;
  $app.innerHTML = `
    <div class="hero">
      <h1>${site.brand.tagline}</h1>
      <div class="tag">${site.brand.name}</div>
      <p class="phi">${site.brand.philosophy}</p>
      <div class="cta-row">
        <a class="btn" href="#" data-go="learner">build a learner profile</a>
        <a class="btn green" href="#" data-go="quiz">try a lesson</a>
      </div>
    </div>
    <div class="grid">
      <div class="card"><h3>learn at your own pace</h3><p>repeat lessons without embarrassment. watch as many times as needed.</p></div>
      <div class="card"><h3>short lessons</h3><p>shorter lessons rather than long classroom sessions. work when you have the time.</p></div>
      <div class="card"><h3>many ways in</h3><p>video, audio, visuals and practical activities. when something doesn't land, we try another way.</p></div>
      <div class="card"><h3>no shame learning</h3><p>never "fail". always "try again". "i haven't understood it yet" — not "i'm stupid".</p></div>
    </div>
    <div class="section">
      <h2>what a learner can do here</h2>
      <div class="grid">
        ${["learn at their own pace","repeat lessons freely","get extra explanations","complete work when they have time","follow a personalised pathway","track their own progress","get tutor support when required","learn from home — no daily travel costs"]
          .map(x=>`<div class="card"><p>${x}</p></div>`).join('')}
      </div>
    </div>
    <div class="section">
      <h2>beyond school subjects</h2>
      <p class="sub">an alternative education ecosystem, not just lessons.</p>
      <div class="grid">
        ${cat('academic', s.academic)}
        ${cat('personal development', s.personalDevelopment)}
        ${cat('financial education', s.financialEducation)}
        ${cat('future skills', s.futureSkills)}
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
  {k:'grade', q:'what grade are you in?', type:'text', ph:'e.g. Grade 6'},
  {k:'enjoy', q:'which subjects do you enjoy?', opts:['Mathematics','English','Science','Technology','Business Studies','Art','History','Geography']},
  {k:'struggle', q:'which subjects do you struggle with?', opts:['Mathematics','English','Science','Technology','Business Studies','Reading','Writing','Exams']},
  {k:'style', q:'how do you prefer learning?', opts:['Watching videos','Listening','Reading','Doing practical activities']},
  {k:'focus', q:'how long can you comfortably concentrate?', opts:['5–10 minutes','10–20 minutes','20–40 minutes','40+ minutes']},
  {k:'hard', q:'what normally makes learning difficult?', opts:['Going too fast','Too much at once','Not enough explanation','Getting rushed','Fear of getting it wrong','Nothing specific']},
  {k:'strength', q:'what are you good at?', type:'text', ph:'e.g. explaining things to friends, building things, drawing'},
  {k:'goal', q:'what do you want to get better at this year?', type:'text', ph:'e.g. maths, confidence, reading'},
];

function renderLearner(site){
  if(profile){ return renderProfileCard(site); }
  $app.innerHTML = `
    <div class="hero"><h1>build your learner profile</h1>
      <p class="phi">we don't just ask "what grade are you in?". we ask how you learn — so the platform can adapt to you.</p></div>
    <div class="card" style="max-width:640px;margin:22px auto 0">
      ${PQUESTIONS.map((q,i)=>`
        <div class="q">
          <label>${i+1}. ${q.q}</label>
          ${q.opts
            ? `<div class="opts" data-k="${q.k}">${q.opts.map(o=>`<button class="opt" data-v="${o}">${o}</button>`).join('')}</div>`
            : `<input type="text" id="in_${q.k}" placeholder="${q.ph||''}">`}
        </div>`).join('')}
      <div style="margin-top:18px;display:flex;gap:10px;flex-wrap:wrap">
        <button class="btn" id="saveProfile">create my profile</button>
        <button class="btn ghost" id="skipProfile">skip for now</button>
      </div>
    </div>`;
  $app.querySelectorAll('.opts').forEach(g=>{
    g.addEventListener('click', e=>{
      const b = e.target.closest('.opt'); if(!b) return;
      g.querySelectorAll('.opt').forEach(x=>x.classList.remove('sel'));
      b.classList.add('sel');
    });
  });
  document.getElementById('skipProfile').onclick = ()=>{ go('quiz'); };
  document.getElementById('saveProfile').onclick = ()=>{
    const p = {answers:{}, created:new Date().toISOString()};
    for(const q of PQUESTIONS){
      if(q.opts){
        const sel = $app.querySelector(`.opts[data-k="${q.k}"] .opt.sel`);
        p.answers[q.k] = sel ? sel.dataset.v : null;
      } else {
        p.answers[q.k] = (document.getElementById('in_'+q.k)||{}).value || null;
      }
    }
    fetch('/api/profile',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)})
      .then(r=>r.json()).then(res=>{
        p.id = res.id;
        profile = p;
        sessionStorage.setItem('btc_profile', JSON.stringify(p));
        toast('profile saved');
        renderProfileCard(site);
      });
  };
}

async function renderProfileCard(site){
  const r = await fetch(profile.id ? `/api/profile?id=${encodeURIComponent(profile.id)}` : '/api/profile');
  const data = await r.json();
  $app.innerHTML = `
    <div class="hero"><h1>learning profile</h1></div>
    <div class="card" style="max-width:640px;margin:0 auto">
      <h3>here's what we learned about how you learn</h3>
      <div class="profile-out">${data.summary}</div>
      <div class="chips" style="margin-top:14px">
        ${data.tags.map(t=>`<span class="chip">${t}</span>`).join('')}
      </div>
      <div style="margin-top:18px;display:flex;gap:10px;flex-wrap:wrap">
        <a class="btn green" href="#" data-go="quiz">start a lesson</a>
        <button class="btn ghost" id="newProfile">start over</button>
      </div>
    </div>`;
  document.getElementById('newProfile').onclick = ()=>{
    profile = null; sessionStorage.removeItem('btc_profile');
    fetch('/api/profile',{method:'DELETE'}).catch(()=>{});
    render();
  };
}

/* ---------- quiz ---------- */
async function renderQuiz(site){
  if(!quizState){
    const r = await fetch('/api/quiz');
    quizState = await r.json();
    quizState.methodNames = site.adaptiveMethods.map(m=>`method ${m.n} — ${m.label}`);
  }
  paintQuiz(site);
}

function paintQuiz(site){
  const qs = quizState.questions;
  const done = quizState.idx >= qs.length;
  if(done){
    const correct = qs.filter(q=>q.correct).length;
    const attempts = qs.reduce((a,q)=>a+q.attempts,0);
    $app.innerHTML = `
      <div class="hero"><h1>lesson complete</h1></div>
      <div class="done" style="max-width:560px;margin:0 auto">
        <div class="big">${correct}/${qs.length}</div>
        <p class="dim" style="margin-top:6px">first-try correct: ${correct} · total tries: ${attempts}</p>
        <p style="margin-top:12px">every question was eventually understood. that's the point. no score is final here — "try again" always leads to understanding.</p>
        <div style="margin-top:18px;display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
          <button class="btn" id="againQuiz">try a fresh lesson</button>
          <a class="btn ghost" href="#" data-go="parent">see the parent view</a>
        </div>
      </div>`;
    document.getElementById('againQuiz').onclick = async ()=>{
      const r = await fetch('/api/quiz'); quizState = await r.json(); paintQuiz(site);
    };
    return;
  }
  const q = qs[quizState.idx];
  const pct = Math.round((quizState.idx / qs.length) * 100);
  $app.innerHTML = `
    <div style="max-width:640px;margin:0 auto">
      <div class="quiz-top">
        <span class="dim">question ${quizState.idx+1} of ${qs.length}</span>
        <span class="dim">${quizState.topic}</span>
      </div>
      <div class="progress"><div style="width:${pct}%"></div></div>
      <div class="card">
        <div class="qq">${q.q}</div>
        <p class="dim">${q.context||''}</p>
        <div class="answers">
          ${q.options.map((o,i)=>`
            <button class="ans
              ${q.answeredThisRound && i===q.answerIndex ? (q.correct?'correct':'wrong') : ''}"
              data-i="${i}" ${q.correct || (q.answeredThisRound && !q.wrong) ? 'disabled':''}>${o}</button>`).join('')}
        </div>
        ${q.rewrites && q.rewrites.length ? `<div class="retry">
          <h4>let's try that another way</h4>
          <p class="dim">you haven't mastered this concept yet. that's okay. here it is, explained differently:</p>
          ${q.rewrites.map((txt,i)=>`
            <div class="method"><b>${(quizState.methodNames||[])[i]||('method '+(i+1))}</b><br><span style="font-size:14px">${txt}</span></div>`).join('')}
        </div>`:''}
        ${q.correct ? `<div class="retry" style="border-color:var(--brand2);background:rgba(34,211,167,.07)">
          <h4 style="color:var(--brand2)">you've got it</h4><p class="dim">${q.praise||'nice work. on to the next one.'}</p></div>`:''}
      </div>
      <div style="margin-top:16px;text-align:center;display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
        ${q.correct
          ? `<button class="btn" id="nextQ">${quizState.idx+1>=qs.length?'finish lesson':'next question'}</button>`
          : q.answeredThisRound
            ? `<button class="btn green" id="retryQ">try again — you've got this</button>
               <button class="btn ghost" id="nextQ">skip for now</button>`
            : ''}
      </div>
    </div>`;
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
          if(res.correct) q.correctCount = (q.correctCount||0)+1;
          else { q.attempts = (q.attempts||0)+1; q.rewrites = [...(q.rewrites||[]), ...(res.rewrites||[])]; }
          paintQuiz(site);
        });
    };
  });
  const nx = document.getElementById('nextQ');
  if(nx) nx.onclick = ()=>{ quizState.idx++; paintQuiz(site); };
  const rq = document.getElementById('retryQ');
  if(rq) rq.onclick = ()=>{ q.answeredThisRound = false; q.wrong = false; q.answerIndex = -1; paintQuiz(site); };
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
    <div class="note">demo data — this is a test build. reports become real as learners use the platform. tier tiers include a monthly parent consultation from Plus upward.</div>
  `;
}

/* ---------- pricing ---------- */
function renderPricing(site){
  const t = site.tiers;
  $app.innerHTML = `
    <div class="hero"><h1>simple monthly tiers</h1>
      <p class="phi">start free. scale support when you need it. cancel anytime.</p></div>
    <div class="grid">
      ${t.map(x=>`
        <div class="card" style="${x.popular?'border-color:var(--brand2);box-shadow:0 0 30px rgba(34,211,167,.12)':''}">
          ${x.popular?'<span class="pill pop">most popular</span>':x.id==='discover'?'<span class="pill grey">free forever</span>':''}
          <h3 style="margin-top:8px">${x.name}</h3>
          <div class="price">${zar(x.price)}<small>/month</small></div>
          <p>${x.blurb}</p>
          <ul class="feat">${x.features.map(f=>`<li>${f}</li>`).join('')}</ul>
          <div style="margin-top:14px"><a class="btn ${x.popular?'':'ghost'}" href="#" data-go="learner">choose ${x.name}</a></div>
        </div>`).join('')}
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

/* ---------- routing ---------- */
function go(v){
  if(v==='quiz' && !quizState) view='quiz'; else view=v;
  render();
}
document.addEventListener('click', e=>{
  const a = e.target.closest('[data-go]');
  if(a){ e.preventDefault(); go(a.dataset.go); }
});
document.querySelectorAll('.navlink').forEach(a=>{
  a.onclick = e=>{ e.preventDefault(); view=a.dataset.view; if(a.dataset.view==='quiz'&&!quizState) view='quiz'; render(); };
});
render();
