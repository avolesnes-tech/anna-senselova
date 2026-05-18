#!/usr/bin/env python3
"""
Generate English translations of selected pages and save them to the en/ directory.
Pages handled: blog.html, mapa-spomienok.html, anna-senselova.html
"""

import os
import re

BASE = "/Users/annalockwoodova/Documents/GitHub/anna-senselova"
EN_DIR = os.path.join(BASE, "en")
os.makedirs(EN_DIR, exist_ok=True)

# ── helpers ──────────────────────────────────────────────────────────────────

def prefix_local_assets(html):
    """
    Prefix all local asset paths with ../
    CDN (http/https) links are left alone.
    Page-link hrefs (*.html not in assets/) are left alone.
    """

    def should_prefix(val):
        if not val:
            return False
        if val.startswith('http') or val.startswith('//') or val.startswith('../') or val.startswith('data:'):
            return False
        if val.startswith('#') or val.startswith('mailto'):
            return False
        return True

    # 1. href="..." — skip HTML page links
    def fix_link_href(m):
        val = m.group(1)
        if not should_prefix(val):
            return m.group(0)
        if val.endswith('.html') or '.html#' in val:
            return m.group(0)
        return 'href="../' + val + '"'

    html = re.sub(r'href="([^"]*)"', fix_link_href, html)

    # 2. src="..."
    def fix_src(m):
        val = m.group(1)
        if not should_prefix(val):
            return m.group(0)
        return 'src="../' + val + '"'

    html = re.sub(r'src="([^"]*)"', fix_src, html)

    # 3. srcset="..."
    def fix_srcset(m):
        val = m.group(1)
        if not should_prefix(val):
            return m.group(0)
        return 'srcset="../' + val + '"'

    html = re.sub(r'srcset="([^"]*)"', fix_srcset, html)

    return html


def set_lang_en(html):
    return html.replace('<html lang="sk">', '<html lang="en">', 1)


def add_hreflang(html, sk_url, en_url):
    """Insert hreflang link tags just before </head>."""
    hreflang = (
        f'<link rel="alternate" hreflang="sk" href="{sk_url}">\n'
        f'<link rel="alternate" hreflang="en" href="{en_url}">\n'
        f'<link rel="alternate" hreflang="x-default" href="{sk_url}">\n'
    )
    return html.replace('</head>', hreflang + '</head>', 1)


def replace_lang_switch(html, sk_href, pattern_old_href):
    """Replace the lang-switch div so EN page shows SK link and EN as current."""
    new_switch = (
        '<div class="lang-switch" aria-label="Language version">\n'
        f'    <a href="{sk_href}" class="lang-link" lang="sk" hreflang="sk">SK</a>\n'
        '    <span class="lang-sep" aria-hidden="true">|</span>\n'
        '    <span class="lang-current" aria-current="true">EN</span>\n'
        '  </div>'
    )
    html = re.sub(
        r'<div class="lang-switch"[^>]*>.*?</div>',
        new_switch,
        html,
        count=1,
        flags=re.DOTALL
    )
    return html


# ── BLOG translations ─────────────────────────────────────────────────────────

def translate_blog(html):
    replacements = [
        ('Blog — Anna Šenšelová', 'Blog — Anna Šenšelová'),
        ('Blog Anny Lockwoodovej o rodinnej histórii, výšivkách, krojoch a príbehoch, ktoré nechceme pustiť do zabudnutia.',
         "Anna Lockwoodová's blog about family history, embroideries, folk costumes, and stories we don't want to let fall into oblivion."),
        ('Blog — Vyšívané poklady Anny Šenšelovej', 'Blog — The Embroidered Treasures of Anna Šenšelová'),
        ('Príbehy o rodinnej histórii, výšivkách a ženách, ktoré boli pred nami.',
         'Stories about family history, embroideries, and the women who came before us.'),
        ('Preskočiť na obsah', 'Skip to content'),
        ('aria-label="Mapa Spomienok – domov"', 'aria-label="Map of Memories – home"'),
        ('aria-label="Otvoriť menu"', 'aria-label="Open menu"'),
        ('<span class="dropdown-label">Príbeh</span>', '<span class="dropdown-label">Story</span>'),
        ('<span class="dropdown-label">Galéria</span>', '<span class="dropdown-label">Gallery</span>'),
        ('Príbeh ▾', 'Story ▾'),
        ('Galéria ▾', 'Gallery ▾'),
        ('>Mapa spomienok<', '>Map of Memories<'),
        ('>Kontakt<', '>Contact<'),
        ("Vzorkovník výšiviek Anny Šenšelovej", "Sample Book of Anna Šenšelová's Embroideries"),
        ('Iné ľudové výšivky a odev', 'Other Folk Embroideries and Dress'),
        ('Krojované bábiky', 'Folk Costume Dolls'),
        ('>Domov<', '>Home<'),
        ('Zápisky · Príbehy · Zamyslenia', 'Notes · Stories · Reflections'),
        ('Miesto, kde s vami budem zdieľať moju cestu pátraním po vlastnej rodinnej histórii, po výšivkách, po Lipe a Živene — a možno aj ďalších pokladoch, ktoré mi pri tom cvrnknú do nosa.',
         "A place where I will share with you my journey searching through my own family history — embroideries, Lipa, Živena — and perhaps other treasures that catch my eye along the way."),
        ('>Rodinná história<', '>Family history<'),
        ('Kde som hľadala a čo som našla', 'Where I searched and what I found'),
        ("Aké zdroje mi pomohli odhaliť históriu mojej rodiny? Od rodinných publikácií a digitálnych archívov až po vzdialených príbuzných a folklórnych nadšencov.",
         "What sources helped me uncover my family's history? From family publications and digital archives to distant relatives and folklore enthusiasts."),
        ('Máj 2026 · 8 min čítania', 'May 2026 · 8 min read'),
        ('>Čítať →<', '>Read →<'),
        ('Pozor: pátranie po minulosti vás vcucne!', 'Warning: searching for the past will pull you in!'),
        ('Záujem o rodinnú históriu vniesol do môjho života úplne nový rozmer. Upozorňujem na hlavné riziko: pátranie vás vcucne do víru, ktorý sa len ťažko zastaví.',
         'An interest in family history brought a whole new dimension to my life. I warn you: the search will pull you into a whirlpool that is very hard to stop.'),
        ('Apríl 2026 · 6 min čítania', 'April 2026 · 6 min read'),
        ('>Príbeh<', '>Story<'),
        ('Galéria & Mapa', 'Gallery & Map'),
        ('Vzorkovník výšiviek', 'Embroidery Sample Book'),
        ('Ľudové výšivky a odev', 'Folk Embroideries and Dress'),
        ('Mapa spomienok', 'Map of Memories'),
        ('Spojme sa', 'Get in touch'),
        ('Vytvorené s láskou a úctou k predošlým generáciám.', 'Created with love and respect for past generations.'),
        ('aria-label="Mapa spomienok na Facebooku"', 'aria-label="Map of Memories on Facebook"'),
        ('aria-label="Mapa spomienok na Instagrame"', 'aria-label="Map of Memories on Instagram"'),
        ('Ochrana osobných údajov', 'Privacy policy'),
        ('Zbierka výšiviek, bábik a pozostalosti po rodine Šenšelovcov nie je mojím osobným vlastníctvom — je dedičstvom celej rodiny. Výšivky, bábiky ani kroje nie sú na predaj.',
         'The collection of embroideries, dolls, and personal effects of the Šenšel family is not my personal property — it is the heritage of the whole family. The embroideries, dolls, and folk costumes are not for sale.'),
        ('aria-labelledby="gdpr-title"', 'aria-labelledby="gdpr-title"'),
        ('aria-label="Zavrieť"', 'aria-label="Close"'),
        ('<h2 id="gdpr-title">Ochrana osobných údajov</h2>', '<h2 id="gdpr-title">Privacy policy</h2>'),
        ('<strong>Prevádzkovateľ webu:</strong>', '<strong>Website operator:</strong>'),
        ('Táto stránka je nekomerčný informačný web vytvorený vo voľnom čase. Nevznikajú z nej žiadne obchodné záväzky.',
         'This website is a non-commercial informational site created in my free time. No commercial obligations arise from it.'),
        ('<strong>Kontaktný formulár:</strong> Ak mi napíšete prostredníctvom kontaktného formulára, spracúvam tieto údaje: meno, e-mailová adresa a text správy. Slúžia výlučne na to, aby som vám mohla odpovedať. Údaje nie sú zdieľané s tretími stranami a po vybavení komunikácie ich vymažem.',
         '<strong>Contact form:</strong> If you write to me via the contact form, I process the following data: name, email address, and the message text. These are used solely to reply to you. Data are not shared with third parties and will be deleted once the communication is resolved.'),
        ('<strong>Vaše práva:</strong> Máte právo požiadať o prístup k svojim údajom, ich opravu alebo vymazanie. Stačí napísať na vyššie uvedený e-mail.',
         '<strong>Your rights:</strong> You have the right to request access to your data, its correction, or deletion. Simply write to the email address above.'),
        ('<strong>Cookies a fonty:</strong> Web nepoužíva sledovacie ani analytické cookies. Písma (fonty) sú hostované priamo na tomto serveri — žiadne dáta sa neposielajú do Google ani iným tretím stranám.',
         '<strong>Cookies and fonts:</strong> This site does not use tracking or analytical cookies. Fonts are hosted directly on this server — no data is sent to Google or any other third parties.'),
        ('aria-label="Jazyková verzia"', 'aria-label="Language version"'),
    ]

    for old, new in replacements:
        html = html.replace(old, new)

    return html


# ── MAPA-SPOMIENOK translations ───────────────────────────────────────────────

def translate_mapa(html):
    replacements = [
        ('Mapa spomienok — Anna Šenšelová', 'Map of Memories — Anna Šenšelová'),
        ('Digitálna mapa príbehov predkov. Zdieľaj spomienky na svojich starých a prastarých rodičov a pomôž zachovať živú pamäť Slovenska.',
         "A digital map of ancestors' stories. Share memories of your grandparents and great-grandparents and help preserve the living memory of Slovakia."),
        ('Každá rodina nesie kúsok histórie Slovenska. Pridaj príbeh svojho predka na mapu.',
         "Every family carries a piece of Slovakia's history. Add your ancestor's story to the map."),
        ('Preskočiť na obsah', 'Skip to content'),
        ('aria-label="Mapa Spomienok – domov"', 'aria-label="Map of Memories – home"'),
        ('aria-label="Otvoriť menu"', 'aria-label="Open menu"'),
        ('<span class="dropdown-label">Príbeh</span>', '<span class="dropdown-label">Story</span>'),
        ('<span class="dropdown-label">Galéria</span>', '<span class="dropdown-label">Gallery</span>'),
        ('Príbeh ▾', 'Story ▾'),
        ('Galéria ▾', 'Gallery ▾'),
        ('>Mapa spomienok<', '>Map of Memories<'),
        ('>Kontakt<', '>Contact<'),
        ("Vzorkovník výšiviek Anny Šenšelovej", "Sample Book of Anna Šenšelová's Embroideries"),
        ('Iné ľudové výšivky a odev', 'Other Folk Embroideries and Dress'),
        ('Krojované bábiky', 'Folk Costume Dolls'),
        ('aria-label="Jazyková verzia"', 'aria-label="Language version"'),
        ('<h1 class="hero-title">Mapa spomienok</h1>', '<h1 class="hero-title">Map of Memories</h1>'),
        ('Každá rodina nesie v sebe kúsok histórie Slovenska.<br>Pomôž nám ho zachovať pre budúce generácie.',
         "Every family carries within it a piece of Slovakia's history.<br>Help us preserve it for future generations."),
        ('>Zdieľaj príbeh<', '>Share a story<'),
        ('>Prezerať príbehy<', '>Browse stories<'),
        ('>príbehov<', '>stories<'),
        ('>obcí<', '>villages<'),
        ('>krajov<', '>regions<'),
        ('Objavovanie minulosti mojich predkov neskutočne obohatilo môj život. Chcela by som k tomu inšpirovať aj ďalších — lebo je to taký jedinečný zážitok, a pritom ho môže prežiť každý z nás. Umožní nám zachovať tieto odkazy pokrvnej línie aj ďalším generáciám.<br><br>',
         'Discovering the past of my ancestors has incredibly enriched my life. I would love to inspire others to do the same — because it is such a unique experience, and yet it is available to every one of us. It allows us to preserve these threads of lineage for future generations.<br><br>'),
        ('Ak príbehy svojich koreňov poznáte, budem rada, keď sa s nimi podelíte a spoločne zmapujeme Slovensko plné výnimočných príbehov. A ak ich nepoznáte — možno som vás motivovala.',
         "If you know the stories of your roots, I will be glad when you share them, so together we can map a Slovakia full of extraordinary stories. And if you don't know them — perhaps I've given you motivation to find out."),
        ('>Vráťte sa k našej mape čoskoro.<', '>Come back to our map soon.<'),
        ('aria-label="Ako pridať príbeh do mapy"', 'aria-label="How to add a story to the map"'),
        ('>Ako sa zapojiť<', '>How to get involved<'),
        ('Iste aj vo vašej rodine sú príbehy,<br>ktoré stoja za zachovanie',
         'Surely your family too has stories<br>worth preserving'),
        ('Nemusíte o svojich predkoch vedieť všetky detaily. Stačí aj malý fragment —\n      čomu sa venovali, kde žili, čím si ich ľudia pamätajú.',
         "You don't need to know every detail about your ancestors. Even a small fragment will do —\n      what they did, where they lived, how people remember them."),
        ('>Čo zdieľať<', '>What to share<'),
        ('Remeslá, hospodárstvo, vzdelanie. Či strávili celý život na jednom mieste alebo cestovali. Čím si ich rodina pamätá. Stačí pár viet — ale kľudne aj viac.',
         'Crafts, farming, education. Whether they spent their whole life in one place or travelled. How their family remembers them. A few sentences are enough — but feel free to write more.'),
        ('>Fotografie<', '>Photographs<'),
        ('Ak máte staré fotografie a chcete sa s nimi podeliť, nahrajte ich k príbehu — maximálne 3 fotky. Stará fotografia dodá príbehu tvár, ale nie je podmienkou.',
         'If you have old photographs and would like to share them, upload them with the story — up to 3 photos. An old photograph gives a face to the story, but it is not required.'),
        ('>Mapa a vyhľadávanie<', '>Map and search<'),
        ('V mape nájdete príbehy podľa kraja, obdobia alebo priezviska. Váš príspevok sa na stránke objaví po schválení administrátorom.',
         'In the map you can find stories by region, period, or surname. Your submission will appear on the site after approval by an administrator.'),
        ('Formulár pre zdieľanie príbehu nájdete pod mapou ↓', 'The form for sharing a story is below the map ↓'),
        ('aria-label="Interaktívna mapa príbehov"', 'aria-label="Interactive map of stories"'),
        ('role="search" aria-label="Filter príbehov"', 'role="search" aria-label="Filter stories"'),
        ('placeholder="Hľadaj podľa priezviska…"', 'placeholder="Search by surname…"'),
        ('aria-label="Vyhľadávanie podľa priezviska"', 'aria-label="Search by surname"'),
        ('aria-label="Filtrovať podľa kraja"', 'aria-label="Filter by region"'),
        ('<option value="">Všetky kraje</option>', '<option value="">All regions</option>'),
        ('aria-label="Filtrovať podľa obdobia"', 'aria-label="Filter by period"'),
        ('<option value="">Všetky obdobia</option>', '<option value="">All periods</option>'),
        ('<option value="pred_1900">Pred rokom 1900</option>', '<option value="pred_1900">Before 1900</option>'),
        ('<option value="medzivojnove">Medzivojnové (1918–1939)</option>', '<option value="medzivojnove">Interwar period (1918–1939)</option>'),
        ('<option value="vojnove">Vojnové roky (1939–1945)</option>', '<option value="vojnove">War years (1939–1945)</option>'),
        ('<option value="povojnove">Povojnové (1945–1968)</option>', '<option value="povojnove">Post-war (1945–1968)</option>'),
        ('aria-label="Zoznam príbehov"', 'aria-label="List of stories"'),
        ("aria-label=\"Formulár pre zdieľanie príbehu predka\"", "aria-label=\"Form for sharing an ancestor's story\""),
        ('>Príbeh<', '>Story<'),
        ('Galéria & Mapa', 'Gallery & Map'),
        ('Vzorkovník výšiviek', 'Embroidery Sample Book'),
        ('Ľudové výšivky a odev', 'Folk Embroideries and Dress'),
        ('Mapa spomienok', 'Map of Memories'),
        ('Spojme sa', 'Get in touch'),
        ('Vytvorené s láskou a úctou k predošlým generáciám.', 'Created with love and respect for past generations.'),
        ('aria-label="Mapa spomienok na Facebooku"', 'aria-label="Map of Memories on Facebook"'),
        ('aria-label="Mapa spomienok na Instagrame"', 'aria-label="Map of Memories on Instagram"'),
        ('Ochrana osobných údajov', 'Privacy policy'),
        ('Zbierka výšiviek, bábik a pozostalosti po rodine Šenšelovcov nie je mojím osobným vlastníctvom — je dedičstvom celej rodiny. Výšivky, bábiky ani kroje nie sú na predaj.',
         'The collection of embroideries, dolls, and personal effects of the Šenšel family is not my personal property — it is the heritage of the whole family. The embroideries, dolls, and folk costumes are not for sale.'),
        ('aria-label="Zavrieť"', 'aria-label="Close"'),
        ('<h2 id="gdpr-title">Ochrana osobných údajov</h2>', '<h2 id="gdpr-title">Privacy policy</h2>'),
        ('<strong>Prevádzkovateľ webu:</strong>', '<strong>Website operator:</strong>'),
        ('Táto stránka je nekomerčný informačný web vytvorený vo voľnom čase. Nevznikajú z nej žiadne obchodné záväzky.',
         'This website is a non-commercial informational site created in my free time. No commercial obligations arise from it.'),
        ('<strong>Kontaktný formulár:</strong> Ak mi napíšete prostredníctvom kontaktného formulára, spracúvam tieto údaje: meno, e-mailová adresa a text správy. Slúžia výlučne na to, aby som vám mohla odpovedať. Údaje nie sú zdieľané s tretími stranami a po vybavení komunikácie ich vymažem.',
         '<strong>Contact form:</strong> If you write to me via the contact form, I process the following data: name, email address, and the message text. These are used solely to reply to you. Data are not shared with third parties and will be deleted once the communication is resolved.'),
        ('<strong>Vaše práva:</strong> Máte právo požiadať o prístup k svojim údajom, ich opravu alebo vymazanie. Stačí napísať na vyššie uvedený e-mail.',
         '<strong>Your rights:</strong> You have the right to request access to your data, its correction, or deletion. Simply write to the email address above.'),
        ('<strong>Cookies a fonty:</strong> Web nepoužíva sledovacie ani analytické cookies. Písma (fonty) sú hostované priamo na tomto serveri — žiadne dáta sa neposielajú do Google ani iným tretím stranám.',
         '<strong>Cookies and fonts:</strong> This site does not use tracking or analytical cookies. Fonts are hosted directly on this server — no data is sent to Google or any other third parties.'),
    ]

    for old, new in replacements:
        html = html.replace(old, new)

    js_translations = [
        ("'príbehov'", "'stories'"),
        ('"príbehov"', '"stories"'),
        ("'príbeh'", "'story'"),
        ('"príbeh"', '"story"'),
        ("'Existujúce príbehy'", "'Existing stories'"),
        ('"Existujúce príbehy"', '"Existing stories"'),
        ("'Nové príbehy'", "'New stories'"),
        ('"Nové príbehy"', '"New stories"'),
        ("'Zdieľal/a:'", "'Shared by:'"),
        ('"Zdieľal/a:"', '"Shared by:"'),
        ("'Zdieľaj:'", "'Share:'"),
        ('"Zdieľaj:"', '"Share:"'),
        ("'Skopírovať odkaz'", "'Copy link'"),
        ('"Skopírovať odkaz"', '"Copy link"'),
        ("'Odkaz skopírovaný!'", "'Link copied!'"),
        ('"Odkaz skopírovaný!"', '"Link copied!"'),
        ("'Otvoriť v galérii'", "'Open in gallery'"),
        ('"Otvoriť v galérii"', '"Open in gallery"'),
        ("'Meno a priezvisko'", "'Full name'"),
        ('"Meno a priezvisko"', '"Full name"'),
        ("'Odkiaľ pochádzal/a'", "'Place of origin'"),
        ('"Odkiaľ pochádzal/a"', '"Place of origin"'),
        ("'Príbeh'", "'Story'"),
        ('"Príbeh"', '"Story"'),
        ("'Odoslať'", "'Submit'"),
        ('"Odoslať"', '"Submit"'),
        ("'Zverejniť'", "'Publish'"),
        ('"Zverejniť"', '"Publish"'),
        ("'Príbeh bol odoslaný!'", "'Story submitted!'"),
        ('"Príbeh bol odoslaný!"', '"Story submitted!"'),
        ("'Ďakujeme za váš príspevok.'", "'Thank you for your contribution.'"),
        ('"Ďakujeme za váš príspevok."', '"Thank you for your contribution."'),
        ("'Žiadne príbehy sa nenašli.'", "'No stories found.'"),
        ('"Žiadne príbehy sa nenašli."', '"No stories found."'),
        ("'Skúste zmeniť filtre.'", "'Try adjusting the filters.'"),
        ('"Skúste zmeniť filtre."', '"Try adjusting the filters."'),
        ("nájdených príbehov", "stories found"),
        ("nájdený príbeh", "story found"),
        ("nájdené príbehy", "stories found"),
        ("'+ Pridať ďalšieho predka'", "'+ Add another ancestor'"),
        ('"+ Pridať ďalšieho predka"', '"+ Add another ancestor"'),
        ("'Odstrániť'", "'Remove'"),
        ('"Odstrániť"', '"Remove"'),
        ("'Druhý predok'", "'Second ancestor'"),
        ('"Druhý predok"', '"Second ancestor"'),
        ("'Nahrať fotografiu'", "'Upload a photograph'"),
        ('"Nahrať fotografiu"', '"Upload a photograph"'),
        ("'alebo pretiahnite súbor sem'", "'or drag a file here'"),
        ('"alebo pretiahnite súbor sem"', '"or drag a file here"'),
    ]

    for old, new in js_translations:
        html = html.replace(old, new)

    return html


def translate_mapa_html_visible(html):
    """Translate visible HTML text in mapa-spomienok that is in actual HTML (not JS)."""
    html = html.replace('Zdieľajte príbeh predka', "Share an ancestor's story")
    html = html.replace('Digitálna pamäť národa', "The nation's digital memory")
    html = html.replace('>Meno a priezvisko<', '>Full name<')
    html = html.replace('Meno a priezvisko predka', "Ancestor's full name")
    html = html.replace('>Odkiaľ pochádzal/a<', '>Place of origin<')
    html = html.replace('>Príbeh<', '>Story<')
    html = html.replace('>Odoslať<', '>Submit<')
    html = html.replace('>Zverejniť<', '>Publish<')
    html = html.replace('predok', 'ancestor')
    html = html.replace('priezvisko', 'surname')
    html = html.replace('región', 'region')
    html = html.replace('Príbehy z mapy', 'Stories from the map')
    html = html.replace('Príbehy, ktoré nechceme zabudnúť', "Stories we don't want to forget")
    html = html.replace('Načítať ďalšie', 'Load more')
    html = html.replace('Žiadne príbehy', 'No stories')
    return html


# ── ANNA-SENSELOVA translations ───────────────────────────────────────────────

def translate_anna_senselova(html):
    replacements = [
        # title / meta
        ('Anna Šenšelová – Vyšívané poklady',
         'Anna Šenšelová – Embroidered Treasures'),
        ('Príbeh Anny Šenšelovej (1882–1976) — ženy, ktorá 42 rokov zachraňovala slovenské výšivkárstvo ako riaditeľka martinskej Lipy. Rodostrom, Zástava slobody a rodinná história.',
         'The story of Anna Šenšelová (1882–1976) — a woman who for 42 years preserved Slovak embroidery as director of the Lipa association in Martin. Family tree, Flag of Freedom, and family history.'),
        ('Príbeh ženy, ktorá 42 rokov zachraňovala slovenské výšivkárstvo. Pešo prechodila slovenské dediny, hľadala vyšívačky a budovala sieť remeselníčok pod hlavičkou spolku Lipa.',
         'The story of a woman who for 42 years preserved Slovak embroidery. She walked through Slovak villages, sought out embroiderers, and built a network of craftswomen under the Lipa association.'),
        ('Anna Šenšelová – rodinná fotografia', 'Anna Šenšelová – family photograph'),
        # skip-link
        ('Preskočiť na obsah', 'Skip to content'),
        # nav
        ('aria-label="Mapa Spomienok – domov"', 'aria-label="Map of Memories – home"'),
        ('aria-label="Otvoriť menu"', 'aria-label="Open menu"'),
        ('<span class="dropdown-label">Príbeh</span>', '<span class="dropdown-label">Story</span>'),
        ('<span class="dropdown-label">Galéria</span>', '<span class="dropdown-label">Gallery</span>'),
        ('Príbeh ▾', 'Story ▾'),
        ('Galéria ▾', 'Gallery ▾'),
        ('>Mapa spomienok<', '>Map of Memories<'),
        ('>Kontakt<', '>Contact<'),
        ("Vzorkovník výšiviek Anny Šenšelovej", "Sample Book of Anna Šenšelová's Embroideries"),
        ('Iné ľudové výšivky a odev', 'Other Folk Embroideries and Dress'),
        ('Krojované bábiky', 'Folk Costume Dolls'),
        ('aria-label="Jazyková verzia"', 'aria-label="Language version"'),
        # hero
        ('aria-label="Úvod"', 'aria-label="Introduction"'),
        ('data-caption="Rodinná fotografia"', 'data-caption="Family photograph"'),
        ('alt="Rodinná fotografia"', 'alt="Family photograph"'),
        ('data-caption="Rodinné stretnutie"', 'data-caption="Family gathering"'),
        ('alt="Rodinné stretnutie"', 'alt="Family gathering"'),
        ('data-caption="Anna Šenšelová s rodinou"', 'data-caption="Anna Šenšelová with her family"'),
        ('alt="Anna Šenšelová s rodinou"', 'alt="Anna Šenšelová with her family"'),
        ('data-caption="Rodinná fotografia r. 1894 — Anna vľavo hore"',
         'data-caption="Family photograph c. 1894 — Anna top left"'),
        ('alt="Rodinná fotografia r. 1894"', 'alt="Family photograph c. 1894"'),
        ('data-caption="Rodinná fotografia r. 1905 — Anna vpravo dole"',
         'data-caption="Family photograph c. 1905 — Anna bottom right"'),
        ('alt="Rodinná fotografia r. 1905"', 'alt="Family photograph c. 1905"'),
        ('<p class="carousel-label">Príbeh</p>', '<p class="carousel-label">Story</p>'),
        ('<p class="carousel-caption" id="carouselCaption">Rodinná fotografia</p>',
         '<p class="carousel-caption" id="carouselCaption">Family photograph</p>'),
        ('aria-label="Predchádzajúca"', 'aria-label="Previous"'),
        ('aria-label="Nasledujúca"', 'aria-label="Next"'),
        # pribeh section
        ('<h2>Skromná žena s vášňou pre slovenskú výšivku</h2>',
         '<h2>A modest woman with a passion for Slovak embroidery</h2>'),
        ('Anna Šenšelová (1882 – 1976) bola výnimočná, nesmierne skromná a húževnatá žena, ktorej život sa stal neoddeliteľnou súčasťou histórie slovenského výšivkárstva. Narodila sa na Štedrý deň v Očovej v rodine národovcov a už od detstva ju sprevádzala láska k slovenskej kultúre.',
         'Anna Šenšelová (1882–1976) was an exceptional, deeply modest, and tenacious woman whose life became inseparable from the history of Slovak embroidery. She was born on Christmas Eve in Očová, into a family of Slovak patriots, and from childhood she was accompanied by a love of Slovak culture.'),
        ('Hoci jej pôvodným snom bola botanika a práca v záhrade, osud ju v roku 1910 zavial do Martina. Práve tam vznikala legendárna <em>Lipa</em>, účastinárska spoločnosť pre ľudový priemysel, a Anna bola povolaná, aby sa stala jej hybnou silou.',
         'Although her original dream was botany and gardening, fate brought her to Martin in 1910. It was there that the legendary <em>Lipa</em> — a cooperative society for folk industry — was being founded, and Anna was called to become its driving force.'),
        ('Aby svojej práci rozumela čo najlepšie, vo svojich 28 rokoch zasadla do školských lavíc v Prahe, kde si osvojila najrôznejšie techniky vyšívania na Mestskej priemyselnej škole v Prahe. Po návrate sa naplno oddala záchrane tradícií:',
         'To understand her work as thoroughly as possible, at the age of 28 she returned to the classroom in Prague, mastering a wide range of embroidery techniques at the Municipal Industrial School. On her return, she devoted herself entirely to preserving traditions:'),
        ('Trpezlivo študovala a odkresľovala staré vzory, aby sa na ne nezabudlo. Veľa cestovala po Slovensku a získavala kontakty a dôveru vyšívačiek, ktoré ďalej pracovali pre Lipu a zachovávali prísne stanovené štandardy slovenského ornamentu.',
         'She patiently studied and copied old patterns so they would not be forgotten. She travelled extensively across Slovakia, building relationships and earning the trust of embroiderers who worked for Lipa and maintained the strict standards of Slovak ornament.'),
        ('Osobne dohliadala na kvalitu každej jednej dečky, obrusu, či kroja — dbala na zachovanie čistoty a pôvodného vzoru.',
         'She personally oversaw the quality of every doily, tablecloth, and folk costume — ensuring the purity and authenticity of the original pattern.'),
        ('V okolí Trnavy pochodila Hrnčiarovce, Ružindol, Gocnod (dnešný Cífer) a Récu. V Čataji sa Lipa neuchytila, pretože tam mal vyšívačskú školu spolok Izabella. V okolí Zvolena boli vyšívačky v Slatine — s charakteristickou krivou ihlou, vyšívali bez predlohy — a v Detve. Vyšívačské obce boli aj Vajnory a Grob. V Hontianskej župe Horný a Dolný Dačov Lom, Litava, Bzovík a Trpín. V niektorých oblastiach Hontu vyšívačky pre Lipu nepracovali — tu zbierala výšivky a vzory Drahotína Kardossová, rod. Križková. Ak do Lipy prišla chybná práca od vyšívačiek, musela ju Anna sama opraviť alebo predať za nižšiu cenu.',
         "Around Trnava she walked through Hrnčiarovce, Ružindol, Gocnod (today's Cífer), and Réca. Lipa never took root in Čataj, where the Izabella association ran its own embroidery school. Around Zvolen, embroiderers worked in Slatina — famous for their distinctive curved needle, stitching without a template — and in Detva. The embroidery villages also included Vajnory and Grob. In the Hont region: Horný and Dolný Dačov Lom, Litava, Bzovík, and Trpín. In some parts of Hont the embroiderers did not work for Lipa — there it was Drahotína Kardossová, née Križková, who collected embroideries and patterns. Whenever faulty work arrived from the embroiderers, Anna had to repair it herself or sell it at a reduced price."),
        ('Anna zbierala staré vzorky výšiviek a podľa nich dbala na zachovávanie tradičného vzoru. Dozerala, aby sa ženy nenechali strhnúť módnymi trendmi z prichádzajúcich časopisov. Vzorník výšiviek, ktorý si dala vyšiť na Dačovom Lome, predala Slovenskému národnému múzeu v Martine.',
         'Anna collected old embroidery samples and used them to ensure that traditional patterns were preserved. She watched closely to make sure the women were not swept along by the fashion trends arriving in new magazines. The embroidery sample book she had stitched in Dačov Lom she later sold to the Slovak National Museum in Martin.'),
        ('Pod Anniným vedením Lipa získavala ocenenia na medzinárodných výstavách od Viedne až po Košice. Anna Šenšelová stála na čele tohto podniku až do jeho zániku v roku 1951.',
         "Under Anna's leadership, Lipa won awards at international exhibitions from Vienna to Košice. Anna Šenšelová remained at the head of the enterprise until its dissolution in 1951."),
        ('Spomienky z rodiny · Oľga Kapustová', 'Family memories · Oľga Kapustová'),
        ('Oľga Kapustová, ďalšia Annina praneter, si ju pamätá ako tichú, skromnú a pracovitú ženu — „tetinku", ako ju deti v rodine volali. Najradšej trávila čas v záhradke pri dome a keď dozreli maliny, posielala deti von s miskami, nech sa napasú. Niekedy im dala peniaze a poslala ich do obchodu kúpiť zmrzlinu. Len tak, aby im spravila radosť. Žila skromne a úsporne, odkladala si peniaze na starobu. Menová reforma v 50. rokoch však jej úspory znehodnotila a Anna prišla o byt, v ktorom žila. Ujala sa jej sestra Oľga s rodinou, kde Anna prežila posledné roky života.',
         'Oľga Kapustová, another of Anna\'s great-nieces, remembers her as a quiet, modest, and hardworking woman — "tetinka", as the children in the family called her. She loved spending time in her garden, and when the raspberries ripened she would send the children out with bowls to eat their fill. Sometimes she gave them money to buy ice cream from the shop — just to make them happy. She lived simply and frugally, setting money aside for old age. But the currency reform of the 1950s wiped out her savings, and Anna lost the flat she had been living in. Her sister Oľga and her family took her in, and it was there that Anna spent the final years of her life.'),
        ('Posledné tri roky Anninho života boli poznačené utrpením. Po páde, pri ktorom si zlomila bedrovú kosť, ostala priputaná na lôžku. Jej fyzické zdravie, no najmä to psychické, začalo pomaly chradnúť. Noci prinášali nepokoje, ťažké sny, chvíle blúznenia. Predsa však nebola sama — najbližšia rodina sa o ňu s láskou a oddanosťou starala do poslednej chvíle. Anna Šenšelová zomrela 28. júla 1976.',
         "The last three years of Anna's life were marked by suffering. After a fall in which she broke her hip, she was confined to bed. Her physical health, and above all her mental health, began to slowly deteriorate. The nights brought restlessness, heavy dreams, moments of delirium. Yet she was not alone — her closest family cared for her with love and devotion until the very end. Anna Šenšelová died on 28 July 1976."),
        ("Odkaz mojej pratety, Anny Šenšelovej sa takmer stratil v zabudnutí. Dve igelitky výšiviek objavené v pivnici po mojich starých rodičoch ma priviedli k pátraniu po jej príbehu. A nielen jej, ale aj mojom, pretože som skrz tieto výšivky začala pátrať po celej mojej rodinnej histórii a skrz poznanie rodinnej minulosti sa začínam mať akosi radšej a som hrdá na to, kam siahajú moje korene.",
         "The legacy of my great-aunt, Anna Šenšelová, almost fell into oblivion. Two plastic bags of embroideries discovered in my grandparents' cellar led me to search for her story. And not only hers, but mine too — for through these embroideries I began tracing my entire family history, and through knowing my family's past I have come to feel a kind of love for myself and pride in how deep my roots go."),
        ('zdroj: Zborník Slovenského národného múzea. Etnografia, Jan V. Ormis, 1982 · rodinný archív: Ján Juráš, Oľga Kapustová',
         'source: Proceedings of the Slovak National Museum. Ethnography, Jan V. Ormis, 1982 · family archive: Ján Juráš, Oľga Kapustová'),
        # rodostrom
        ('<p class="section-label">Rodová línia</p>', '<p class="section-label">Family line</p>'),
        ('>Rodostrom<', '>Family Tree<'),
        ('Anna pochádzala z dlhej línie evanjelických národovcov. Prejdite kurzorom nad osobu pre viac informácií.',
         'Anna came from a long line of Evangelical Slovak patriots. Hover over a person for more information.'),
        ('<p class="gen-label">Prastarí rodičia</p>', '<p class="gen-label">Great-grandparents</p>'),
        ('data-titul="Učiteľ · Národný pracovník · Zakladajúci člen Matice slovenskej"',
         'data-titul="Teacher · National activist · Founding member of Matica slovenská"'),
        ('data-text="Narodil sa v Háji pri Turčianskych Tepliciach. V roku 1848/49 sa zúčastnil slovenského povstania, kde osobne spoznal Ľudovíta Štúra. Bol zakladajúcim členom a jednateľom Matice slovenskej, zakladateľom školskej knižnice, spevokolu mládeže. 30 rokov učil na Dačovom Lome v čase najtvrdšej maďarizácie."',
         'data-text="Born in Háj near Turčianske Teplice. In 1848/49 he took part in the Slovak Uprising, where he met Ľudovít Štúr in person. He was a founding member and secretary of Matica slovenská, founder of the school library and youth choir. For 30 years he taught in Dačov Lom during the harshest years of Magyarisation."'),
        ('data-titul="Neter Michala Miloslava Hodžu"', 'data-titul="Niece of Michal Miloslav Hodža"'),
        ('data-text="Anna Hodžová bola neterou významného slovenského národovca a evanjelického farára Michala Miloslava Hodžu. Cez ňu sa rodina Šenšelovcov priamo napájala na jednu z najvýznamnejších línií slovenského národného obrodenia."',
         'data-text="Anna Hodžová was the niece of the prominent Slovak patriot and Evangelical pastor Michal Miloslav Hodža. Through her, the Šenšel family was directly connected to one of the most important lineages of the Slovak national revival."'),
        ('<p class="gen-label">Rodičia</p>', '<p class="gen-label">Parents</p>'),
        ('data-titul="Evanjelický učiteľ · Očová"', 'data-titul="Evangelical teacher · Očová"'),
        ('data-text="Narodil sa 18.12.1853. Bol evanjelický učiteľ v Očovej do roku 1906. Keď hrozilo, že ho suspendujú, pretože deti nenaučil dosť po maďarsky, odišiel s rodinou na Dačov Lom, kde s manželkou opatrovali svokrovcov Izákovcov. Bol otcom Anny, Ľudovíta, Jána a Oľgy."',
         'data-text="Born 18 December 1853. He was an Evangelical teacher in Očová until 1906. When he faced suspension for not teaching the children enough Hungarian, he moved with his family to Dačov Lom, where he and his wife cared for his in-laws, the Izáks. He was the father of Anna, Ľudovít, Ján, and Oľga."'),
        ('data-titul="Dcéra Ľudovíta Izáka · Spojivo Lipy so Slatinou"',
         'data-titul="Daughter of Ľudovít Izák · Link between Lipa and Slatina"'),
        ('data-text="Narodila sa 24.5.1860. Dcéra národovca a učiteľa Ľudovíta Izáka. Pomáhala Anne s kontaktovaním vyšívačiek v okolí Zvolena počas jej práce v spolku Lipa. Jej otec strávil posledné roky života v ich domácnosti."',
         'data-text="Born 24 May 1860. Daughter of the patriot and teacher Ľudovít Izák. She helped Anna contact the embroiderers in the Zvolen region during her work with the Lipa association. Her father spent the final years of his life in their household."'),
        ('<p class="gen-label">Anna Šenšelová a jej súrodenci</p>',
         '<p class="gen-label">Anna Šenšelová and her siblings</p>'),
        ('data-titul="Evanjelický farár · Učiteľ · Poslanec · Odporca fašizmu"',
         'data-titul="Evangelical pastor · Teacher · MP · Anti-fascist"'),
        ("data-text=\"Brat Anny. Študoval teológiu v Šoproni, pobýval v Lipsku a Edinburghu. Od 1914 farár v Liptovskej Porúbke. Zakladateľ časopisu Tvorba, predseda Hurbanovej spol. Organizoval protifašistický odboj. Poslanec SNR 1945–48. Po komunistickom prevrate vylúčený zo všetkých funkcií.\"",
         "data-text=\"Anna's brother. He studied theology in Sopron, spent time in Leipzig and Edinburgh. From 1914 pastor in Liptovská Porúbka. Founder of the journal Tvorba, chairman of the Hurban Society. He organised anti-fascist resistance. Member of the Slovak National Council 1945–48. After the communist takeover he was removed from all posts.\""),
        ('data-titul="Riaditeľka Lipy · Zachránkyňa slovenského výšivkárstva"',
         'data-titul="Director of Lipa · Saviour of Slovak embroidery"'),
        ('data-text="Narodila sa na Štedrý deň v Očovej. V 28 rokoch odišla študovať vyšívanie do Prahy. 42 rokov viedla martinskú Lipu — pešo vyhľadávala vyšívačky po slovenských dedinách, zachraňovala vzory a budovala sieť remeselníčok. Lipa získavala ocenenia od Viedne po Košice."',
         'data-text="Born on Christmas Eve in Očová. At 28 she went to study embroidery in Prague. For 42 years she led Lipa in Martin — on foot she sought out embroiderers in Slovak villages, preserved patterns, and built a network of craftswomen. Lipa won awards from Vienna to Košice."'),
        ('data-titul="Kúpeľný tajomník · Nový Smokovec"',
         'data-titul="Spa secretary · Nový Smokovec"'),
        ('data-text="Ján Šenšel bol kúpeľným tajomníkom v Novom Smokovci. Oženil sa s Arankou Hubkovou, priekopníčkou kozmetiky na Slovensku, ktorá dlhé roky viedla modnú rubriku v časopise Živena."',
         'data-text="Ján Šenšel was spa secretary in Nový Smokovec. He married Aranka Hubková, a pioneer of cosmetics in Slovakia, who for many years edited the fashion column in the journal Živena."'),
        ("data-titul=\"Obchodná škola Šoproň · Evanjelická farárka · Martin\"",
         "data-titul=\"Commercial school Sopron · Evangelical pastor's wife · Martin\""),
        ('data-text="Narodila sa 7.5.1881. Vyštudovala obchodnú školu v Šoproni. Vydala sa za evanjelického farára Júliusa Helvígha, s ktorým žili najskôr v Sučanoch a neskôr v Martine, kde opatrovali rodičov Šenšelovcov aj starého otca Ľudovíta Izáka."',
         'data-text="Born 7 May 1881. She completed a commercial school in Sopron. She married the Evangelical pastor Július Helvígh; they lived first in Sučany and later in Martin, where they cared for the Šenšel parents and her grandfather Ľudovít Izák."'),
        # tooltip close button (unique context)
        ('>×</button>\n    <div class="tooltip-foto-wrap">',
         '>×</button>\n    <div class="tooltip-foto-wrap">'),
        # zastava section
        ('<p class="section-label">Výšivka v DNA</p>', '<p class="section-label">Embroidery in the DNA</p>'),
        ('<h2>Rodina popretkávaná láskou k výšivke</h2>',
         '<h2>A family woven through with love of embroidery</h2>'),
        ('Keď som začala pátrať po histórii Lipy a Anne Šenšelovej, nečakala som, že objavím lásku k výšivke u toľkých predkov. Rodina Šenšelovcov mala k ihle a niti vzťah, o akom sa mi ani nesnívalo.',
         'When I began researching the history of Lipa and Anna Šenšelová, I did not expect to discover a love of embroidery in so many of my ancestors. The Šenšel family had a relationship with needle and thread that I could never have imagined.'),
        ('<h3>Výšivka ako tajná misia — Zástava slobody</h3>',
         '<h3>Embroidery as a secret mission — the Flag of Freedom</h3>'),
        ('Bol rok 1918 a Slovensko stálo na prahu obrovskej zmeny. Skupina mikulášskych diev sa rozhodla privítať toto oslobodenie spôsobom, ktorý bol v tej dobe nielen symbolický, ale aj nebezpečný — vyšiť vlajku slobody. Pracovali za zamknutými dverami, so zatiahnutými oblokmi, a keď sa niekto pýtal, čo robia, odpovedali, že „vyšívajú oltárne rúcho".',
         'It was 1918, and Slovakia stood on the threshold of an enormous change. A group of young women from Mikuláš decided to welcome this liberation in a way that was not only symbolic but also dangerous — by embroidering a flag of freedom. They worked behind locked doors with the curtains drawn, and when anyone asked what they were doing, they replied that they were "embroidering altar cloth".'),
        ('Financoval ich Branko Lacko, ktorý zohnal pravý český biely hodváb. Nákres zástavy zhotovil akademický maliar Kostelníček, zlaté a strieborné nite im dodal spolok <em>Lipa</em> z Turčianskeho Sv. Martina — ten istý spolok, v ktorom dlhé roky pracovala aj Anna Šenšelová. Vzory z Čiech, Slovenska, Moravy a Sliezska vyšívala slečinka Uličných, každý roh zástavy mal svoju vyšívačku — štyri devy na rohoch, ďalšie pri vzoroch, príprave a odkresľovaní — dokopy deväť odvážnych žien, jeden spoločný čin.',
         'They were funded by Branko Lacko, who procured genuine Czech white silk. The design of the flag was drawn by the academic painter Kostelníček; gold and silver threads were supplied by the <em>Lipa</em> association from Turčiansky Sv. Martin — the very association where Anna Šenšelová worked for so many years. The motifs from Bohemia, Slovakia, Moravia, and Silesia were embroidered by Miss Uličná; each corner of the flag had its own embroiderer — four women on the corners, others on the patterns, preparation, and tracing — nine courageous women in all, one shared act.'),
        ('Každá z vyšívačiek si pred prácou odstrihla prameň vlasov a zavyšívala ho do vzorky zástavy. Kúsok seba doslova všili do látky, do histórie.',
         'Before beginning, each embroiderer cut a strand of her own hair and stitched it into the pattern of the flag. They literally sewed a piece of themselves into the fabric — into history.'),
        ('alt="Vyšívačky zástavy slobody"', 'alt="Embroiderers of the Flag of Freedom"'),
        ('Vyšívačky zástavy slobody —<br>Darina Trnovská (neskôr Šenšelová) druhá zľava v hornom rade',
         'Embroiderers of the Flag of Freedom —<br>Darina Trnovská (later Šenšelová) second from left, top row'),
        ('Zástava slobody', 'Flag of Freedom'),
        ('alt="Slávnostné zhromaždenie na námestí v Liptovskom Sv. Mikuláši, 8. december 1918"',
         'alt="Ceremonial gathering in the square in Liptovský Sv. Mikuláš, 8 December 1918"'),
        ('Slávnostné zhromaždenie<br>8. december 1918, Liptovský Sv. Mikuláš',
         'Ceremonial gathering<br>8 December 1918, Liptovský Sv. Mikuláš'),
        ('<h3>Moja prastará mama Darina</h3>', '<h3>My great-grandmother Darina</h3>'),
        ('Medzi tými štyrmi odvážnymi devami bola aj moja prastará mama, <strong>Darina Trnovská</strong>, neskôr Šenšelová — svagriná Anny Šenšelovej.',
         "Among those four courageous women was my own great-grandmother, <strong>Darina Trnovská</strong>, later Šenšelová — Anna Šenšelová's sister-in-law."),
        ('Zástava bola verejne predstavená 8. decembra 1918 na zhromaždení 15 000 ľudí v Liptovskom Sv. Mikuláši. Posvätili ju spoločne Andrej Hlinka a Jur Janoška. Vojaci pod ňou zložili prísahu. Na tento deň bola napísaná špeciálna báseň, ktorú predniesla Lujza Lacková.',
         'The flag was publicly presented on 8 December 1918 at a gathering of 15,000 people in Liptovský Sv. Mikuláš. It was consecrated together by Andrej Hlinka and Jur Janoška. Soldiers took their oath beneath it. A special poem was written for that day and recited by Lujza Lacková.'),
        ('V roku 1968, pri päťdesiatom výročí Martinskej deklarácie, sa zástava vrátila domov do Liptovského Mikuláša. Na slávnostnom večierku s názvom „Hoj, zem drahá!" ju verejnosti opäť predstavili tri vyšívačky — Darina Droppová-Hubková, Oľga Schatzová-Belnayová a Darina — vtedy už Darina Šenšelová-Trnovská.',
         'In 1968, on the fiftieth anniversary of the Martin Declaration, the flag returned home to Liptovský Mikuláš. At a ceremonial evening titled "Hoj, zem drahá!" ("Oh, dear land!"), it was presented to the public once more by three of the embroiderers — Darina Droppová-Hubková, Oľga Schatzová-Belnayová, and Darina — by then Darina Šenšelová-Trnovská.'),
        ("Spomedzi ďalších žien šenšelovského rodu, ktorých život súvisel s výšivkou, bola Annina matka, <strong>Ľudmila Šenšelová Izáková</strong>, ktorá sprostredkovala kontakt medzi Annou a vyšívačkami v Slatine — tiché, nenápadné spojivo, bez ktorého by sa možno Lipa nikdy nedostala k tým správnym ženám. V predajni Lipy v Martine zase pracovala aj Annina neter, <strong>Viera Helvíghová</strong>, ktorá žiaľ zomrela veľmi mladá. Jej staršia sestra, <strong>Darina Helvíghová</strong>, sa potom starala o obe Vierine dcéry a neskôr sa v Martine starala aj o samotnú Annu Šenšelovú v jej pokročilom veku.",
         "Among the other women of the Šenšel family whose lives were connected to embroidery was Anna's mother, <strong>Ľudmila Šenšelová Izáková</strong>, who served as the link between Anna and the embroiderers in Slatina — a quiet, unassuming connection without which Lipa might never have reached the right women. Also working in the Lipa shop in Martin was Anna's niece, <strong>Viera Helvíghová</strong>, who sadly died very young. Her older sister, <strong>Darina Helvíghová</strong>, then cared for Viera's two daughters and later also looked after Anna Šenšelová herself in her old age in Martin."),
        ('Príbeh zástavy bol zdokumentovaný Jozefom Jurášom, evanjelickým farárom a politickým väzňom, otcom Jána Juráša — krstného syna Anny Šenšelovej. Tento text pochádza z osobného archívu rodiny Jurášovcov a je jedným z mála priamych svedectiev o vzniku zástavy slobody.',
         "The story of the flag was documented by Jozef Juráš, an Evangelical pastor and political prisoner, the father of Ján Juráš — Anna Šenšelová's godson. This text comes from the personal archive of the Juráš family and is one of the few direct accounts of how the Flag of Freedom came to be."),
        ('Prečítať pôvodný text Jozefa Juráša (PDF)', 'Read the original text by Jozef Juráš (PDF)'),
        ('Mikulášska Zástava Slobody · Jozef Juráš', 'Mikuláš Flag of Freedom · Jozef Juráš'),
        ('title="Mikulášska zástava slobody"', 'title="Mikuláš Flag of Freedom"'),
        # podcast section
        ('<p class="section-label">Vypočujte si</p>', '<p class="section-label">Listen</p>'),
        ('<h2>Anna Šenšelová v Robinsonky_FM</h2>', '<h2>Anna Šenšelová on Robinsonky_FM</h2>'),
        ('Jedným z prvých momentov, ktorý ma inšpiroval k hlbšiemu pátraniu po príbehu mojej menovkyne, bol tento podcast. Monika Kapráliková venovala sa tejto téme s citom a zvedavosťou — a vďaka nej som pochopila, že Annu Šenšelovú jednoducho musím spoznať.',
         'One of the first things that inspired me to dig deeper into the story of my namesake was this podcast. Monika Kapráliková approached the topic with sensitivity and curiosity — and it was thanks to her that I understood I simply had to get to know Anna Šenšelová.'),
        ('Podcast zo série <em>Robinsonky_FM</em>, ktorý bol jedným z prvých impulzov k tomuto pátraniu. Monika Kapráliková sa Anninmu príbehu venovala s citom — oplatí sa počuť ho aj v jej podaní.',
         "A podcast from the <em>Robinsonky_FM</em> series, one of the first impulses behind this search. Monika Kapráliková approached Anna's story with great sensitivity — it is well worth hearing it in her telling too."),
        ('>Počúvať na Rádio_FM<', '>Listen on Rádio_FM<'),
        # footer
        ('>Príbeh<', '>Story<'),
        ('Galéria &amp; Mapa', 'Gallery &amp; Map'),
        ('Vzorkovník výšiviek', 'Embroidery Sample Book'),
        ('Ľudové výšivky a odev', 'Folk Embroideries and Dress'),
        ('Mapa spomienok', 'Map of Memories'),
        ('Spojme sa', 'Get in touch'),
        ('Vytvorené s láskou a úctou k predošlým generáciám.',
         'Created with love and respect for past generations.'),
        ('aria-label="Mapa spomienok na Facebooku"', 'aria-label="Map of Memories on Facebook"'),
        ('aria-label="Mapa spomienok na Instagrame"', 'aria-label="Map of Memories on Instagram"'),
        ('Ochrana osobných údajov', 'Privacy policy'),
        ('Zbierka výšiviek, bábik a pozostalosti po rodine Šenšelovcov nie je mojím osobným vlastníctvom — je dedičstvom celej rodiny. Výšivky, bábiky ani kroje nie sú na predaj.',
         'The collection of embroideries, dolls, and personal effects of the Šenšel family is not my personal property — it is the heritage of the whole family. The embroideries, dolls, and folk costumes are not for sale.'),
        # GDPR modal close button
        ('aria-label="Zavrieť">✕</button>', 'aria-label="Close">✕</button>'),
        # carousel JS
        ("d.setAttribute('aria-label', 'Snímka ' + (i + 1));",
         "d.setAttribute('aria-label', 'Slide ' + (i + 1));"),
        # lightbox close
        ('aria-label="Zavrieť">×</button>\n  <img class="lightbox-img"',
         'aria-label="Close">×</button>\n  <img class="lightbox-img"'),
        # tooltip close (rodostrom)
        ('aria-label="Zavrieť">×</button>\n    <div class="tooltip-foto-wrap">',
         'aria-label="Close">×</button>\n    <div class="tooltip-foto-wrap">'),
        # pdf modal close
        ('aria-label="Zavrieť">×</button>\n    </div>\n    <iframe',
         'aria-label="Close">×</button>\n    </div>\n    <iframe'),
    ]

    for old, new in replacements:
        html = html.replace(old, new)

    # Replace entire GDPR box content with regex to avoid encoding mismatches
    gdpr_en = (
        '<div class="gdpr-box">\n'
        '    <button class="gdpr-close" onclick="document.getElementById(\'gdpr-modal\').classList.remove(\'open\')" aria-label="Close">✕</button>\n'
        '    <h2 id="gdpr-title">Privacy policy</h2>\n'
        '    <p><strong>Website operator:</strong> Anna Lockwoodová · <a href="mailto:senselovaanna@gmail.com" style="color:var(--red);">senselovaanna@gmail.com</a></p>\n'
        '    <p>This website is a non-commercial informational site created in my free time. No commercial obligations arise from it.</p>\n'
        '    <p><strong>Contact form:</strong> If you write to me via the contact form, I process the following data: name, email address, and the message text. These are used solely to reply to you. Data are not shared with third parties and will be deleted once the communication is resolved.</p>\n'
        '    <p><strong>Your rights:</strong> You have the right to request access to your data, its correction, or deletion. Simply write to the email address above.</p>\n'
        '    <p><strong>Cookies and fonts:</strong> This site does not use tracking or analytical cookies. Fonts are hosted directly on this server — no data is sent to Google or any other third parties.</p>\n'
        '  </div>'
    )
    html = re.sub(
        r'<div class="gdpr-box">.*?</div>',
        gdpr_en,
        html,
        count=1,
        flags=re.DOTALL
    )

    return html


# ── MAIN ─────────────────────────────────────────────────────────────────────

def process_file(src_path, dst_path, translate_fn, sk_href, old_lang_href,
                 sk_canonical, en_canonical):
    with open(src_path, 'r', encoding='utf-8') as f:
        html = f.read()

    html = set_lang_en(html)
    html = prefix_local_assets(html)
    html = replace_lang_switch(html, sk_href, old_lang_href)
    html = add_hreflang(html, sk_canonical, en_canonical)
    html = translate_fn(html)

    with open(dst_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Written: {dst_path}")


# blog.html
process_file(
    src_path=os.path.join(BASE, 'blog.html'),
    dst_path=os.path.join(EN_DIR, 'blog.html'),
    translate_fn=translate_blog,
    sk_href='../blog.html',
    old_lang_href='en/blog.html',
    sk_canonical='https://avolesnes-tech.github.io/anna-senselova/blog.html',
    en_canonical='https://avolesnes-tech.github.io/anna-senselova/en/blog.html',
)

# mapa-spomienok.html
def translate_mapa_combined(html):
    html = translate_mapa(html)
    html = translate_mapa_html_visible(html)
    return html

process_file(
    src_path=os.path.join(BASE, 'mapa-spomienok.html'),
    dst_path=os.path.join(EN_DIR, 'mapa-spomienok.html'),
    translate_fn=translate_mapa_combined,
    sk_href='../mapa-spomienok.html',
    old_lang_href='en/mapa-spomienok.html',
    sk_canonical='https://avolesnes-tech.github.io/anna-senselova/mapa-spomienok.html',
    en_canonical='https://avolesnes-tech.github.io/anna-senselova/en/mapa-spomienok.html',
)

# anna-senselova.html
process_file(
    src_path=os.path.join(BASE, 'anna-senselova.html'),
    dst_path=os.path.join(EN_DIR, 'anna-senselova.html'),
    translate_fn=translate_anna_senselova,
    sk_href='../anna-senselova.html',
    old_lang_href='en/anna-senselova.html',
    sk_canonical='https://avolesnes-tech.github.io/anna-senselova/anna-senselova.html',
    en_canonical='https://avolesnes-tech.github.io/anna-senselova/en/anna-senselova.html',
)

print("Done.")
