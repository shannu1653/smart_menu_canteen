/* enhancements/dark_toggle.js */
(function(){
  function setTheme(t){ if(t==='dark') document.documentElement.setAttribute('data-theme','dark'); else document.documentElement.removeAttribute('data-theme'); localStorage.setItem('theme',t); }
  var pref = localStorage.getItem('theme')||'light'; setTheme(pref);
  window.toggleTheme = function(){ var c = localStorage.getItem('theme')||'light'; setTheme(c==='dark'?'light':'dark'); };
})();
