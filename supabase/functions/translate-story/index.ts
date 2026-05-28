// ═══════════════════════════════════════════════════════════════
//  translate-story — Supabase Edge Function
//  Preloží príbeh pomocou DeepL API (SK↔EN).
//  DeepL kľúč je uložený ako Supabase secret, nikdy nie v kóde.
// ═══════════════════════════════════════════════════════════════

const DEEPL_API_KEY = Deno.env.get('DEEPL_API_KEY')!;
const DEEPL_URL     = 'https://api-free.deepl.com/v2/translate';

const CORS = {
  'Access-Control-Allow-Origin':  '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, apikey, x-client-info',
};

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: CORS });
  }

  if (req.method !== 'POST') {
    return new Response('Method Not Allowed', { status: 405, headers: CORS });
  }

  let body: { text?: string; source_lang?: string; target_lang?: string };
  try {
    body = await req.json();
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid JSON' }), {
      status: 400, headers: { ...CORS, 'Content-Type': 'application/json' },
    });
  }

  const { text, source_lang, target_lang } = body;

  if (!text || !source_lang || !target_lang) {
    return new Response(JSON.stringify({ error: 'Missing: text, source_lang, target_lang' }), {
      status: 400, headers: { ...CORS, 'Content-Type': 'application/json' },
    });
  }

  if (text.length > 5000) {
    return new Response(JSON.stringify({ error: 'Text too long (max 5000 chars)' }), {
      status: 400, headers: { ...CORS, 'Content-Type': 'application/json' },
    });
  }

  try {
    const deepl = await fetch(DEEPL_URL, {
      method: 'POST',
      headers: {
        'Authorization': `DeepL-Auth-Key ${DEEPL_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text:        [text],
        source_lang: source_lang.toUpperCase(),
        target_lang: target_lang.toUpperCase(),
      }),
    });

    if (!deepl.ok) {
      const err = await deepl.text();
      console.error('DeepL error:', deepl.status, err);
      return new Response(JSON.stringify({ error: 'Translation failed', detail: err }), {
        status: deepl.status, headers: { ...CORS, 'Content-Type': 'application/json' },
      });
    }

    const data  = await deepl.json();
    const translated = data.translations?.[0]?.text ?? '';

    return new Response(JSON.stringify({ translated }), {
      status: 200, headers: { ...CORS, 'Content-Type': 'application/json' },
    });

  } catch (err) {
    console.error('Unexpected error:', err);
    return new Response(JSON.stringify({ error: 'Internal error' }), {
      status: 500, headers: { ...CORS, 'Content-Type': 'application/json' },
    });
  }
});
