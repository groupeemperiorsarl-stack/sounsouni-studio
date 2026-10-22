// Le TECHNICIEN de Sounsouni Studio : une IA qui cherche et répare les problèmes en boucle, sur une machine GitHub (le téléphone peut être fermé).
// Issa lui écrit sur la demande « 🛠 Technicien » (étiquette technicien) ; il répond sur la même demande.
// Il apprend : leçons dans technicien/carnet.md (lu par toutes les IA du studio), journal de chaque recherche dans technicien/journal/,
// et notes des modèles d'IA dans technicien/modeles.json (le meilleur selon l'usage passe en premier).
// Clés : secrets GitHub seulement (GEMINI_API_KEY, GROQ_API_KEY, CEREBRAS_API_KEY, OPENROUTER_API_KEY). Jamais dans les fichiers.
import fs from 'fs';
import { execFileSync } from 'child_process';

const { ISSUE, GITHUB_REPOSITORY: REPO, GH_TOKEN, MESSAGE_ID } = process.env;
const T0 = Date.now(), MAX_ETAPES = +(process.env.MAX_ETAPES || 40), MAX_MIN = +(process.env.MAX_MIN || 45);
const dodo = ms => new Promise(r => setTimeout(r, ms));
const log = t => console.log(new Date().toISOString().slice(11, 19), t);
const sh = (cmd, args, o = {}) => execFileSync(cmd, args, { encoding: 'utf8', maxBuffer: 64 << 20, ...o });
const court = (t, n = 6000) => { t = String(t ?? ''); return t.length > n ? t.slice(0, n * 0.4) + '\n…(coupé)…\n' + t.slice(-n * 0.6) : t; };

async function gh(chemin, o = {}) {
  const url = chemin.startsWith('http') ? chemin : 'https://api.github.com' + (chemin.startsWith('/repos') ? '' : '/repos/' + REPO) + chemin;
  for (let i = 0; i < 3; i++) {
    const r = await fetch(url, { ...o, headers: { Authorization: 'Bearer ' + GH_TOKEN, Accept: o.accept || 'application/vnd.github+json', 'Content-Type': 'application/json' } });
    if (r.status >= 500 && i < 2) { await dodo(3000); continue; }
    if (!r.ok) throw new Error('GitHub ' + r.status + ' ' + (await r.text()).slice(0, 200));
    if (o.texte) return r.text();
    if (o.brut) return Buffer.from(await r.arrayBuffer());
    return r.status === 204 || r.status === 202 ? null : r.json().catch(() => null);
  }
}
const minutes = (a, b) => Math.round(((b ? new Date(b) : new Date()) - new Date(a)) / 60000);

// ---------------- mémoire : carnet, modèles ----------------
const CARNET = 'technicien/carnet.md', MODELES = 'technicien/modeles.json';
let carnet = fs.existsSync(CARNET) ? fs.readFileSync(CARNET, 'utf8') : '# Carnet du studio\n';
let stats = {}; try { stats = JSON.parse(fs.readFileSync(MODELES, 'utf8')); } catch (e) {}
const nouvellesLecons = [];
function ajouterLecon(theme, texte, qui) {
  theme = (theme || 'fabrication').toLowerCase().replace(/[^a-z-]/g, '') || 'fabrication';
  texte = String(texte).replace(/\s+/g, ' ').trim().slice(0, 400); if (texte.length < 15) return false;
  const deja = carnet.toLowerCase().includes(texte.toLowerCase().slice(0, 60)); if (deja) return false;
  const ligne = '- ' + new Date().toISOString().slice(0, 10) + ' · ' + qui + ' · ' + texte;
  const re = new RegExp('^## ' + theme + '\\s*$', 'm');
  if (re.test(carnet)) { const L = carnet.split('\n'), i = L.findIndex(l => re.test(l)); let j = i + 1; while (j < L.length && !L[j].startsWith('## ')) j++;
    while (j > i + 1 && !L[j - 1].trim()) j--; L.splice(j, 0, ligne); carnet = L.join('\n'); }
  else carnet = carnet.replace(/\n*$/, '\n\n## ' + theme + '\n' + ligne + '\n');
  nouvellesLecons.push(theme + ' : ' + texte); return true;
}

// ---------------- les IA (format OpenAI pour toutes, Gemini par sa porte compatible) ----------------
async function listeGemini(k) {   // les modèles gratuits changent souvent : on prend les « flash » disponibles, du plus récent au plus ancien
  let v = [];
  try { const j = await (await fetch('https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000', { headers: { 'x-goog-api-key': k } })).json();
    v = (j.models || []).filter(x => (x.supportedGenerationMethods || []).includes('generateContent') && /flash/.test(x.name) && !/lite|image|tts|live|audio|embed|exp|vision|thinking/.test(x.name)).map(x => x.name.replace('models/', '')); } catch (e) {}
  const num = m => { const x = m.match(/gemini-(\d+(?:\.\d+)?)/); return x ? +x[1] - (/preview/.test(m) ? 0.01 : 0) : (/latest/.test(m) ? 2.95 : 0); };
  v.sort((a, b) => num(b) - num(a));
  return v.length ? v.slice(0, 6) : ['gemini-flash-latest', 'gemini-3-flash-preview'];
}
async function fournisseurs() {
  const P = [];
  const g = process.env.GEMINI_API_KEY; if (g) for (const m of await listeGemini(g)) P.push({ nom: 'Gemini ' + m, url: 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions', cle: g, modele: m, gemini: true });
  if (process.env.CEREBRAS_API_KEY) P.push({ nom: 'Cerebras gpt-oss-120b', url: 'https://api.cerebras.ai/v1/chat/completions', cle: process.env.CEREBRAS_API_KEY, modele: 'gpt-oss-120b', x: { reasoning_effort: 'medium' } });
  if (process.env.GROQ_API_KEY) P.push({ nom: 'Groq gpt-oss-120b', url: 'https://api.groq.com/openai/v1/chat/completions', cle: process.env.GROQ_API_KEY, modele: 'openai/gpt-oss-120b', x: { reasoning_effort: 'medium' } });
  if (process.env.OPENROUTER_API_KEY) P.push({ nom: 'OpenRouter gpt-oss-120b', url: 'https://openrouter.ai/api/v1/chat/completions', cle: process.env.OPENROUTER_API_KEY, modele: 'openai/gpt-oss-120b:free' });
  // ordre selon l'usage : chaque modèle garde sa note (recherches réussies, 👍 / 👎 d'Issa) ; un modèle jamais essayé garde sa place d'origine
  const note = p => { const s = stats[p.nom]; if (!s) return null; return (s.reussies + 2 * s.pouces_haut + 1) / (s.sessions + 2 * (s.pouces_haut + s.pouces_bas) + 2); };
  return P.map((p, i) => ({ p, i, n: note(p) })).sort((a, b) => (a.n == null || b.n == null) ? a.i - b.i : (b.n - a.n) || (a.i - b.i)).map(x => x.p);
}
let FOURN = [], actuel = 0;
const nettoyerPour = (p, msgs) => msgs.map(m => { const c = { role: m.role, content: m.content ?? '' };
  if (m.tool_calls) c.tool_calls = m.tool_calls.map(t => p.gemini ? t : { id: t.id, type: 'function', function: t.function });
  if (m.tool_call_id) { c.tool_call_id = m.tool_call_id; if (!p.gemini) c.name = m.name; }
  if (m.role === 'assistant' && m.tool_calls && !m.content) c.content = p.gemini ? null : '';
  return c; });
async function penser(msgs, outils) {   // un tour de l'IA ; en cas de panne on passe à la suivante (la conversation suit)
  let err = '';
  for (let tour = 0; tour < 3; tour++) { for (let k = 0; k < FOURN.length; k++) {
    const p = FOURN[(actuel + k) % FOURN.length];
    try {
      const corps = { model: p.modele, messages: nettoyerPour(p, msgs), temperature: 0.3, ...(outils ? { tools: outils, tool_choice: 'auto' } : {}), ...(p.x || {}) };
      const r = await fetch(p.url, { method: 'POST', headers: { Authorization: 'Bearer ' + p.cle, 'Content-Type': 'application/json' }, body: JSON.stringify(corps), signal: AbortSignal.timeout(240000) });
      if (r.status === 429) { const b = await r.text(); err = p.nom + ' : 429 ' + b.slice(0, 120); const mm = b.match(/try again in\s*(?:(\d+)m)?\s*([\d.]+)s/i);
        if (mm && !/per day|TPD|RPD/i.test(b) && +(mm[1] || 0) < 2) { const w = Math.ceil(+(mm[1] || 0) * 60 + parseFloat(mm[2])) + 2; log(p.nom + ' attend ' + w + ' s'); await dodo(w * 1000); k--; continue; }
        log(err); continue; }
      if (!r.ok) { err = p.nom + ' : ' + r.status + ' ' + (await r.text()).slice(0, 200); log(err); continue; }
      const d = await r.json(), m = d.choices?.[0]?.message;
      if (!m || (!m.content && !(m.tool_calls || []).length)) { err = p.nom + ' : réponse vide'; log(err); continue; }
      if (actuel !== (actuel + k) % FOURN.length) log('→ ' + p.nom + ' prend le relais');
      actuel = (actuel + k) % FOURN.length; return { m, p };
    } catch (e) { err = p.nom + ' : ' + e.message; log(err); }
    }
    if (tour < 2) { log('toutes les IA sont occupées, nouvel essai dans 20 s'); await dodo(20000); }
  }
  throw new Error('aucune IA ne répond (' + err + ')');
}

// ---------------- les outils du technicien ----------------
const NOMS = {};   // nom de fabrication par id
async function etat({ nombre = 25 } = {}) {
  const j = await gh('/actions/runs?per_page=' + Math.min(50, Math.max(15, nombre) + 3));
  const lignes = [];
  for (const r of j.workflow_runs.filter(r => !(String(r.id) === process.env.GITHUB_RUN_ID)).slice(0, Math.max(15, nombre))) {
    NOMS[r.id] = r.name;
    let l = `#${r.id} · ${r.name} · ${r.status === 'completed' ? (r.conclusion === 'success' ? 'réussie' : r.conclusion === 'cancelled' ? 'arrêtée' : r.conclusion === 'skipped' ? 'ignorée' : 'RATÉE') : r.status === 'in_progress' ? 'EN COURS' : 'en attente'} · lancée ${r.created_at.slice(5, 16).replace('T', ' ')} UTC · ${minutes(r.run_started_at || r.created_at, r.status === 'completed' ? r.updated_at : null)} min${r.display_title && r.display_title !== r.name ? ' · « ' + r.display_title.slice(0, 60) + ' »' : ''}`;
    if (r.status !== 'completed') try {
      const jb = await gh('/actions/runs/' + r.id + '/jobs?per_page=100');
      const enc = jb.jobs.filter(x => x.status === 'in_progress'), att = jb.jobs.filter(x => x.status === 'queued').length, ok = jb.jobs.filter(x => x.conclusion === 'success').length, ko = jb.jobs.filter(x => x.conclusion === 'failure').map(x => x.name);
      l += `\n   étapes : ${ok} finies, ${enc.length} en cours, ${att} en attente${ko.length ? ', RATÉES : ' + ko.join(', ') : ''}`;
      for (const x of enc.slice(0, 6)) { const s = (x.steps || []).find(s => s.status === 'in_progress'); l += `\n   - ${x.name} : ${s ? '« ' + s.name + ' » depuis ' + minutes(s.started_at) + ' min' : 'démarre'} (étape commencée il y a ${minutes(x.started_at)} min)`; }
    } catch (e) {}
    lignes.push(l);
  }
  return lignes.join('\n') || 'aucune fabrication';
}
async function journal({ fabrication, etape, motif }) {
  const jb = await gh('/actions/runs/' + fabrication + '/jobs?per_page=100');
  let out = jb.jobs.map(x => `${x.name} : ${x.status === 'completed' ? x.conclusion : x.status} (${minutes(x.started_at || x.created_at, x.completed_at)} min)` + ((x.steps || []).filter(s => s.conclusion === 'failure' || s.status === 'in_progress').map(s => ' — étape « ' + s.name + ' » ' + (s.conclusion || 'en cours')).join(''))).join('\n');
  let cibles = etape ? jb.jobs.filter(x => x.name.toLowerCase().includes(String(etape).toLowerCase())) : jb.jobs.filter(x => x.conclusion === 'failure');
  if (!cibles.length) cibles = jb.jobs.filter(x => x.status === 'completed').slice(-1);
  for (const x of cibles.slice(0, 2)) {
    if (x.status !== 'completed') { out += `\n\n[${x.name}] encore en cours : le journal complet sera lisible à la fin de l'étape. Étapes : ` + (x.steps || []).map(s => s.name + '=' + (s.conclusion || s.status)).join(', '); continue; }
    try {
      const t = (await gh('/actions/jobs/' + x.id + '/logs', { texte: true })).split('\n').map(l => l.replace(/^\d{4}-\d\d-\d\dT[\d:.]+Z /, ''));
      let garde;
      if (motif) { const re = new RegExp(motif, 'i'); garde = t.map((l, i) => re.test(l) ? t.slice(Math.max(0, i - 2), i + 3).join('\n') : null).filter(Boolean).slice(0, 25).join('\n--\n'); }
      else { const err = t.map((l, i) => /error|erreur|traceback|exception|failed|killed|no space|timeout|##\[error\]/i.test(l) ? i : -1).filter(i => i >= 0);
        garde = (err.length ? 'Lignes d\'erreur :\n' + [...new Set(err.slice(-12))].map(i => t.slice(Math.max(0, i - 3), i + 2).join('\n')).join('\n--\n') + '\n\n' : '') + 'Fin du journal :\n' + t.slice(-60).join('\n'); }
      out += `\n\n[journal de ${x.name}]\n` + court(garde, 7000);
    } catch (e) { out += `\n\n[${x.name}] journal illisible : ${e.message}`; }
  }
  return out;
}
const ref = r => r || 'HEAD';
function lire({ chemin, debut = 1, fin, branche }) {
  let t; try { t = sh('git', ['show', (branche ? 'origin/' + branche : 'HEAD') + ':' + chemin]); } catch (e) { return 'fichier introuvable : ' + chemin + (branche ? ' (branche ' + branche + ')' : ''); }
  const L = t.split('\n'), a = Math.max(1, +debut || 1), b = Math.min(L.length, +fin || a + 249);
  return `${chemin} (${L.length} lignes, de ${a} à ${b})\n` + L.slice(a - 1, b).map((l, i) => (a + i) + '\t' + l.slice(0, 400)).join('\n');
}
function chercher({ motif, dossier }) {
  try { return court(sh('git', ['grep', '-n', '-I', '-i', '-E', motif, 'HEAD', '--', ...(dossier ? [dossier] : ['studio', 'docs', '.github', 'outils', 'technicien'])]).split('\n').slice(0, 80).map(l => l.replace(/^HEAD:/, '').slice(0, 300)).join('\n'), 8000); }
  catch (e) { return 'rien trouvé pour « ' + motif + ' »'; }
}
function lister({ dossier = '' }) {
  try { return sh('git', ['ls-tree', '-l', 'HEAD', dossier ? dossier.replace(/\/?$/, '/') : '.']).split('\n').filter(Boolean).slice(0, 200).map(l => { const p = l.split(/\s+/); return (p[1] === 'tree' ? '📁 ' : '   ') + l.split('\t')[1] + (p[3] !== '-' ? ' (' + Math.round(p[3] / 1024) + ' Ko)' : ''); }).join('\n'); }
  catch (e) { return 'dossier introuvable'; }
}
async function demande({ numero }) {
  let i; try { i = await gh('/issues/' + numero); } catch (e) { return 'Il n\'y a pas de demande n° ' + numero + ' (le numéro d\'un épisode n\'est pas celui de sa demande). Regarde la liste avec « demandes ».'; }
  const c = await gh('/issues/' + numero + '/comments?per_page=100');
  return `Demande n° ${numero} : « ${i.title} » (${i.state})\n--- début du texte ---\n${court(i.body, 1500)}\n--- derniers messages ---\n` + c.slice(-10).map(x => `[${x.created_at.slice(5, 16).replace('T', ' ')} · ${x.user.login.includes('[bot]') ? 'studio' : 'Issa'}] ${court(x.body, 700)}`).join('\n');
}
async function demandes() {
  const L = await gh('/issues?state=open&per_page=30');
  return L.map(i => `n° ${i.number} · ${i.title} · ${i.labels.map(l => l.name).join(',')} · mise à jour ${i.updated_at.slice(5, 16).replace('T', ' ')}`).join('\n');
}
async function fichiersDemande({ numero }) {
  try { const L = await gh('/contents/' + numero + '?ref=fichiers'); return L.map(f => f.name + ' (' + Math.round(f.size / 1024) + ' Ko)').join('\n'); } catch (e) { return 'aucun fichier rangé pour la demande ' + numero; }
}
async function regarder({ chemin, question }) {   // Gemini regarde une image ou une petite vidéo et répond à la question
  const k = process.env.GEMINI_API_KEY; if (!k) return 'pas de clé Gemini : impossible de regarder';
  let data; const [n, ...reste] = chemin.split('/');
  if (/^\d+$/.test(n)) data = await gh('/contents/' + chemin + '?ref=fichiers', { accept: 'application/vnd.github.raw', brut: true });
  else { try { data = sh('git', ['show', 'HEAD:' + chemin], { encoding: 'buffer' }); } catch (e) { return 'fichier introuvable : ' + chemin; } }
  if (data.length > 18e6) return 'fichier trop gros pour être regardé (' + Math.round(data.length / 1e6) + ' Mo)';
  const mime = /\.mp4$/i.test(chemin) ? 'video/mp4' : /\.jpe?g$/i.test(chemin) ? 'image/jpeg' : /\.wav$/i.test(chemin) ? 'audio/wav' : 'image/png';
  for (const m of await listeGemini(k)) {
    const r = await fetch('https://generativelanguage.googleapis.com/v1beta/models/' + m + ':generateContent', { method: 'POST', headers: { 'x-goog-api-key': k, 'Content-Type': 'application/json' },
      body: JSON.stringify({ contents: [{ role: 'user', parts: [{ inline_data: { mime_type: mime, data: data.toString('base64') } }, { text: 'Tu aides le technicien d\'un studio d\'animation. Décris précisément ce que tu vois (ou entends), en français simple, pour répondre à : ' + (question || 'y a-t-il un problème ?') }] }], generationConfig: { temperature: 0.2 } }) }).catch(() => null);
    if (!r || !r.ok) continue; const d = await r.json(), t = (d.candidates?.[0]?.content?.parts || []).map(p => p.text || '').join(''); if (t) return court(t, 5000);
  }
  return 'Gemini n\'a pas pu regarder ce fichier pour le moment';
}
async function arreter({ fabrication, raison }) { await gh('/actions/runs/' + fabrication + '/cancel', { method: 'POST' }); return 'fabrication ' + fabrication + ' arrêtée (' + (raison || '') + '). Attends environ 30 s avant de la relancer.'; }
async function relancer({ fabrication, tout = false }) {
  for (let i = 0; i < 12; i++) { const r = await gh('/actions/runs/' + fabrication); if (r.status === 'completed') break; await dodo(10000); }
  await gh('/actions/runs/' + fabrication + (tout ? '/rerun' : '/rerun-failed-jobs'), { method: 'POST' }); return 'fabrication ' + fabrication + ' relancée (' + (tout ? 'en entier' : 'seulement les étapes ratées ou arrêtées') + ')';
}
let attente = null;   // ce qui attend l'accord d'Issa (lu dans la dernière réponse du technicien)
const ACCORD = /^\s*(oui|ok|okay|d'?accord|vas[- ]?y|go|accepte|valide|fusionne|lance|c'?est bon)\b/i;
function accorde(action, cible) { return MSG_ACCORD && attente && attente.action === action && String(attente.cible) === String(cible); }
async function lancer({ quoi, numero, de, a, choix }) {
  if (quoi === 'video' && !accorde('video', numero)) return 'Il faut l\'accord d\'Issa pour une vidéo complète : appelle proposer(action="video", cible="' + numero + '"), puis termine en lui posant la question.';
  if (quoi === 'fiche') { await gh('/actions/workflows/fiche.yml/dispatches', { method: 'POST', body: JSON.stringify({ ref: 'main', inputs: { script: 'demandes/episode_' + numero + '.txt', issue: String(numero) } }) }); }
  else await gh('/actions/workflows/episode.yml/dispatches', { method: 'POST', body: JSON.stringify({ ref: 'main', inputs: { script: 'demandes/episode_' + numero + '.txt', issue: String(numero), apercu: quoi === 'video' ? 'false' : 'true', choix: choix || '', de: quoi === 'planches' ? (de || '') : '', fin: quoi === 'planches' ? (a || '') : '' } }) });
  const M = { apercu: 'l\'aperçu des plans (environ 10 minutes)', planches: 'les planches' + (de ? ' de ' + de + ' à ' + a : ''), video: 'la vidéo complète (environ 30 minutes)', fiche: 'la fiche Gemini (environ 3 minutes)' }[quoi] || quoi;
  await gh('/issues/' + numero + '/comments', { method: 'POST', body: JSON.stringify({ body: '⏳ Le technicien relance ' + M + '. Vous serez prévenu ici.' }) });
  return quoi + ' lancé pour la demande ' + numero + '. Utilise attendre(quoi="episode") si tu dois vérifier le résultat.';
}
const PERMIS = /^(studio\/[\w./-]+\.(py|json|txt|sh)|docs\/[\w./-]+\.md|outils\/[\w.-]+\.(html|md)|exemples\/[\w.-]+\.txt|demandes\/[\w.-]+\.(txt|json)|technicien\/[\w.-]+\.md)$/;
async function essayerCode({ changements, explication, episode }) {
  if (!Array.isArray(changements) || !changements.length) return 'aucun changement donné';
  const br = 'technicien-' + new Date().toISOString().slice(0, 16).replace(/[-:T]/g, '') + '-' + Math.random().toString(36).slice(2, 5), D = '/tmp/essai-' + br;
  sh('git', ['worktree', 'add', '-q', '-b', br, D, 'origin/main']);
  try {
    for (const c of changements) {
      if (!PERMIS.test(c.fichier || '') || /\.\./.test(c.fichier)) return 'fichier interdit : ' + c.fichier + ' (permis : studio/, docs/, outils/, exemples/, demandes/ ; jamais .github/)';
      const f = D + '/' + c.fichier;
      if (!c.ancien) { if (fs.existsSync(f)) return 'le fichier ' + c.fichier + ' existe déjà : donne « ancien » (texte exact à remplacer)'; fs.mkdirSync(f.replace(/\/[^/]+$/, ''), { recursive: true }); fs.writeFileSync(f, c.nouveau); continue; }
      if (!fs.existsSync(f)) return 'fichier introuvable : ' + c.fichier;
      const t = fs.readFileSync(f, 'utf8'), n = t.split(c.ancien).length - 1;
      if (n !== 1) return (n ? 'texte trouvé ' + n + ' fois' : 'texte « ancien » introuvable') + ' dans ' + c.fichier + ' : relis le fichier avec « lire » et recopie les lignes EXACTEMENT (espaces compris).';
      fs.writeFileSync(f, t.replace(c.ancien, () => c.nouveau));
    }
    for (const c of changements) {   // vérification immédiate de l'écriture du fichier
      const f = D + '/' + c.fichier;
      try { if (/\.py$/.test(f)) sh('python3', ['-m', 'py_compile', f]); if (/\.json$/.test(f)) JSON.parse(fs.readFileSync(f, 'utf8')); if (/\.sh$/.test(f)) sh('bash', ['-n', f]); }
      catch (e) { return 'la modification de ' + c.fichier + ' est mal écrite (erreur : ' + court(e.stderr || e.message, 600) + '). Corrige et réessaie.'; }
    }
    sh('git', ['-C', D, 'add', '-A']); sh('git', ['-C', D, '-c', 'user.name=technicien', '-c', 'user.email=studio@sounsouni.pro', 'commit', '-qm', 'Technicien : ' + String(explication || 'modification').slice(0, 200)]);
    sh('git', ['-C', D, 'push', '-q', 'origin', br]);
  } finally { try { sh('git', ['worktree', 'remove', '--force', D]); } catch (e) {} }
  const t1 = new Date(Date.now() - 5000).toISOString();
  const scr = episode && fs.existsSync(String(episode)) ? episode : (episode && /^\d+$/.test(String(episode)) ? 'demandes/episode_' + episode + '.txt' : 'exemples/episode18_l_avis.txt');
  await gh('/actions/workflows/essai-code.yml/dispatches', { method: 'POST', body: JSON.stringify({ ref: 'main', inputs: { issue: String(ISSUE), branche: br, script: scr } }) });
  let id = null; for (let i = 0; i < 10 && !id; i++) { await dodo(6000); const r = await gh('/actions/workflows/essai-code.yml/runs?per_page=5'); id = r.workflow_runs.find(x => x.created_at >= t1.slice(0, 19))?.id; }
  return 'Modification mise sur la copie « ' + br + ' » ; essai lancé' + (id ? ' (fabrication ' + id + ')' : '') + ' sur ' + scr + ' + 2 épisodes validés (environ 10 à 15 min). Appelle attendre(fabrication=' + (id || '…') + ') pour connaître le résultat. Si l\'essai réussit, appelle proposer(action="fusionner", cible="' + br + '") et demande l\'accord d\'Issa.';
}
async function attendre({ fabrication, quoi, minutes: mx = 20 }) {
  mx = Math.min(30, +mx || 20, MAX_MIN - (Date.now() - T0) / 60000 - 3);
  if (mx < 1) return 'plus le temps d\'attendre dans cette recherche : dis à Issa de te redemander dans quelques minutes';
  if (!fabrication && quoi) { const r = await gh('/actions/workflows/' + (quoi === 'essai' ? 'essai-code' : quoi === 'episode' ? 'episode' : quoi) + '.yml/runs?per_page=1'); fabrication = r.workflow_runs[0]?.id; }
  if (!fabrication) return 'quelle fabrication attendre ? donne son numéro';
  const fin = Date.now() + mx * 60000; let r;
  while (Date.now() < fin) { r = await gh('/actions/runs/' + fabrication); if (r.status === 'completed') break; await maj('⏳ J\'attends la fin de « ' + r.name + ' » (' + minutes(r.run_started_at || r.created_at) + ' min)…'); await dodo(30000); }
  if (r.status !== 'completed') return 'toujours en cours après ' + Math.round(mx) + ' min (' + r.name + ', ' + minutes(r.run_started_at || r.created_at) + ' min en tout)';
  let plus = '';
  if (/Essai/.test(r.name)) { const c = await gh('/issues/' + ISSUE + '/comments?per_page=100'); const e = c.reverse().find(x => /Essai du code (réussi|raté)/.test(x.body)); if (e) plus = '\nMessage de l\'essai : ' + court(e.body, 2500); }
  return r.name + ' terminée : ' + (r.conclusion === 'success' ? 'réussie' : r.conclusion) + ' en ' + minutes(r.run_started_at || r.created_at, r.updated_at) + ' min.' + plus + (r.conclusion !== 'success' ? '\nRegarde journal(fabrication=' + fabrication + ').' : '');
}
async function fusionner({ branche }) {
  if (!accorde('fusionner', branche)) return 'Il faut l\'accord d\'Issa : appelle proposer(action="fusionner", cible="' + branche + '"), puis termine en lui posant la question.';
  await gh('/merges', { method: 'POST', body: JSON.stringify({ base: 'main', head: branche, commit_message: 'Modification du technicien acceptée par Issa (' + branche + ')' }) });
  await gh('/git/refs/heads/' + branche, { method: 'DELETE' }).catch(() => {});
  attente = null; return 'modification ' + branche + ' entrée dans le studio. Les prochaines fabrications l\'utiliseront.';
}
let proposition = null;
function proposer({ action, cible, explication }) { proposition = { action, cible: String(cible), explication: explication || '' }; return 'Proposition enregistrée. Termine maintenant ta réponse en demandant à Issa s\'il est d\'accord (il répondra « oui » ou « non »).'; }
function noter({ theme, lecon }) { return ajouterLecon(theme, lecon, FOURN[actuel]?.nom.split(' ')[0] || 'IA') ? 'leçon notée dans le carnet (thème ' + theme + ')' : 'leçon déjà dans le carnet (ou trop courte)'; }

const O = (name, description, props = {}, req = []) => ({ type: 'function', function: { name, description, parameters: { type: 'object', properties: props, required: req } } });
const S = d => ({ type: 'string', description: d }), I = d => ({ type: 'integer', description: d });
const OUTILS = [
  O('etat', 'Liste des dernières fabrications (en cours, réussies, ratées) avec leur durée, et pour celles en cours l\'étape où elles sont et depuis combien de temps.', { nombre: I('combien (25 par défaut)') }),
  O('journal', 'Journal d\'une fabrication : étapes, lignes d\'erreur et fin du journal de l\'étape ratée (ou de celle demandée).', { fabrication: I('numéro de la fabrication (#… dans etat)'), etape: S('nom (ou morceau du nom) de l\'étape, ex. "voix (3)"'), motif: S('mot à chercher dans le journal (expression régulière)') }, ['fabrication']),
  O('demandes', 'Liste des demandes (épisodes) ouvertes.'),
  O('demande', 'Texte et derniers messages d\'une demande d\'épisode.', { numero: I('numéro de la demande') }, ['numero']),
  O('fichiers_demande', 'Fichiers rangés pour une demande (aperçu, planches, vidéo légère, plans_resume.json…).', { numero: I('numéro') }, ['numero']),
  O('regarder', 'Faire regarder une image, une petite vidéo ou un son par Gemini. chemin = "<numéro de demande>/<fichier>" (fichiers rangés) ou chemin dans le dépôt.', { chemin: S('ex. "10/apercu_plans.png" ou "10/video.mp4"'), question: S('ce qu\'il faut vérifier') }, ['chemin']),
  O('lire', 'Lire un fichier du studio (numéros de ligne).', { chemin: S('ex. studio/director.py'), debut: I('première ligne'), fin: I('dernière ligne'), branche: S('autre branche (facultatif)') }, ['chemin']),
  O('chercher', 'Chercher un mot ou une expression dans les fichiers du studio.', { motif: S('expression régulière'), dossier: S('dossier (facultatif)') }, ['motif']),
  O('lister', 'Lister un dossier du studio.', { dossier: S('ex. studio/assets') }),
  O('arreter', 'Arrêter une fabrication bloquée.', { fabrication: I('numéro'), raison: S('pourquoi') }, ['fabrication']),
  O('relancer', 'Relancer une fabrication terminée (par défaut seulement les étapes ratées ou arrêtées : les autres sont gardées).', { fabrication: I('numéro'), tout: { type: 'boolean', description: 'true = tout refaire' } }, ['fabrication']),
  O('lancer', 'Lancer pour une demande : apercu, planches (de/a), fiche (Gemini) ou video (vidéo complète : accord d\'Issa obligatoire).', { quoi: { type: 'string', enum: ['apercu', 'planches', 'fiche', 'video'] }, numero: I('numéro de la demande'), de: S('planches : début, ex. 1:20'), a: S('planches : fin'), choix: S('réponse aux planches, ex. "1B 3C"') }, ['quoi', 'numero']),
  O('essayer_code', 'Modifier le code sur une copie à part et la faire essayer automatiquement. Chaque changement remplace un texte EXACT (lu avec « lire ») présent une seule fois. ancien vide = nouveau fichier.', { changements: { type: 'array', items: { type: 'object', properties: { fichier: S('ex. studio/director.py'), ancien: S('lignes exactes actuelles'), nouveau: S('lignes corrigées') }, required: ['fichier', 'ancien', 'nouveau'] } }, explication: S('ce que corrige la modification'), episode: S('numéro de la demande dont l\'épisode sert à l\'essai (facultatif)') }, ['changements', 'explication']),
  O('attendre', 'Attendre la fin d\'une fabrication (au plus 30 min) et donner son résultat.', { fabrication: I('numéro'), quoi: S('ou : "essai", "episode", "format"'), minutes: I('au plus') }),
  O('proposer', 'Préparer une action qui demande l\'accord d\'Issa (fusionner une modification essayée, lancer une vidéo complète). Ensuite, termine ta réponse par la question.', { action: { type: 'string', enum: ['fusionner', 'video'] }, cible: S('branche (fusionner) ou numéro de demande (video)'), explication: S('pour Issa') }, ['action', 'cible']),
  O('fusionner', 'Mettre dans le vrai studio une modification essayée (seulement après l\'accord d\'Issa).', { branche: S('technicien-… ou assistant-…') }, ['branche']),
  O('noter', 'Noter dans le carnet une leçon utile pour la prochaine fois (pour toutes les IA du studio) : symptôme → cause → remède, en une phrase.', { theme: { type: 'string', enum: ['fabrication', 'format', 'ia', 'images', 'mise-en-scene', 'voix', 'son', 'page', 'pour-claude'] }, lecon: S('la leçon') }, ['theme', 'lecon']),
];
const FAIRE = { etat, journal, demandes, demande, fichiers_demande: fichiersDemande, regarder, lire, chercher, lister, arreter, relancer, lancer, essayer_code: essayerCode, attendre, proposer, fusionner, noter };
const DIRE = { etat: '🔎 Je regarde les fabrications', journal: '📜 Je lis le journal', demandes: '📋 Je regarde les demandes', demande: '📋 Je lis la demande', fichiers_demande: '🗂 Je regarde les fichiers', regarder: '👀 Je regarde', lire: '📖 Je lis', chercher: '🔍 Je cherche', lister: '📁 Je regarde le dossier',
  arreter: '⏹ J\'arrête', relancer: '🔁 Je relance', lancer: '▶️ Je lance', essayer_code: '🧪 J\'essaie une modification', attendre: '⏳ J\'attends', proposer: '🙋 Je prépare une proposition', fusionner: '✅ Je mets la modification dans le studio', noter: '📝 Je note une leçon' };

// ---------------- la conversation ----------------
let commentaire = null; const etapes = [];
async function maj(enCours) {
  const corps = '🛠 **Je cherche…** (' + Math.round((Date.now() - T0) / 60000) + ' min)\n\n' + etapes.map((e, i) => (i + 1) + '. ' + e).join('\n') + (enCours ? '\n\n' + enCours : '') + '\n<!--tech:encours-->';
  try { if (commentaire) await gh('/issues/comments/' + commentaire, { method: 'PATCH', body: JSON.stringify({ body: corps }) }); else commentaire = (await gh('/issues/' + ISSUE + '/comments', { method: 'POST', body: JSON.stringify({ body: corps }) })).id; } catch (e) { log('maj : ' + e.message); }
}
let MSG_ACCORD = false;
const nettoyerTexte = b => b.replace(/<details>[\s\S]*?<\/details>/g, '').replace(/<!--[\s\S]*?-->/g, '').replace(/\n+_Generated by[\s\S]*$/, '').trim();

async function principal() {
  const C = await gh('/issues/' + ISSUE + '/comments?per_page=100');
  // la question d'Issa : le commentaire qui a lancé la recherche (ou le dernier d'Issa)
  const issa = C.filter(x => !x.user.login.includes('[bot]'));
  const q = (MESSAGE_ID ? C.find(x => String(x.id) === String(MESSAGE_ID)) : null) || issa[issa.length - 1];
  if (!q) { log('pas de message'); return; }
  const texte = nettoyerTexte(q.body);
  // 👍 / 👎 sur la dernière réponse : la note du modèle change, sans appeler d'IA
  const pouce = texte.match(/^(👍|👎)\s*$/u);
  const avant = C.filter(x => x.created_at < q.created_at);
  const derniere = [...avant].reverse().find(x => x.user.login.includes('[bot]') && /<!--tech:fin/.test(x.body));
  if (pouce) {
    const m = derniere?.body.match(/<!--tech:fin modele="([^"]+)"/); if (m) { const s = stats[m[1]] = stats[m[1]] || { sessions: 0, reussies: 0, pouces_haut: 0, pouces_bas: 0, etapes: 0 }; s[pouce[1] === '👍' ? 'pouces_haut' : 'pouces_bas']++; }
    await gh('/issues/comments/' + q.id + '/reactions', { method: 'POST', body: JSON.stringify({ content: 'eyes' }) }).catch(() => {});
    return { pouce: true };
  }
  const at = derniere?.body.match(/<!--tech:attente (\{.*?\})-->/); if (at) try { attente = JSON.parse(at[1]); } catch (e) {}
  MSG_ACCORD = !!attente && ACCORD.test(texte);

  FOURN = await fournisseurs(); if (!FOURN.length) throw new Error('aucune clé d\'IA dans les secrets GitHub');
  const sys = fs.readFileSync('docs/TECHNICIEN.md', 'utf8') + '\n\n## NOTES DU PROJET (écrites par Claude, à jour)\n' + fs.readFileSync('CLAUDE.md', 'utf8') + '\n\n## CARNET (leçons déjà apprises)\n' + carnet +
    '\n\nNous sommes le ' + new Date().toISOString().slice(0, 16).replace('T', ' ') + ' (heure de Bamako = UTC). La demande « Technicien » est le n° ' + ISSUE + '.' +
    (attente ? '\n\nEN ATTENTE DE L\'ACCORD D\'ISSA : ' + JSON.stringify(attente) + (MSG_ACCORD ? ' → Issa vient de dire OUI : fais-le maintenant.' : ' → s\'il ne dit pas oui clairement, ne le fais pas.') : '');
  const hist = [];
  for (const x of avant.slice(-30)) {
    if (x.user.login.includes('[bot]')) { if (/<!--tech:fin/.test(x.body) || /Essai du code/.test(x.body)) hist.push({ role: 'assistant', content: court(nettoyerTexte(x.body), 1500) }); }
    else if (!/^(👍|👎)\s*$/u.test(x.body.trim())) hist.push({ role: 'user', content: court(nettoyerTexte(x.body), 1500) });
  }
  const msgs = [{ role: 'system', content: sys }, ...hist.slice(-12), { role: 'user', content: texte }];
  await maj('🤔 Je réfléchis…');
  let reponse = '', n = 0, p;
  while (true) {
    const tropLong = n >= MAX_ETAPES || (Date.now() - T0) / 60000 > MAX_MIN;
    if (tropLong) msgs.push({ role: 'user', content: '(Message du studio : temps ou nombre d\'étapes dépassé. Arrête de chercher et réponds maintenant à Issa : ce que tu as trouvé, ce qui reste, et si besoin un résumé pour Claude.)' });
    const r = await penser(msgs, tropLong ? null : OUTILS); p = r.p; const m = r.m;
    msgs.push({ ...m, role: 'assistant' });
    const tc = m.tool_calls || [];
    if (!tc.length) { reponse = (m.content || '').trim(); break; }
    for (const t of tc) {
      n++; let args = {}; try { args = JSON.parse(t.function.arguments || '{}'); } catch (e) {}
      const nom = t.function.name, quoi = DIRE[nom] || nom, detail = args.chemin || args.motif || args.numero || args.fabrication || args.branche || args.quoi || args.dossier || '';
      etapes.push(quoi + (detail ? ' (' + String(detail).slice(0, 60) + ')' : '')); await maj(); log('outil ' + nom + ' ' + JSON.stringify(args).slice(0, 200));
      let res; try { res = FAIRE[nom] ? await FAIRE[nom](args) : 'outil inconnu : ' + nom; } catch (e) { res = 'ERREUR : ' + e.message; }
      res = court(res, 9000); log('  → ' + res.slice(0, 160).replace(/\n/g, ' ¶ '));
      etapes[etapes.length - 1] += ' — ' + res.split('\n')[0].slice(0, 90);
      msgs.push({ role: 'tool', tool_call_id: t.id, name: nom, content: res });
    }
    // garder la conversation légère : les vieux résultats d'outils sont raccourcis
    let tot = msgs.reduce((s, x) => s + String(x.content || '').length, 0);
    for (let i = 1; i < msgs.length - 6 && tot > 150000; i++) if (msgs[i].role === 'tool' && msgs[i].content.length > 400) { tot -= msgs[i].content.length - 400; msgs[i].content = msgs[i].content.slice(0, 400) + '…(raccourci)'; }
  }
  return { texte, reponse, msgs, p, n };
}

async function bilan({ texte, reponse, msgs, p, n }) {   // auto-apprentissage : l'IA relit sa recherche et en tire des leçons
  const resume = msgs.filter(x => x.role !== 'system').map(x => x.role === 'tool' ? '  résultat : ' + String(x.content).slice(0, 300) : x.tool_calls ? x.tool_calls.map(t => '  outil ' + t.function.name + ' ' + String(t.function.arguments).slice(0, 200)).join('\n') : (x.role === 'user' ? 'ISSA : ' : 'TECHNICIEN : ') + String(x.content || '').slice(0, 800)).join('\n');
  const consigne = 'Tu relis une recherche du technicien de Sounsouni Studio pour en tirer des leçons pour la prochaine fois (pour toutes les IA du studio).\nRéponds UNIQUEMENT en JSON : {"reussie": true|false, "theme": "un mot", "journal": "5 à 10 lignes : la demande, les hypothèses, ce qui a marché, ce qui n\'a pas marché, les étapes inutiles à éviter", "lecons": [{"theme": "fabrication|format|ia|images|mise-en-scene|voix|son|page|pour-claude", "texte": "symptôme → cause → remède, une phrase"}]}\nAu plus 3 leçons, seulement des leçons VÉRIFIÉES pendant la recherche, générales et réutilisables, absentes du carnet. Aucune leçon si rien de neuf. "reussie" = le problème est vraiment réglé ou la question a vraiment une réponse.\n\n## CARNET ACTUEL\n' + carnet;
  try {
    const r = await penser([{ role: 'system', content: consigne }, { role: 'user', content: '## LA RECHERCHE\n' + court(resume, 40000) + '\n\n## RÉPONSE FINALE\n' + reponse }], null);
    const j = JSON.parse(r.m.content.replace(/^[\s\S]*?\{/, '{').replace(/\}[^}]*$/, '}'));
    for (const l of (j.lecons || []).slice(0, 3)) ajouterLecon(l.theme, l.texte, p.nom.split(' ')[0]);
    const nom = 'technicien/journal/' + new Date().toISOString().slice(0, 16).replace(/[:T]/g, '-') + '.md';
    fs.mkdirSync('technicien/journal', { recursive: true });
    fs.writeFileSync(nom, '# Recherche du ' + new Date().toISOString().slice(0, 16).replace('T', ' ') + ' (' + p.nom + ', ' + n + ' étapes, ' + Math.round((Date.now() - T0) / 60000) + ' min)\n\n**Issa :** ' + texte + '\n\n**Bilan :**\n' + (j.journal || '') + '\n\n**Étapes :**\n' + etapes.map((e, i) => (i + 1) + '. ' + e).join('\n') + '\n\n**Réponse :**\n' + reponse + '\n');
    const L = fs.readdirSync('technicien/journal').sort(); L.slice(0, -80).forEach(f => fs.unlinkSync('technicien/journal/' + f));   // on garde les 80 dernières recherches
    return j;
  } catch (e) { log('bilan : ' + e.message); return { reussie: true }; }
}
async function ranger() {   // carnet trop long : une IA le condense (mêmes leçons, sans doublons)
  if (carnet.length < 14000) return;
  try {
    const r = await penser([{ role: 'system', content: 'Condense ce carnet de leçons : fusionne les doublons, garde les leçons utiles et précises, mêmes titres « ## thème », même format de ligne « - date · qui · symptôme → cause → remède ». Réponds uniquement avec le carnet complet en Markdown.' }, { role: 'user', content: carnet }], null);
    const t = r.m.content.replace(/^```\w*\n|```\s*$/g, '').trim();
    if (t.length > 2000 && t.length < carnet.length && /^## /m.test(t)) { carnet = t + '\n'; log('carnet rangé'); }
  } catch (e) { log('rangement : ' + e.message); }
}
function enregistrer(msg) {
  fs.writeFileSync(CARNET, carnet); fs.writeFileSync(MODELES, JSON.stringify(stats, null, 1) + '\n');
  try { sh('git', ['add', 'technicien']); sh('git', ['-c', 'user.name=technicien', '-c', 'user.email=studio@sounsouni.pro', 'commit', '-qm', msg]); } catch (e) { return; }
  for (let i = 0; i < 5; i++) { try { sh('git', ['pull', '-q', '--rebase', '--autostash', 'origin', 'main']); sh('git', ['push', '-q', 'origin', 'HEAD:main']); return; } catch (e) { log('envoi carnet : nouvel essai'); } }
}

try {
  const r = await principal();
  if (r?.pouce) { enregistrer('Technicien : avis d\'Issa sur une réponse'); process.exit(0); }
  if (!r) process.exit(0);
  const s = stats[r.p.nom] = stats[r.p.nom] || { sessions: 0, reussies: 0, pouces_haut: 0, pouces_bas: 0, etapes: 0 };
  const corps = r.reponse + '\n\n<details><summary>Ce que j\'ai fait (' + etapes.length + ' étapes, ' + Math.round((Date.now() - T0) / 60000) + ' min, ' + r.p.nom + ')</summary>\n\n' + (etapes.map((e, i) => (i + 1) + '. ' + e).join('\n') || 'rien') + '\n</details>\n<!--tech:fin modele="' + r.p.nom + '"-->' + (proposition ? '<!--tech:attente ' + JSON.stringify(proposition) + '-->' : '');
  if (commentaire) await gh('/issues/comments/' + commentaire, { method: 'PATCH', body: JSON.stringify({ body: corps }) }); else await gh('/issues/' + ISSUE + '/comments', { method: 'POST', body: JSON.stringify({ body: corps }) });
  log('réponse envoyée');
  const b = await bilan(r);
  s.sessions++; if (b.reussie !== false) s.reussies++; s.etapes += r.n; s.themes = s.themes || {}; if (b.theme) s.themes[b.theme] = (s.themes[b.theme] || 0) + 1;
  await ranger();
  enregistrer('Technicien : carnet et journal (' + (nouvellesLecons.length ? nouvellesLecons.length + ' leçon(s)' : 'sans nouvelle leçon') + ')');
  if (nouvellesLecons.length && commentaire) await gh('/issues/comments/' + commentaire, { method: 'PATCH', body: JSON.stringify({ body: corps.replace('</details>', '</details>\n\n📝 Appris pour la prochaine fois :\n' + nouvellesLecons.map(l => '- ' + l).join('\n')) }) }).catch(() => {});
} catch (e) {
  console.error(e);
  const t = '❌ Le technicien n\'a pas pu finir : ' + e.message + '\n\nRéessayez dans quelques minutes (vos messages sont gardés).\n<!--tech:fin modele="erreur"-->';
  if (commentaire) await gh('/issues/comments/' + commentaire, { method: 'PATCH', body: JSON.stringify({ body: t }) }).catch(() => {}); else await gh('/issues/' + ISSUE + '/comments', { method: 'POST', body: JSON.stringify({ body: t }) }).catch(() => {});
  process.exit(1);
}
