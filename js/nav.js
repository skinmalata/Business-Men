(function () {
  function getActivePage() {
    var path = window.location.pathname.replace(/\/+$/, '');
    if (path.endsWith('listing.html')) return 'services';
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
            '<a href="/Business-Men/" class="logo">' +
              '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e94560" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px">' +
                '<circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/>' +
                '<path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>' +
              '</svg>Business<span>Men</span>' +
            '</a>' +
            '<div class="nav-scroll">' +
              '<a href="/Business-Men/"' + (active === 'home' ? ' class="active"' : '') + '>Home</a>' +
              '<a href="/Business-Men/#about">About</a>' +
              '<a href="/Business-Men/listing.html"' + (active === 'services' ? ' class="active"' : '') + '>Services</a>' +
              '<div class="nav-dropdown">' +
                '<a href="/Business-Men/#categories">Categories</a>' +
                '<div class="nav-dropdown-menu">' +
                  '<a href="/Business-Men/listing.html?cat=hotels">Hotels</a>' +
                  '<a href="/Business-Men/listing.html?cat=hospitals">Hospitals</a>' +
                  '<a href="/Business-Men/listing.html?cat=schools">Schools</a>' +
                  '<a href="/Business-Men/listing.html?cat=agriculture">Agriculture</a>' +
                  '<a href="/Business-Men/listing.html?cat=transportation">Transport</a>' +
                  '<a href="/Business-Men/listing.html?cat=shopping">Shopping</a>' +
                  '<a href="/Business-Men/listing.html?cat=business">Business</a>' +
                  '<a href="/Business-Men/listing.html?cat=realestate">Real Estate</a>' +
                  '<a href="/Business-Men/listing.html?cat=oilgas">Oil & Gas</a>' +
                  '<a href="/Business-Men/listing.html?cat=construction">Construction</a>' +
                  '<a href="/Business-Men/listing.html?cat=automobile">Automobile</a>' +
                  '<a href="/Business-Men/listing.html?cat=food">Food & Restaurants</a>' +
                '</div>' +
              '</div>' +
              '<a href="/Business-Men/claim.html"' + (active === 'contact' ? ' class="active"' : '') + '>Advertise</a>' +
              '<a href="/Business-Men/claim.html">Contact</a>' +
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
