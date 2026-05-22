// ═══════════════════════════════════════════════════════════════
//  notify-author — Supabase Edge Function
//  Spustí sa automaticky, keď návštevník odošle kontaktnú správu
//  (INSERT do contact_messages). Pošle email autorovi príbehu cez
//  Resend API. Email odosielateľa zostane skrytý — autor odpisuje
//  na adresu stránky, ktorá správu prepošle ďalej (budúca fáza).
// ═══════════════════════════════════════════════════════════════

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const RESEND_API_KEY      = Deno.env.get('RESEND_API_KEY')!;
const FROM_EMAIL          = Deno.env.get('FROM_EMAIL') ?? 'Mapa Spomienok <noreply@mapaspomienok.sk>';
const SUPABASE_URL        = Deno.env.get('SUPABASE_URL')!;
const SUPABASE_SERVICE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
const SITE_URL            = 'https://mapaspomienok.sk/mapa-spomienok.html';

Deno.serve(async (req: Request) => {
  try {
    if (req.method !== 'POST') {
      return new Response('Method Not Allowed', { status: 405 });
    }

    const payload = await req.json();

    // Spracuj iba INSERT udalosti
    if (payload.type !== 'INSERT') {
      return new Response('OK — not an insert', { status: 200 });
    }

    const msg = payload.record; // nový riadok z contact_messages

    // Honeypot ochrana na úrovni funkcie (druhá vrstva)
    if (msg.honeypot && msg.honeypot.trim() !== '') {
      console.log('Honeypot filled — spam, skipping');
      return new Response('OK — spam filtered', { status: 200 });
    }

    // Načítaj email autora príbehu cez service_role (obíde RLS)
    const sb = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);
    const { data: story, error: storyErr } = await sb
      .from('stories')
      .select('zdielal_email, zdielal_meno, zdielal_priezvisko, predok_meno, predok_priezvisko, obec')
      .eq('id', msg.story_id)
      .single();

    if (storyErr || !story) {
      console.error('Story lookup error:', storyErr);
      return new Response('OK — story not found', { status: 200 });
    }

    const authorEmail = story.zdielal_email?.trim();
    if (!authorEmail) {
      return new Response('OK — author has no email', { status: 200 });
    }

    // Zostav texty
    const predokMeno  = [story.predok_meno, story.predok_priezvisko].filter(Boolean).join(' ');
    const autorMeno   = [story.zdielal_meno, story.zdielal_priezvisko].filter(Boolean).join(' ')
                        || 'milý autor/milá autorka';
    const senderName  = msg.sender_name  || 'Návštevník';
    const senderMsg   = msg.message      || '';
    const storyLink   = `${SITE_URL}#pribeh-${msg.story_id}`;

    const html = `<!DOCTYPE html>
<html lang="sk">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nová správa k vášmu príbehu</title>
</head>
<body style="margin:0;padding:0;background:#f8f4ef;font-family:'Georgia',serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f4ef;padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0" style="background:#fffdf8;border:1px solid #e8dcc8;max-width:560px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:#8b1a1a;padding:28px 40px;text-align:center;">
              <p style="margin:0;color:#f0d080;font-family:'Georgia',serif;font-size:11px;letter-spacing:3px;text-transform:uppercase;">Anna Šenšelová</p>
              <h1 style="margin:8px 0 0;color:#fffdf8;font-family:'Georgia',serif;font-size:22px;font-weight:normal;letter-spacing:1px;">Mapa Spomienok</h1>
            </td>
          </tr>

          <!-- Ornament -->
          <tr>
            <td style="padding:28px 40px 0;text-align:center;">
              <p style="margin:0;color:#c4955a;font-size:20px;letter-spacing:8px;">✦ ✦ ✦</p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:24px 40px 32px;">
              <p style="margin:0 0 16px;color:#2c2416;font-size:16px;line-height:1.7;">
                Milý ${autorMeno},
              </p>
              <p style="margin:0 0 16px;color:#2c2416;font-size:16px;line-height:1.7;">
                niekto si prečítal príbeh <strong>${predokMeno}</strong>${story.obec ? ` z ${story.obec}` : ''} a chce sa s tebou spojiť.
              </p>

              <!-- Správa návštevníka -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 24px;">
                <tr>
                  <td style="background:#f5ede0;border-left:3px solid #c4955a;padding:16px 20px;">
                    <p style="margin:0 0 8px;color:#8a7560;font-size:11px;letter-spacing:2px;text-transform:uppercase;">
                      Správa od ${senderName}
                    </p>
                    <p style="margin:0;color:#2c2416;font-size:15px;line-height:1.7;white-space:pre-wrap;">${senderMsg.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</p>
                  </td>
                </tr>
              </table>

              <p style="margin:0 0 24px;color:#2c2416;font-size:15px;line-height:1.7;">
                Ak chceš odpovedať, napíš nám na
                <a href="mailto:senselovaanna@gmail.com" style="color:#8b1a1a;">senselovaanna@gmail.com</a>
                a správu ti prepošleme. Email odosielateľa zostáva skrytý.
              </p>

              <!-- CTA Button -->
              <table cellpadding="0" cellspacing="0" style="margin:0 auto 28px;">
                <tr>
                  <td style="background:#8b1a1a;border-radius:2px;">
                    <a href="${storyLink}"
                       style="display:inline-block;padding:12px 28px;color:#fffdf8;font-family:'Georgia',serif;font-size:14px;letter-spacing:1px;text-decoration:none;">
                      Zobraziť príbeh na mape →
                    </a>
                  </td>
                </tr>
              </table>

              <p style="margin:0;color:#8a7560;font-size:13px;line-height:1.6;border-top:1px solid #e8dcc8;padding-top:20px;">
                Tento email bol odoslaný, pretože si pri zdieľaní príbehu súhlasil/a s tým, že ťa môžu kontaktovať iní návštevníci.
                Súhlas môžeš kedykoľvek odvolať na
                <a href="mailto:senselovaanna@gmail.com" style="color:#8b1a1a;">senselovaanna@gmail.com</a>.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f0e8d8;padding:16px 40px;text-align:center;border-top:1px solid #e8dcc8;">
              <p style="margin:0;color:#8a7560;font-size:11px;letter-spacing:2px;text-transform:uppercase;">
                Anna Šenšelová · Mapa Spomienok
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>`;

    // Odošli email cez Resend
    const resendRes = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from:    FROM_EMAIL,
        to:      [authorEmail],
        subject: `✦ Niekto si prečítal príbeh ${predokMeno} a píše ti`,
        html,
      }),
    });

    if (!resendRes.ok) {
      const errText = await resendRes.text();
      console.error('Resend API error:', resendRes.status, errText);
      return new Response('Email send failed', { status: 500 });
    }

    const result = await resendRes.json();
    console.log('Notification sent:', result.id, '→', authorEmail);

    // Označ správu ako doručenú
    await sb
      .from('contact_messages')
      .update({ status: 'delivered' })
      .eq('id', msg.id);

    return new Response(JSON.stringify({ sent: true, id: result.id }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });

  } catch (err) {
    console.error('Unexpected error:', err);
    return new Response('Internal error', { status: 500 });
  }
});
