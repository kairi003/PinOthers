const html = document.documentElement;
html.lang = localStorage['lang'] = location.hash.replace('#', '') || localStorage['lang'] || (navigator.language.startsWith('ja') ? 'ja' : 'en');
addEventListener('hashchange', e => html.lang = localStorage['lang'] = location.hash.replace('#', ''));