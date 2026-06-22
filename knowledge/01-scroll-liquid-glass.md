# Scroll & Liquid-Glass — 2026 Front-End Cheat-Sheet (uygulanacak)

Düz statik HTML/CSS/JS, build yok, Vercel. Drop-in pattern'ler.

## Özet öncelik (ilk uygulanacak 10)
1. `prefers-reduced-motion` global guard — her efekt buna dallanır
2. Liquid glass component — backdrop blur + specular + 1px border; refraction `@supports` ile
3. IntersectionObserver reveal + stagger — en yüksek cila/bayt oranı
4. Sticky pinned storytelling stacks — saf CSS anlatı scroll'u
5. Mobil video kapısı: poster + preload=metadata + IO play/pause
6. Scroll hero: **image sequence** (video yerine) — mobil-güvenli sinematik merkez
7. Lenis smooth scroll — reduced-motion korumalı
8. Aurora mesh + grain arka plan — saf CSS, ~sıfır maliyet
9. Parallax depth katmanları — tek rAF döngüsü
10. CSS `view()` reveal + GSAP ScrollTrigger pin/scrub — progressive enhancement

## Kritik kod pattern'leri

### Scroll-scrub video (hero scroll'la ilerler)
- Tall section pinle; scroll ilerlemesini `video.currentTime`'a map et.
- `currentTime`'ı rAF döngüsünden sür (scroll event'ten DEĞİL), target'a lerp ile yaklaş.
- Video'yu **her kare keyframe** (1-frame GOP) encode et → smooth seek. Mobilde image-sequence'e düş.
```css
.hero-scrub{height:300vh}
.pin{position:sticky;top:0;height:100vh;display:grid;place-items:center}
.pin video{width:100%;height:100%;object-fit:cover}
```
```js
const v=heroV, sec=document.querySelector('.hero-scrub'); let target=0,current=0;
v.addEventListener('loadedmetadata',()=>{
  const prog=()=>{const r=sec.getBoundingClientRect();return Math.min(1,Math.max(0,-r.top/(sec.offsetHeight-innerHeight)));};
  addEventListener('scroll',()=>{target=prog()*v.duration},{passive:true});
  (function loop(){current+=(target-current)*0.12; if(Math.abs(target-current)>0.01) v.currentTime=current; requestAnimationFrame(loop);})();
});
```

### Image-sequence (mobil için EN İYİ — AirPods tarzı)
N kare (örn 120 WebP) preload → scroll progress'e göre canvas drawImage. Android'de video seek stutter yapar; bunu kullan.
```js
const cv=seq,ctx=cv.getContext('2d'),N=120,imgs=[];let target=0,cur=0;
for(let i=0;i<N;i++){const im=new Image();im.src=`/seq/${String(i).padStart(3,'0')}.webp`;imgs[i]=im;}
const sec=document.querySelector('.seq-scrub');
addEventListener('scroll',()=>{const r=sec.getBoundingClientRect();target=Math.min(1,Math.max(0,-r.top/(sec.offsetHeight-innerHeight)));},{passive:true});
(function loop(){cur+=(target-cur)*0.15;const im=imgs[Math.round(cur*(N-1))];if(im?.complete)ctx.drawImage(im,0,0,cv.width,cv.height);requestAnimationFrame(loop);})();
```

### Liquid glass (imza estetik)
```css
.glass{background:rgba(255,255,255,.08);
  backdrop-filter:blur(20px) saturate(180%);-webkit-backdrop-filter:blur(20px) saturate(180%);
  border:1px solid rgba(255,255,255,.18);border-radius:24px;
  box-shadow:inset 0 1px 1px rgba(255,255,255,.45),inset 0 -1px 1px rgba(255,255,255,.10),0 20px 50px rgba(0,0,0,.25);
  isolation:isolate;}
@supports (backdrop-filter:url(#g)){.glass.refract{backdrop-filter:url(#liquid) blur(8px) saturate(180%);}}
```
SVG refraction filtresi (feTurbulence+feDisplacementMap, scale~40). **blur radius'unu ASLA anime etme** (repaint storm). `will-change` sadece anime olan elemanda, sonra kaldır. Okunabilirlik için solid rgba fallback şart.

### CSS scroll-driven (compositor, JS yok)
```css
@media (prefers-reduced-motion:no-preference){@supports (animation-timeline:view()){
  .reveal{animation:fadeUp linear both;animation-timeline:view();animation-range:entry 0% cover 35%;}}}
.progress{position:fixed;inset:0 0 auto 0;height:3px;transform-origin:left;animation:grow linear both;animation-timeline:scroll(root block);}
```
Support 2026: Chromium 115+, Safari 18+; Firefox flag (~%85). `@supports` ile sar.

### Sticky storytelling
```css
.story{position:relative}.chapter{position:sticky;top:0;height:100vh;display:grid;place-items:center}
```

### Aurora mesh + grain (saf CSS)
Stacked radial-gradient + animasyonlu background-position; WebGL'e gerek yok. SVG noise overlay banding'i keser. reduced-motion'da animation:none.

### Reveal + stagger (IO)
```css
.reveal{opacity:0;transform:translateY(28px);transition:opacity .7s,transform .7s;transition-delay:calc(var(--i,0)*80ms)}
.reveal.in{opacity:1;transform:none}
```
```js
const io=new IntersectionObserver((es,o)=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');o.unobserve(e.target);}}),{threshold:0.15});
document.querySelectorAll('.reveal').forEach((el,i)=>{el.style.setProperty('--i',i%6);io.observe(el)});
```

### reduced-motion global net
```css
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.001ms!important;animation-iteration-count:1!important;transition-duration:.001ms!important;scroll-behavior:auto!important}.aurora,.grain{animation:none}}
```

### Mobil video perf
poster.webp + preload=metadata; IntersectionObserver ile play/pause; her zaman `muted playsinline`; mobilde scrubbing video → image-sequence/poster.

### CDN'ler
GSAP+ScrollTrigger (jsdelivr), Lenis (jsdelivr) — hepsi reduced-motion gated.
