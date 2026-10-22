// Mise au format d'un script par l'assistant, faite par une machine GitHub (le téléphone peut être fermé).
// Mêmes règles que la page Studio mobile : les fonctions de nettoyage sont prises dans outils/studio_mobile.html (blocs « <<format »).
// Clés : secrets GitHub GROQ_API_KEY (et en secours CEREBRAS_API_KEY, OPENROUTER_API_KEY, GEMINI_API_KEY). Jamais dans les fichiers.
import fs from 'fs';

const { ISSUE, REPO, GH_TOKEN, AUTO } = process.env;
const html = fs.readFileSync('outils/studio_mobile.html', 'utf8');
const code = [...html.matchAll(/\/\/ <<format[^\n]*\n([\s\S]*?)\/\/ format>>/g)].map(m => m[1]).join('\n');
const F = new Function(code + '\nreturn {preBrut,parties,avant,nettoyer,apres,controle,dejaFormat,regles_seules};')();
const dodo = ms => new Promise(r => setTimeout(r, ms));
const gh = async (chemin, o = {}) => {
  const r = await fetch('https://api.github.com/repos/' + REPO + chemin, { ...o, headers: { Authorization: 'Bearer ' + GH_TOKEN, Accept: 'application/vnd.github+json', 'Content-Type': 'application/json' } });
  if (!r.ok) throw new Error('GitHub ' + r.status + ' ' + (await r.text()).slice(0, 200));
  return r.status === 204 ? null : r.json();
};
const dire = t => gh('/issues/' + ISSUE + '/comments', { method: 'POST', body: JSON.stringify({ body: t }) });
const log = t => console.log(new Date().toISOString().slice(11, 19), t);

async function gemini(sys, user) {
  const k = process.env.GEMINI_API_KEY; if (!k) throw new Error('pas de clé Gemini');
  let L = ['models/gemini-3.8-flash', 'models/gemini-3-flash-preview', 'models/gemini-flash-latest'];
  try { const j = await (await fetch('https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000', { headers: { 'x-goog-api-key': k } })).json();
    L = [...new Set([...L, ...(j.models || []).filter(x => (x.supportedGenerationMethods || []).includes('generateContent') && /flash/.test(x.name) && !/lite|image|tts|live|audio|embed|exp/.test(x.name)).map(x => x.name)])]; } catch (e) {}
  for (let tour = 0; tour < 8; tour++) {
    for (const m of L) {
      const r = await fetch('https://generativelanguage.googleapis.com/v1beta/' + m + ':generateContent', { method: 'POST', headers: { 'x-goog-api-key': k, 'Content-Type': 'application/json' },
        body: JSON.stringify({ systemInstruction: { parts: [{ text: sys }] }, contents: [{ role: 'user', parts: [{ text: user }] }], generationConfig: { temperature: 0.2 } }) }).catch(() => null);
      if (!r || !r.ok) continue;
      const d = await r.json(), t = (d.candidates?.[0]?.content?.parts || []).map(p => p.text || '').join('');
      if (t) return t;
    }
    log('Gemini saturé, nouvel essai dans 30 s'); await dodo(30000);
  }
  throw new Error('Gemini saturé');
}

async function ia(messages) {   // Groq, puis Cerebras, OpenRouter, Gemini : comme la page, mais ici on peut attendre longtemps
  const P = [['Groq', 'https://api.groq.com/openai/v1/chat/completions', process.env.GROQ_API_KEY, 'openai/gpt-oss-120b', { reasoning_effort: 'low' }],
    ['Cerebras', 'https://api.cerebras.ai/v1/chat/completions', process.env.CEREBRAS_API_KEY, 'gpt-oss-120b', { reasoning_effort: 'low' }],
    ['OpenRouter', 'https://openrouter.ai/api/v1/chat/completions', process.env.OPENROUTER_API_KEY, 'openai/gpt-oss-120b:free', {}]].filter(p => p[2]);
  let err = '';
  for (const [n, u, k, m, x] of P) for (let essai = 0; essai < 8; essai++) {
    try {
      const r = await fetch(u, { method: 'POST', headers: { Authorization: 'Bearer ' + k, 'Content-Type': 'application/json' }, body: JSON.stringify({ model: m, temperature: 0.2, messages, ...x }) });
      if (r.status === 429) { const b = await r.text(); if (/per day|\bTPD\b|\bRPD\b/i.test(b)) { err = n + ' : quota du jour épuisé'; break; }
        const mm = b.match(/try again in\s*(?:(\d+)m)?\s*([\d.]+)s/i), w = Math.min(90, Math.ceil(mm ? (+(mm[1] || 0) * 60 + parseFloat(mm[2])) : 30) + 2);
        log(n + ' : limite par minute, attente ' + w + ' s'); await dodo(w * 1000); continue; }
      if (!r.ok) { err = n + ' : ' + r.status + ' ' + (await r.text()).slice(0, 160); break; }
      const d = await r.json(), t = d.choices?.[0]?.message?.content; if (t) return { t, n }; err = n + ' : réponse vide'; break;
    } catch (e) { err = n + ' : ' + e.message; break; }
  }
  if (process.env.GEMINI_API_KEY) { log((err ? err + ' — ' : '') + 'Gemini prend le relais');
    return { t: await gemini(messages.filter(x => x.role === 'system').map(x => x.content).join('\n'), messages.filter(x => x.role !== 'system').map(x => x.content).join('\n\n')), n: 'Gemini' }; }
  throw new Error(err || 'aucune clé d\'IA dans les secrets GitHub (GROQ_API_KEY ou GEMINI_API_KEY)');
}

try {
  const issue = await gh('/issues/' + ISSUE);
  const m = (issue.body || '').match(/```(?:text)?\n([\s\S]*?)\n```/);
  const brut = (m ? m[1] : issue.body || '').trim();
  const sys = fs.readFileSync('docs/ASSISTANT.md', 'utf8');
  const ps = F.dejaFormat(brut) ? [] : F.parties(F.preBrut(brut)), res = []; let qui = F.dejaFormat(brut) ? 'les règles du studio (script déjà au format, sans IA)' : '';
  for (let i = 0; i < ps.length; i++) {
    log('partie ' + (i + 1) + ' sur ' + ps.length);
    const consigne = 'Partie ' + (i + 1) + ' sur ' + ps.length + ' du script validé. ' + (i === 0 ? '' : 'N\'écris ni TITRE ni lignes NOUVEAU… (déjà faits). ') + (i === ps.length - 1 ? 'C\'est la dernière partie : termine par la FIN.' : 'Ce n\'est pas la dernière partie : n\'écris PAS la FIN.') + ' Mets-la au format exact.\n\n' + ps[i];
    const r = await ia([{ role: 'system', content: sys }, { role: 'user', content: consigne }]); res.push(r.t); qui = qui && qui !== r.n ? qui + ' + ' + r.n : r.n;
  }
  const c = ps.length ? F.nettoyer(F.avant(res.join('\n\n'))) : F.regles_seules(brut); if (ps.length) c.s = F.apres(c.s, brut, c.al);
  let s = c.s; const titre = (s.match(/^TITRE:\s*(.*)$/m) || [, ''])[1];
  if (!titre) s = 'TITRE: ' + issue.title.replace(/^Épisode\s*:\s*/, '') + '\n\n' + s;
  const k = F.controle(s, c.al);
  fs.writeFileSync('script_au_format.txt', s);
  const corps = "### Que faire ?\n\nAperçu des plans d'abord (rapide, environ 10 minutes)\n\n### Script de l'épisode\n\n```text\n" + s + "\n```\n";
  await gh('/issues/' + ISSUE, { method: 'PATCH', body: JSON.stringify({ body: corps, ...(titre ? { title: 'Épisode : ' + titre.replace(/^Les Plans de Bakary\s*[–-]\s*/, '') } : {}) }) });
  const al = k.al.length ? '\n\n**À vérifier :**\n' + k.al.map(x => '- ' + x).join('\n') : '\n\n✅ Aucun problème de format trouvé.';
  await dire('🤖 Script mis au format par ' + qui + '. ' + k.dtxt + '.' + al + '\n\n' + (AUTO === 'true' ? 'L\'aperçu des plans est lancé tout de suite.' : 'Relisez-le dans la page (« Planches et corrections » → « Modifier le script »), puis lancez l\'aperçu.'));
  log('fini');
} catch (e) {
  console.error(e);
  await dire('❌ La mise au format n\'a pas pu être faite : ' + e.message).catch(() => {});
  process.exit(1);
}
