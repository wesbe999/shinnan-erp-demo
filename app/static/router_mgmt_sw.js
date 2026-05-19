const CACHE_NAME = 'shinnan-router-v1';
const STATIC_ASSETS = [
  '/static/app_header_unified.css?v=20260511_title_v1',
  '/static/app_header_actions.js?v=cl17p6',
  '/static/shinnan_home_logo.png',
  '/static/pwa_icon_192.png',
  '/static/pwa_icon_512.png',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(c => c.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  // API 請求不快取
  if (url.pathname.startsWith('/api/')) return;
  // 靜態資源優先用快取
  if (url.pathname.startsWith('/static/')) {
    e.respondWith(
      caches.match(e.request).then(r => r || fetch(e.request))
    );
    return;
  }
  // 其他走網路
});
