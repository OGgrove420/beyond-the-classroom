// parse-check the front-end files and verify the correction-button wiring textually
const fs = require('fs'), path = '/opt/data/learning-app/public/';
let fail = 0;
const check = (n, c) => { console.log((c?'PASS ':'FAIL ') + n); if(!c) fail=1; };

for (const f of ['app.js','auth.js','vendor/supabase.umd.js']) {
  const src = fs.readFileSync(path+f,'utf8');
  try { new Function(src); check(`${f} parses`, true); }
  catch(e){ check(`${f} parses (${e.message})`, false); }
}

const app = fs.readFileSync(path+'app.js','utf8');
// the wrong-answer box must render <button> elements with data-say keys
check('rewrites render as buttons', /class="method saybtn" data-say="\$\{q\.id\}:rw:\$\{i\}"/.test(app));
check('why-note button included', /data-say="\$\{q\.id\}:opt:\$\{q\.answerIndex\}"/.test(app));
check('tap handler wired', /\$app\.querySelectorAll\('\.saybtn'\)\.forEach\(b=>\{\s*b\.onclick = \(\)=>playCorrection\(b\)/.test(app));
check('audio stops on nav', /stopCorrectionAudio\(\); quizState\.idx\+\+/.test(app));
// auth.js must create the client from /api/auth/config values
const auth = fs.readFileSync(path+'auth.js','utf8');
check('client from config', /createClient\(authCfg\.url, authCfg\.anonKey/.test(auth));
check('guest path present', /continue as guest/.test(auth));
const html = fs.readFileSync(path+'index.html','utf8');
check('umd loaded before auth.js', html.indexOf('supabase.umd.js') < html.indexOf('auth.js') && html.indexOf('auth.js') > html.indexOf('app.js'));
process.exit(fail);
