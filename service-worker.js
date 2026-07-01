// 1. تحديد الملفات التي تريد أن يعمل بها التطبيق بدون إنترنت
const CACHE_NAME = 'smart-water-v1';
const ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icon.ico'
  // أضف هنا أي ملفات أخرى مثل ملفات الـ CSS أو JS
];

// 2. حدث التثبيت: تحميل الملفات في الذاكرة المؤقتة (Cache)
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('تم فتح الكاش بنجاح');
      return cache.addAll(ASSETS);
    })
  );
});

// 3. حدث الجلب: عندما يحاول المتصفح طلب ملف، نعطيه إياه من الكاش إن وجد
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      // إذا كان الملف موجوداً في الكاش نرجعه، وإلا نقوم بجلبه من السيرفر
      return response || fetch(event.request);
    })
  );
});

// 4. حدث التنشيط: تنظيف النسخ القديمة من الكاش عند تحديث التطبيق
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
});
