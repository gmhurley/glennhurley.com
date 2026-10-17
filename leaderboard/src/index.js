// Global leaderboard API for glennhurley.com/hormuz.
//
//   GET  /scores  -> { top: [...] }
//   POST /scores  -> { top: [...], you: { id, rank, name } }
//
// The game runs in the browser, so scores can't be made cheat-proof. This
// keeps them plausible (range checks, minimum run time for the distance),
// rate-limits each IP, and keeps names family-friendly.

const TOP_N = 10;
const FLAGS = ['🇲🇳', '🇲🇭', '🇹🇻'];
const DEFAULT_NAME = 'MV CRUDE JUSTICE';
const REDACTED = 'MV [REDACTED]';

// Mirrors the game's scroll physics: starts at 110 px/s, accelerates 5 px/s²,
// caps at 310 px/s; 180 px per nautical mile. Fastest possible time to reach nm.
function minSecondsFor(nm) {
  const px = nm * 180;
  const rampPx = 110 * 40 + 2.5 * 40 * 40;              // distance covered while accelerating
  if (px <= rampPx) return (-110 + Math.sqrt(110 * 110 + 10 * px)) / 5;
  return 40 + (px - rampPx) / 310;
}

// ── name filter ──────────────────────────────────────────────────
// Matched anywhere in the name (after undoing common letter swaps)...
const BLOCK_ANYWHERE = [
  'fuck', 'shit', 'cunt', 'bitch', 'whore', 'slut', 'porn', 'penis', 'vagina', 'pussy', 'twat',
  'wank', 'jizz', 'dildo', 'asshole', 'bastard', 'nigg', 'nigga', 'faggot', 'retard',
  'kike', 'chink', 'spic', 'tranny', 'dyke', 'hitler', 'nazi', 'kkk', 'rapist', 'molest',
];
// ...or only as a whole word, because they hide inside innocent words
// (bass, cockpit, document, title, grape, sussex).
const BLOCK_WORDS = ['ass', 'cock', 'cum', 'tit', 'tits', 'rape', 'sex', 'fag', 'dick', 'hoe', 'piss', 'crap', 'damn'];
const LEET = { '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't', '8': 'b', '@': 'a', '$': 's', '!': 'i' };

function isOffensive(name) {
  const deleet = name.toLowerCase().replace(/[0134578@$!]/g, c => LEET[c]);
  const squashed = deleet.replace(/[^a-z]/g, '');
  // also catch stretched spellings (fuuuck), but only for words with no
  // double letters of their own, so 'nigg' can't start matching 'night'
  const collapse = t => t.replace(/(.)\1+/g, '$1');
  const squashedC = collapse(squashed);
  if (BLOCK_ANYWHERE.some(w => squashed.includes(w) || (collapse(w) === w && squashedC.includes(w)))) return true;
  const words = deleet.split(/[^a-z]+/).filter(Boolean);
  return words.some(w => BLOCK_WORDS.includes(w));
}

function cleanName(raw) {
  let n = String(raw ?? '').toUpperCase().replace(/[^A-Z0-9 .'\-!?&#]/g, '').replace(/\s+/g, ' ').trim().slice(0, 22);
  if (!n) n = DEFAULT_NAME;
  return isOffensive(n) ? REDACTED : n;
}

// ── helpers ──────────────────────────────────────────────────────
function cors(req, env) {
  const origin = req.headers.get('Origin');
  const allowed = (env.ALLOWED_ORIGINS || '').split(',').map(s => s.trim()).filter(Boolean);
  const h = { 'Vary': 'Origin' };
  if (origin && allowed.includes(origin)) {
    h['Access-Control-Allow-Origin'] = origin;
    h['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS';
    h['Access-Control-Allow-Headers'] = 'Content-Type';
    h['Access-Control-Max-Age'] = '86400';
  }
  return h;
}

function json(data, status, headers) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', ...headers },
  });
}

async function hashIp(ip, salt) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(salt + '|' + ip));
  return [...new Uint8Array(buf)].slice(0, 12).map(b => b.toString(16).padStart(2, '0')).join('');
}

async function topScores(env) {
  const { results } = await env.DB.prepare(
    `SELECT id, name, flag, nm, damage, created_at FROM scores
     ORDER BY nm DESC, damage ASC, created_at ASC LIMIT ?`
  ).bind(TOP_N).all();
  return results;
}

// ── handlers ─────────────────────────────────────────────────────
async function postScore(req, env, headers) {
  let body;
  try { body = await req.json(); } catch { return json({ error: 'bad json' }, 400, headers); }

  const nm = Number(body.nm), damage = Number(body.damage), durationMs = Number(body.durationMs);
  const flag = String(body.flag ?? '');
  if (!Number.isInteger(nm) || nm < 0 || nm > 100) return json({ error: 'bad nm' }, 400, headers);
  if (!Number.isInteger(damage) || damage < 0 || damage > 100) return json({ error: 'bad damage' }, 400, headers);
  if (!FLAGS.includes(flag)) return json({ error: 'bad flag' }, 400, headers);
  if (!Number.isFinite(durationMs) || durationMs < 0 || durationMs > 6 * 3600e3) return json({ error: 'bad duration' }, 400, headers);
  if (durationMs < minSecondsFor(nm) * 1000 * 0.9) return json({ error: 'too fast' }, 422, headers);

  const now = Date.now();
  const ipHash = await hashIp(req.headers.get('CF-Connecting-IP') || 'unknown', env.IP_SALT || 'hormuz-salt');
  const recent = await env.DB.prepare(
    `SELECT COUNT(*) AS n, MAX(created_at) AS last FROM scores WHERE ip_hash = ? AND created_at > ?`
  ).bind(ipHash, now - 86400e3).first();
  // a run takes at least ~4s (deploy, hit something, 2s sinking), so this only stops scripts
  if (recent.last && now - recent.last < 3e3) return json({ error: 'slow down' }, 429, headers);
  if (recent.n >= 100) return json({ error: 'daily limit' }, 429, headers);

  const name = cleanName(body.name);
  const ins = await env.DB.prepare(
    `INSERT INTO scores (name, flag, nm, damage, duration_ms, created_at, ip_hash) VALUES (?, ?, ?, ?, ?, ?, ?)`
  ).bind(name, flag, nm, damage, Math.round(durationMs), now, ipHash).run();
  const id = ins.meta.last_row_id;

  const better = await env.DB.prepare(
    `SELECT COUNT(*) AS n FROM scores
     WHERE nm > ?1 OR (nm = ?1 AND damage < ?2) OR (nm = ?1 AND damage = ?2 AND created_at < ?3)`
  ).bind(nm, damage, now).first();

  return json({ top: await topScores(env), you: { id, rank: better.n + 1, name } }, 201, headers);
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const headers = cors(req, env);
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers });
    if (url.pathname !== '/scores') return json({ error: 'not found' }, 404, headers);
    try {
      if (req.method === 'GET') return json({ top: await topScores(env) }, 200, headers);
      if (req.method === 'POST') return await postScore(req, env, headers);
      return json({ error: 'method not allowed' }, 405, headers);
    } catch (err) {
      console.error(err);
      return json({ error: 'server error' }, 500, headers);
    }
  },
};

// exported for tests
export { cleanName, isOffensive, minSecondsFor };
