// DİDİ Otel — rezervasyon yakalama (Vercel Serverless + Blob)
// Site rezervasyon sihirbazı buraya POST eder; kayıtlar UniqBee Ajans
// Dashboard'unda (aynı Blob store) görünür. Ödeme/PII toplamaz; sadece
// isim + opsiyonel telefon + tarih + oda + misafir bilgisi.
import { put, list } from '@vercel/blob';

const s = (v, max) => (typeof v === 'string' ? v.trim().slice(0, max) : '');
const isDate = (v) => typeof v === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(v);
const isEmail = (v) => typeof v === 'string' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim());
const clampInt = (v, lo, hi) => {
  const n = parseInt(v, 10);
  if (Number.isNaN(n)) return lo;
  return Math.max(lo, Math.min(hi, n));
};

const DEDUP_WINDOW_MS = 10 * 60 * 1000;

// Ayni kisi/oda/tarih icin kisa sure icinde (cift tikla, retry, coklu sekme)
// tekrar POST gelirse yeni kayit acmak yerine mevcut kaydi dondur.
async function findRecentDuplicate(rec) {
  try {
    const now = Date.now();
    const candidates = [];
    let cursor;
    do {
      const page = await list({ prefix: 'didi/reservations/', limit: 1000, cursor });
      for (const b of page.blobs) {
        if (now - new Date(b.uploadedAt).getTime() <= DEDUP_WINDOW_MS) candidates.push(b);
      }
      cursor = page.hasMore ? page.cursor : undefined;
    } while (cursor);

    for (const b of candidates) {
      try {
        const r = await fetch(b.url + (b.url.includes('?') ? '&' : '?') + 'ts=' + now, { cache: 'no-store' });
        if (!r.ok) continue;
        const j = await r.json();
        if (j.name === rec.name && j.phone === rec.phone && j.room === rec.room &&
            j.checkin === rec.checkin && j.checkout === rec.checkout &&
            j.adults === rec.adults && j.children === rec.children) {
          return j;
        }
      } catch { /* bozuk kayit atla */ }
    }
  } catch { /* dedup basarisiz olursa normal akisa devam */ }
  return null;
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, error: 'method' });
  }
  try {
    let body = req.body;
    if (typeof body === 'string') { try { body = JSON.parse(body); } catch { body = {}; } }
    body = body || {};

    const name = s(body.name, 100);
    const checkin = isDate(body.checkin) ? body.checkin : '';
    const checkout = isDate(body.checkout) ? body.checkout : '';
    if (!name || !checkin || !checkout) {
      return res.status(400).json({ ok: false, error: 'eksik-alan' });
    }

    const rec = {
      id: 'r_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 8),
      brand: 'didi-otel',
      name,
      phone: s(body.phone, 32),
      email: isEmail(body.email) ? s(body.email, 120) : '',
      room: s(body.room, 60),
      checkin,
      checkout,
      nights: clampInt(body.nights, 0, 365),
      adults: clampInt(body.adults, 1, 12),
      children: clampInt(body.children, 0, 10),
      breakfast: !!body.breakfast,
      source: s(body.source, 40) || 'website-wizard',
      channel: s(body.channel, 40) || 'Doğrudan',
      referrer: s(body.referrer, 300),
      utm: s(body.utm, 60),
      status: 'new',
      createdAt: new Date().toISOString(),
      ip: (req.headers['x-forwarded-for'] || '').toString().split(',')[0].trim().slice(0, 45),
      ua: s(req.headers['user-agent'], 200),
    };

    if (!process.env.BLOB_READ_WRITE_TOKEN) {
      // Storage bağlı değilse sessizce kabul et (site akışı bozulmasın).
      return res.status(202).json({ ok: true, stored: false });
    }

    const dup = await findRecentDuplicate(rec);
    if (dup) {
      return res.status(200).json({ ok: true, stored: true, id: dup.id, dedup: true });
    }

    await put(`didi/reservations/${rec.id}.json`, JSON.stringify(rec), {
      access: 'public',
      addRandomSuffix: true,
      contentType: 'application/json',
      cacheControlMaxAge: 0,
    });

    return res.status(200).json({ ok: true, stored: true, id: rec.id });
  } catch (err) {
    return res.status(500).json({ ok: false, error: 'server' });
  }
}
