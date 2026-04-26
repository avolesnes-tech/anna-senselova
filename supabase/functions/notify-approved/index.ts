// ═══════════════════════════════════════════════════════════════
//  notify-approved — Supabase Edge Function
//  Spustí sa automaticky, keď admin schváli príbeh (status → approved).
//  Pošle email autorovi cez Resend API.
// ═══════════════════════════════════════════════════════════════

const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY')!;
const FROM_EMAIL     = Deno.env.get('FROM_EMAIL') ?? 'Mapa Spomienok <noreply@anna-senselova.sk>';
const SITE_URL       = 'https://avolesnes-tech.github.io/anna-senselova/mapa-spomienok.html';

Deno.serve(async (req: Request) => {
  try {
    // Supabase Database Webhooks používajú POST s JSON payload
    if (req.method !== 'POST') {
      return new Response('Method Not Allowed', { status: 405 });
    }

    const payload = await req.json();

    // Spracuj iba UPDATE udalosti
    if (payload.type !== 'UPDATE') {
      return new Response('OK — not an update', { status: 200 });
    }

    const newRow = payload.record;
    const oldRow = payload.old_record;

    // Pokračuj iba ak sa status zmenil z pending → approved
    if (newRow?.status !== 'approved' || oldRow?.status === 'approved') {
      return new Response('OK — status not changed to approved', { status: 200 });
    }

    // Pokračuj iba ak má autor email
    const recipientEmail = newRow?.zdielal_email?.trim();
    if (!recipientEmail) {
      return new Response('OK — no email address', { status: 200 });
    }

    // Zostav texty pre email
    const predokMeno = [newRow.predok_meno, newRow.predok_priezvisko]
      .filter(Boolean).join(' ');
    const autorMeno  = [newRow.zdielal_meno, newRow.zdielal_priezvisko]
      .filter(Boolean).join(' ') || 'milý prispievateľ/milá prispievateľka';
    const obec       = newRow.obec || '';
    const storyLink  = newRow.id ? `${SITE_URL}#pribeh-${newRow.id}` : SITE_URL;

    // HTML email — v duchu dizajnu stránky
    const html = `<!DOCTYPE html>
<html lang="sk">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Príbeh ${predokMeno} je na mape</title>
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
                príbeh <strong>${predokMeno}</strong>${obec ? ` z ${obec}` : ''} sme schválili a od tejto chvíle je súčasťou Mapy Spomienok.
              </p>
              <p style="margin:0 0 28px;color:#2c2416;font-size:16px;line-height:1.7;">
                Ďakujeme, že si pomohol/a zachovať kúsok Slovenska pre ďalšie generácie.
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
                Tento email bol odoslaný, pretože si uviedol/a svoju e-mailovú adresu pri odosielaní príbehu na
                <a href="${SITE_URL}" style="color:#8b1a1a;">anna-senselova.sk</a>.
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
        to:      [recipientEmail],
        subject: `Príbeh ${predokMeno} je na mape ✦`,
        html,
      }),
    });

    if (!resendRes.ok) {
      const errText = await resendRes.text();
      console.error('Resend API error:', resendRes.status, errText);
      return new Response('Email send failed', { status: 500 });
    }

    const result = await resendRes.json();
    console.log('Email sent:', result.id, '→', recipientEmail);
    return new Response(JSON.stringify({ sent: true, id: result.id }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });

  } catch (err) {
    console.error('Unexpected error:', err);
    return new Response('Internal error', { status: 500 });
  }
});
