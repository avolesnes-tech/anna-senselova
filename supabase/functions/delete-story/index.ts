// ═══════════════════════════════════════════════════════════════
//  delete-story — Supabase Edge Function
//  Zmaže príbeh podľa delete_token.
//  Volaná z mapa-spomienok.html keď autor klikne na delete link.
// ═══════════════════════════════════════════════════════════════

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const SUPABASE_URL              = Deno.env.get('SUPABASE_URL')!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;

// CORS headers — GitHub Pages origin + lokálny vývoj
const CORS = {
  'Access-Control-Allow-Origin':  'https://avolesnes-tech.github.io',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

Deno.serve(async (req: Request) => {
  // Preflight
  if (req.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: CORS });
  }

  if (req.method !== 'POST') {
    return new Response('Method Not Allowed', { status: 405, headers: CORS });
  }

  try {
    const { token } = await req.json();

    if (!token || typeof token !== 'string' || token.length < 30) {
      return new Response(
        JSON.stringify({ deleted: false, error: 'Invalid token' }),
        { status: 400, headers: { ...CORS, 'Content-Type': 'application/json' } }
      );
    }

    // Použi service role — obíde RLS, zmaže podľa tokenu
    const sb = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
      auth: { persistSession: false }
    });

    const { data, error } = await sb
      .from('stories')
      .delete()
      .eq('delete_token', token)
      .select('id')
      .single();

    if (error || !data) {
      console.log('Story not found for token:', token.slice(0, 8) + '...');
      return new Response(
        JSON.stringify({ deleted: false }),
        { status: 200, headers: { ...CORS, 'Content-Type': 'application/json' } }
      );
    }

    console.log('Story deleted:', data.id);
    return new Response(
      JSON.stringify({ deleted: true, id: data.id }),
      { status: 200, headers: { ...CORS, 'Content-Type': 'application/json' } }
    );

  } catch (err) {
    console.error('Unexpected error:', err);
    return new Response(
      JSON.stringify({ deleted: false, error: 'Internal error' }),
      { status: 500, headers: { ...CORS, 'Content-Type': 'application/json' } }
    );
  }
});
