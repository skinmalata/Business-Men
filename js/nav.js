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
            '<a href="." class="logo">' +
              '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#e94560" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:7px">' +
                '<rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>' +
              '</svg>Business<span>Men</span>' +
            '</a>' +
            '<button class="nav-toggle" aria-label="Toggle menu" aria-expanded="false">&#9776;</button>' +
            '<div class="nav-scroll">' +
              '<a href="."' + (active === 'home' ? ' class="active"' : '') + '>Home</a>' +
              '<a href="#about">About</a>' +
              '<a href="services.html"' + (active === 'services' ? ' class="active"' : '') + '>Services</a>' +
              '<div class="nav-dropdown">' +
                '<a href="#categories" class="nav-dropdown-trigger">Categories <span class="dropdown-arrow">&#9662;</span></a>' +
                '<div class="nav-dropdown-menu">' +
                  '<a href="listing.html?cat=hotels">Hotels</a>' +
                  '<a href="listing.html?cat=hospitals">Hospitals</a>' +
                  '<a href="listing.html?cat=schools">Schools</a>' +
                  '<a href="listing.html?cat=agriculture">Agriculture</a>' +
                  '<a href="listing.html?cat=transportation">Transport</a>' +
                  '<a href="listing.html?cat=shopping">Shopping</a>' +
                  '<a href="listing.html?cat=business">Business</a>' +
                  '<a href="listing.html?cat=realestate">Real Estate</a>' +
                  '<a href="listing.html?cat=oilgas">Oil & Gas</a>' +
                  '<a href="listing.html?cat=construction">Construction</a>' +
                  '<a href="listing.html?cat=automobile">Automobile</a>' +
                  '<a href="listing.html?cat=food">Food & Restaurants</a>' +
                '</div>' +
              '</div>' +
              '<a href="claim.html"' + (active === 'contact' ? ' class="active"' : '') + '>Edit Listing</a>' +
              '<a href="claim.html">Contact</a>' +
            '</div>' +
          '</div>' +
        '</nav>' +
      '</header>';

    var toggle = container.querySelector('.nav-toggle');
    if (toggle) {
      toggle.addEventListener('click', function(e) {
        e.stopPropagation();
        var nav = container.querySelector('.navbar');
        var expanded = this.getAttribute('aria-expanded') === 'true';
        nav.classList.toggle('nav-open');
        this.setAttribute('aria-expanded', !expanded);
        this.innerHTML = expanded ? '\u2630' : '\u2715';
      });
      document.addEventListener('click', function(e) {
        if (!e.target.closest('.navbar')) {
          var nav = container.querySelector('.navbar');
          if (nav && nav.classList.contains('nav-open')) {
            nav.classList.remove('nav-open');
            toggle.setAttribute('aria-expanded', 'false');
            toggle.innerHTML = '\u2630';
          }
        }
      });
    }

    var dropdownTrigger = container.querySelector('.nav-dropdown-trigger');
    if (dropdownTrigger) {
      dropdownTrigger.addEventListener('click', function(e) {
        if (window.innerWidth <= 900) {
          e.preventDefault();
          this.parentElement.classList.toggle('open');
        }
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectNav);
  } else {
    injectNav();
  }
})();
