(function () {
  function getActivePage() {
    var path = window.location.pathname.replace(/\/+$/, '');
    if (path.endsWith('listing.html')) return 'listings';
    if (path.endsWith('getlisted.html')) return 'getlisted';
    if (path.endsWith('services.html')) return 'services';
    if (path.endsWith('claim.html')) return 'claim';
    if (path.endsWith('contact.html')) return 'contact';
    if (path.endsWith('marketplace.html')) return 'marketplace';
    if (path.endsWith('post-ad.html')) return 'marketplace';
    if (path.endsWith('ad-detail.html')) return 'marketplace';
    if (path.includes('/blog/') || path.endsWith('/blog')) return 'blog';
    return 'home';
  }

  function injectNav() {
    var container = document.getElementById('nav-container');
    if (!container) return;

    var active = getActivePage();
    var isBlog = active === 'blog';
    var p = isBlog ? '../' : '';

    container.innerHTML =
      '<header>' +
        '<nav class="navbar" aria-label="Main navigation">' +
          '<div class="container">' +
            '<a href="' + p + '." class="logo">' +
              '<img src="' + p + 'bm logo.png" alt="BusinessMen" style="height:42px;vertical-align:middle;margin-right:10px">Business<span>Men</span>' +
            '</a>' +
            '<button class="nav-toggle" aria-label="Toggle menu" aria-expanded="false">&#9776;</button>' +
            '<div class="nav-scroll">' +
              '<a href="' + p + '."' + (active === 'home' ? ' class="active"' : '') + '>Home</a>' +
              '<a href="' + p + '#about">About</a>' +
              '<a href="' + p + 'services.html"' + (active === 'services' ? ' class="active"' : '') + '>Services</a>' +
              '<div class="nav-dropdown">' +
                '<span class="nav-dropdown-trigger">Categories <span class="dropdown-arrow">&#9662;</span></span>' +
                '<div class="nav-dropdown-menu">' +
                  '<a href="' + p + 'listing.html?cat=all"><strong>All Businesses</strong></a>' +
                  '<a href="' + p + 'listing.html?cat=hotels">Hotels</a>' +
                  '<a href="' + p + 'listing.html?cat=hospitals">Hospitals</a>' +
                  '<a href="' + p + 'listing.html?cat=schools">Schools</a>' +
                  '<a href="' + p + 'listing.html?cat=agriculture">Agriculture</a>' +
                  '<a href="' + p + 'listing.html?cat=transportation">Transport</a>' +
                  '<a href="' + p + 'listing.html?cat=shopping">Shopping</a>' +
                  '<a href="' + p + 'listing.html?cat=business">Business</a>' +
                  '<a href="' + p + 'listing.html?cat=realestate">Real Estate</a>' +
                  '<a href="' + p + 'listing.html?cat=oilgas">Oil & Gas</a>' +
                  '<a href="' + p + 'listing.html?cat=construction">Construction</a>' +
                  '<a href="' + p + 'listing.html?cat=automobile">Automobile</a>' +
                  '<a href="' + p + 'listing.html?cat=food">Food & Restaurants</a>' +
                '</div>' +
              '</div>' +
              '<a href="' + p + 'marketplace.html"' + (active === 'marketplace' ? ' class="active"' : '') + '>Marketplace</a>' +
              '<a href="' + p + 'blog/"' + (active === 'blog' ? ' class="active"' : '') + '>Blog</a>' +
              '<a href="' + p + 'getlisted.html"' + (active === 'getlisted' ? ' class="active"' : '') + '>Get Listed</a>' +
              '<a href="' + p + 'contact.html"' + (active === 'contact' ? ' class="active"' : '') + '>Contact</a>' +
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
        e.stopPropagation();
        this.parentElement.classList.toggle('open');
      });
      document.addEventListener('click', function(e) {
        var dropdown = container.querySelector('.nav-dropdown');
        if (dropdown && !dropdown.contains(e.target)) {
          dropdown.classList.remove('open');
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
