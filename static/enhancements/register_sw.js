if('serviceWorker' in navigator){ window.addEventListener('load', ()=>{ navigator.serviceWorker.register('/static/enhancements/pwa/serviceworker.js').then(()=>console.log('SW')).catch(()=>{}); }); }
