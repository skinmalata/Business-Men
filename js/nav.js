(function () {
  function getActivePage() {
    var path = window.location.pathname.replace(/\/+$/, '');
    if (path.endsWith('listing.html')) return 'listings';
    if (path.endsWith('services.html')) return 'services';
    if (path.endsWith('claim.html')) return 'contact';
    return 'home';
  }

  function injectNav() {
    var container = document.getElementById('nav-container');
    if (!container) return;

    var active = getActivePage();

    container.innerHTML =
      '<header>' +
        '<nav class="navbar" aria-label="Main navigation">' +
          '<div class="container">' +
            '<a href="/" class="logo">' +
              '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#e94560" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:7px">' +
                '<rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>' +
              '</svg>Business<span>Men</span>' +
            '</a>' +
            '<div class="nav-scroll">' +
              '<a href="/"' + (active === 'home' ? ' class="active"' : '') + '>Home</a>' +
              '<a href="/#about">About</a>' +
              '<a href="/services.html"' + (active === 'services' ? ' class="active"' : '') + '>Services</a>' +
              '<div class="nav-dropdown">' +
                '<a href="/#categories">Categories</a>' +
                '<div class="nav-dropdown-menu">' +
                  '<a href="/listing.html?cat=hotels">Hotels</a>' +
                  '<a href="/listing.html?cat=hospitals">Hospitals</a>' +
                  '<a href="/listing.html?cat=schools">Schools</a>' +
                  '<a href="/listing.html?cat=agriculture">Agriculture</a>' +
                  '<a href="/listing.html?cat=transportation">Transport</a>' +
                  '<a href="/listing.html?cat=shopping">Shopping</a>' +
                  '<a href="/listing.html?cat=business">Business</a>' +
                  '<a href="/listing.html?cat=realestate">Real Estate</a>' +
                  '<a href="/listing.html?cat=oilgas">Oil & Gas</a>' +
                  '<a href="/listing.html?cat=construction">Construction</a>' +
                  '<a href="/listing.html?cat=automobile">Automobile</a>' +
                  '<a href="/listing.html?cat=food">Food & Restaurants</a>' +
                '</div>' +
              '</div>' +
              '<a href="/claim.html"' + (active === 'contact' ? ' class="active"' : '') + '>Advertise</a>' +
              '<a href="/claim.html">Contact</a>' +
            '</div>' +
          '</div>' +
        '</nav>' +
      '</header>';
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectNav);
  } else {
    injectNav();
  }
})();
