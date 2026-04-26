-- ═══════════════════════════════════════════════════════════════
--  MAPA SPOMIENOK — Supabase setup
--  Spusti tento script v Supabase → SQL Editor
-- ═══════════════════════════════════════════════════════════════

-- 1. TABUĽKA PRÍBEHOV
-- ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS stories (
  id                  UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
  predok_meno         TEXT        NOT NULL,
  predok_priezvisko   TEXT        NOT NULL,
  obec                TEXT        NOT NULL,
  kraj                TEXT,
  lat                 FLOAT,          -- zemepisná šírka (voliteľné — pre presné umiestnenie pinu)
  lng                 FLOAT,          -- zemepisná dĺžka (voliteľné)
  obdobie             TEXT        NOT NULL,
  pribeh              TEXT        NOT NULL,
  foto_url            TEXT,           -- URL z Supabase Storage
  zdielal_meno        TEXT,           -- voliteľné — meno prispievateľa
  zdielal_priezvisko  TEXT,           -- voliteľné — priezvisko prispievateľa
  zdielal_email       TEXT,           -- voliteľné — e-mail prispievateľa (pre notifikáciu o schválení)
  status              TEXT        NOT NULL DEFAULT 'pending'
                                  CHECK (status IN ('pending','approved','rejected')),
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index pre fulltextové vyhľadávanie podľa priezviska
CREATE INDEX IF NOT EXISTS stories_priezvisko_idx
  ON stories USING GIN (to_tsvector('simple', predok_priezvisko));

-- Index pre filtrovanie podľa statusu + dátumu
CREATE INDEX IF NOT EXISTS stories_status_created_idx
  ON stories (status, created_at DESC);

-- Index pre filtrovanie podľa kraja
CREATE INDEX IF NOT EXISTS stories_kraj_idx
  ON stories (kraj);


-- 2. ROW LEVEL SECURITY
-- ───────────────────────────────────────────────────────────────
ALTER TABLE stories ENABLE ROW LEVEL SECURITY;

-- Verejnosť číta iba schválené príbehy
CREATE POLICY "public_read_approved"
  ON stories FOR SELECT
  USING (status = 'approved');

-- Verejnosť môže vkladať iba pending príbehy
CREATE POLICY "public_insert_pending"
  ON stories FOR INSERT
  WITH CHECK (status = 'pending');

-- Len autentifikovaní (ty) môžu meniť status / mazať
CREATE POLICY "auth_update"
  ON stories FOR UPDATE
  USING (auth.role() = 'authenticated');

CREATE POLICY "auth_delete"
  ON stories FOR DELETE
  USING (auth.role() = 'authenticated');


-- 3. STORAGE BUCKET PRE FOTOGRAFIE
-- ───────────────────────────────────────────────────────────────
-- Spusti toto v Supabase → Storage → New bucket
-- Alebo cez SQL:

INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'story-photos',
  'story-photos',
  TRUE,                           -- verejne čitateľné URL
  5242880,                        -- max 5 MB
  ARRAY['image/jpeg','image/jpg','image/png','image/webp','image/gif']
)
ON CONFLICT (id) DO NOTHING;

-- Storage RLS — ktokoľvek môže nahrávať, čítať; len auth môže mazať
CREATE POLICY "public_upload_photos"
  ON storage.objects FOR INSERT
  WITH CHECK (bucket_id = 'story-photos');

CREATE POLICY "public_read_photos"
  ON storage.objects FOR SELECT
  USING (bucket_id = 'story-photos');

CREATE POLICY "auth_delete_photos"
  ON storage.objects FOR DELETE
  USING (bucket_id = 'story-photos' AND auth.role() = 'authenticated');


-- 4. PRÍKLAD — ako pridať príbeh manuálne cez SQL Editor
-- ───────────────────────────────────────────────────────────────
/*
INSERT INTO stories (
  predok_meno, predok_priezvisko, obec, kraj, obdobie, pribeh,
  foto_url, zdielal_meno, zdielal_priezvisko, status
) VALUES (
  'Mária', 'Šenšelová',
  'Horné Srnie', 'Trenčiansky kraj',
  'medzivojnove',
  'Babička celé noci vyšívala pri sviečke, aby ušetrila na školu pre deti...',
  NULL,
  'Anna', 'Lockwoodová',
  'approved'        -- ← ihneď zverejnené, keďže vkladáš ty
);
*/


-- 5. AKO SCHVAĽOVAŤ PRÍSPEVKY
-- ───────────────────────────────────────────────────────────────
-- V Supabase dashboarde: Table Editor → stories → filter status = pending
-- Zmeň status z 'pending' na 'approved'
-- Alebo cez SQL:
/*
UPDATE stories SET status = 'approved' WHERE id = 'UUID_PRISPEVKU';
UPDATE stories SET status = 'rejected' WHERE id = 'UUID_PRISPEVKU';
*/


-- 6. UŽITOČNÉ QUERY
-- ───────────────────────────────────────────────────────────────
-- Všetky čakajúce príspevky:
-- SELECT id, predok_meno, predok_priezvisko, obec, created_at FROM stories WHERE status = 'pending' ORDER BY created_at;

-- Počet príbehov podľa kraja:
-- SELECT kraj, COUNT(*) FROM stories WHERE status = 'approved' GROUP BY kraj ORDER BY COUNT(*) DESC;

-- Príbehy s rovnakým priezviskom:
-- SELECT * FROM stories WHERE status = 'approved' AND predok_priezvisko ILIKE '%Kopecká%';
