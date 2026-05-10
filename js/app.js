let allData = [];
let filteredData = [];
let currentCategory = 'hotels';

const DATA_FILES = {
  hotels: 'data/nigeria_hotels.json',
  hospitals: 'data/nigeria_hospitals.json',
  schools: 'data/nigeria_schools.json',
    agriculture: 'data/nigeria_agriculture.json',
    transportation: 'data/nigeria_transportation.json',
    shopping: 'data/nigeria_shopping.json',
    business: 'data/nigeria_business.json',
    realestate: 'data/nigeria_realestate.json',
    oilgas: 'data/nigeria_oilgas.json',
    construction: 'data/nigeria_construction.json'
  };

const CATEGORY_NAMES = {
  hotels: { label: 'Hotels', title: 'Hotels in Nigeria', desc: 'Find hotels, resorts, and accommodation across all Nigerian cities. Browse contact info, addresses, and services.' },
  hospitals: { label: 'Hospitals', title: 'Hospitals in Nigeria', desc: 'Find hospitals, medical centres, and healthcare providers across Nigeria. Browse contact info and services.' },
  schools: { label: 'Schools', title: 'Schools & Universities in Nigeria', desc: 'Find schools, universities, colleges, and educational institutions across all Nigerian states.' },
  agriculture: { label: 'Agriculture', title: 'Agriculture Companies in Nigeria', desc: 'Find agriculture companies, farms, and agribusinesses across Nigeria. Browse contact info and services.' },
  transportation: { label: 'Transport', title: 'Transportation Companies in Nigeria', desc: 'Find transport, logistics, courier, and shipping companies across Nigeria. Browse contact info and services.' },
  shopping: { label: 'Shopping', title: 'Shopping & Retail in Nigeria', desc: 'Find online stores, supermarkets, and retail shops across Nigeria. Browse contact info and services.' },
  business: { label: 'Business', title: 'Business Services in Nigeria', desc: 'Find business services, consulting firms, and professional services across all Nigerian cities.' },
  realestate: { label: 'Real Estate', title: 'Real Estate Companies in Nigeria', desc: 'Find real estate agents, property developers, estate surveyors, and property managers across all Nigerian cities.' },
  oilgas: { label: 'Oil & Gas', title: 'Oil & Gas Companies in Nigeria', desc: 'Find oil and gas companies, petroleum marketers, and energy service providers across all Nigerian states.' },
  construction: { label: 'Construction', title: 'Construction Companies in Nigeria', desc: 'Find construction companies, building contractors, and civil engineering firms across all Nigerian states.' }
};

async function loadData(category) {
  currentCategory = category || 'hotels';
  const file = DATA_FILES[currentCategory] || DATA_FILES.hotels;
  try {
    const resp = await fetch(file);
    allData = await resp.json();
    const countEl = document.getElementById('totalCount');
    if (countEl) countEl.textContent = allData.length;
    const labelEl = document.getElementById('categoryLabel');
    if (labelEl) {
      const labels = { hotels: 'hotels listed', hospitals: 'hospitals listed', schools: 'schools listed', agriculture: 'agriculture listings', transportation: 'transport listings', shopping: 'shopping listings', business: 'business listings', realestate: 'real estate listings', oilgas: 'oil & gas listings', construction: 'construction listings' };
      labelEl.textContent = labels[currentCategory] || 'listings';
    }
    const cityCountEl = document.getElementById('cityCount');
    if (cityCountEl) {
      const cities = new Set(allData.map(d => d.city).filter(Boolean));
      cityCountEl.textContent = cities.size;
    }
    populateCityFilter();
    return allData;
  } catch (e) {
    console.error('Failed to load data:', e);
    return [];
  }
}

function populateCityFilter() {
  const select = document.getElementById('cityFilter');
  if (!select) return;
  select.innerHTML = '<option value="">All Cities</option>';
  const cities = [...new Set(allData.map(d => d.city).filter(Boolean))].sort();
  cities.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c;
    opt.textContent = c;
    select.appendChild(opt);
  });
}

function handleSearch(query) {
  const grid = document.getElementById('listingGrid');
  if (!grid) return;
  query = query.trim().toLowerCase();

  filteredData = allData.filter(item => {
    const name = (item.name || '').toLowerCase();
    const city = (item.city || '').toLowerCase();
    const desc = (item.description || '').toLowerCase();
    const phone = (item.phone || '');
    return `${name} ${city} ${desc} ${phone}`.includes(query);
  });

  applyFilters();
}

function applyFilters() {
  const cityFilter = document.getElementById('cityFilter');
  const grid = document.getElementById('listingGrid');
  if (!grid) return;

  let results = filteredData.length ? filteredData : allData;

  if (cityFilter && cityFilter.value) {
    results = results.filter(d => d.city === cityFilter.value);
  }

  const noResults = document.getElementById('noResults');
  if (noResults) noResults.style.display = results.length ? 'none' : 'block';

  renderGrid(results);
}

function renderGrid(items) {
  const grid = document.getElementById('listingGrid');
  const loading = document.getElementById('loading');
  if (!grid) return;
  if (loading) loading.style.display = 'none';

  grid.innerHTML = items.map((item, index) => {
    const id = item.url?.match(/(\d+)\/$/)?.[1] || '';
    const phone = item.phone || '';
    const desc = item.description || '';
    const city = item.city || '';
    const email = item.email || '';

    return `
      <article class="card" onclick="showDetail('${currentCategory}', '${id}')" role="listitem">
        <div class="card-body">
          <h3>${escapeHtml(item.name || 'Unnamed')}</h3>
          <div class="card-city">${escapeHtml(city)}</div>
          ${phone ? `<a href="tel:${phone}" class="card-phone" onclick="event.stopPropagation();">${escapeHtml(phone)}</a>` : ''}
          ${desc ? `<div class="card-desc">${escapeHtml(desc)}</div>` : ''}
          <div class="card-footer">
            ${email ? `<span class="card-badge">Has Email</span>` : `<span class="card-badge">Phone Only</span>`}
            <span class="card-claim">View Details &rarr;</span>
          </div>
        </div>
      </article>
    `;
  }).join('');
}

async function loadListings(category) {
  await loadData(category);
  filteredData = allData;
  updateListingPageMeta(category);
  renderGrid(allData);
}

function updateListingPageMeta(category) {
  const catInfo = CATEGORY_NAMES[category] || CATEGORY_NAMES.hotels;
  const titleEl = document.getElementById('dynamicTitle');
  const descEl = document.getElementById('dynamicDesc');
  const ogTitle = document.getElementById('ogTitle');
  const ogDesc = document.getElementById('ogDesc');
  const twTitle = document.getElementById('twTitle');
  const twDesc = document.getElementById('twDesc');

  if (titleEl) titleEl.textContent = `${catInfo.title} - BusinessMen Nigeria Directory`;
  if (descEl) descEl.setAttribute('content', catInfo.desc);
  if (ogTitle) ogTitle.setAttribute('content', `${catInfo.title} | BusinessMen Nigeria`);
  if (ogDesc) ogDesc.setAttribute('content', catInfo.desc);
  if (twTitle) twTitle.setAttribute('content', `${catInfo.title} | BusinessMen Nigeria`);
  if (twDesc) twDesc.setAttribute('content', catInfo.desc);
}

function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function showDetail(cat, id) {
  if (!id) return;
  const item = allData.find(d => {
    const match = d.url?.match(/(\d+)\/$/);
    return match && match[1] === id;
  });
  if (!item) return;

  const listView = document.getElementById('listView');
  const detailView = document.getElementById('listingDetail');
  const loading = document.getElementById('loading');
  if (listView) listView.style.display = 'none';
  if (detailView) detailView.style.display = '';
  if (loading) loading.style.display = 'none';

  const url = new URL(window.location);
  url.searchParams.set('cat', cat);
  url.searchParams.set('id', id);
  history.pushState({cat, id}, '', url);

  renderDetailView(item, cat);
}

function closeDetail() {
  const params = new URLSearchParams(window.location.search);
  const cat = params.get('cat') || 'hotels';
  const listView = document.getElementById('listView');
  const detailView = document.getElementById('listingDetail');
  if (listView) listView.style.display = '';
  if (detailView) detailView.style.display = 'none';

  const url = new URL(window.location);
  url.searchParams.delete('id');
  history.pushState({cat}, '', url);
}

function renderDetailView(item, cat) {
  const container = document.getElementById('listingDetail');
  if (!container) return;

  const phone = item.phone || '';
  const email = item.email || '';
  const website = item.website || '';
  const city = item.city || '';
  const address = item.address || '';
  const hours = item.working_hours || '';
  const desc = item.description || '';
  const products = item.products || '';
  const catLabel = CATEGORY_NAMES[cat]?.label || 'Listings';
  const businessName = item.name || 'Business';

  container.innerHTML = `
    <nav aria-label="Breadcrumb">
      <a href="#" onclick="closeDetail(); return false;" class="back-link">&larr; Back to ${escapeHtml(catLabel)}</a>
    </nav>
    <div class="detail-header">
      <div>
        <h1>${escapeHtml(businessName)}</h1>
        ${city ? `<p style="color:#6b7280;margin-top:4px;">${escapeHtml(city)}, Nigeria</p>` : ''}
      </div>
      <div class="detail-actions">
        <a href="claim.html?business=${encodeURIComponent(businessName)}" class="btn-secondary" rel="nofollow">Claim this Business</a>
      </div>
    </div>

    <div class="detail-body">
      <section class="detail-section">
        <h2>Contact Information</h2>
        ${address ? `<div class="info-row"><span class="label">Address</span><span class="value">${escapeHtml(address)}</span></div>` : ''}
        ${phone ? `<div class="info-row"><span class="label">Phone</span><span class="value"><a href="tel:${phone}" rel="nofollow">${escapeHtml(phone)}</a></span></div>` : ''}
        ${email ? `<div class="info-row"><span class="label">Email</span><span class="value"><a href="mailto:${email}" rel="nofollow">${escapeHtml(email)}</a></span></div>` : ''}
        ${website ? `<div class="info-row"><span class="label">Website</span><span class="value"><a href="${website}" target="_blank" rel="noopener noreferrer">${escapeHtml(website)}</a></span></div>` : ''}
        ${hours ? `<div class="info-row"><span class="label">Hours</span><span class="value">${escapeHtml(hours)}</span></div>` : ''}
        ${!address && !phone && !email && !website && !hours ? '<p>No contact info available.</p>' : ''}
        ${phone || email || website ? '<p style="margin-top:12px;font-size:0.8rem;color:#9ca3af;">Contact information is verified from public sources.</p>' : ''}
      </section>

      <section class="detail-section">
        <h2>About ${escapeHtml(businessName)}</h2>
        ${desc ? `<p>${escapeHtml(desc)}</p>` : `<p>${escapeHtml(businessName)} is a ${catLabel.toLowerCase().slice(0, -1)} business located in ${escapeHtml(city || 'Nigeria')}.</p>`}
        ${city ? `<p style="margin-top:10px;color:#6b7280;font-size:0.9rem;">Serving the ${escapeHtml(city)} area and surrounding regions in Nigeria.</p>` : ''}
      </section>

      ${products ? `
      <section class="detail-section">
        <h2>Products & Services</h2>
        <div class="products-box">${products}</div>
      </section>
      ` : ''}

      <section class="detail-section">
        <h2>Claim This Listing</h2>
        <p style="color:#6b7280;font-size:0.9rem;">Is this your business? Claim your page on BusinessMen to update information, add products and services, and respond to customer inquiries.</p>
        <a href="claim.html?business=${encodeURIComponent(businessName)}" class="btn-primary" style="display:inline-block;margin-top:12px;" rel="nofollow">Claim Now</a>
      </section>
    </div>
  `;
}

window.addEventListener('popstate', () => {
  const params = new URLSearchParams(window.location.search);
  const id = params.get('id');
  if (id) {
    showDetail(params.get('cat') || 'hotels', id);
  } else {
    const listView = document.getElementById('listView');
    const detailView = document.getElementById('listingDetail');
    if (listView) listView.style.display = '';
    if (detailView) detailView.style.display = 'none';
  }
});

async function loadListingDetail() {
  const params = new URLSearchParams(window.location.search);
  const id = params.get('id');
  const cat = params.get('cat') || 'hotels';
  const query = params.get('q') || '';
  const cityParam = params.get('city') || '';

  const listView = document.getElementById('listView');
  const detailView = document.getElementById('listingDetail');
  const loading = document.getElementById('loading');

  if (!id) {
    if (listView) listView.style.display = '';
    if (detailView) detailView.style.display = 'none';
    await loadListings(cat);
    if (query || cityParam) {
      if (query) {
        const el = document.getElementById('heroQuery');
        if (el) el.value = query;
      }
      if (cityParam) {
        const el = document.getElementById('cityFilter');
        if (el) el.value = cityParam;
      }
      handleSearch(query);
      if (cityParam) applyFilters();
    }
    if (loading) loading.style.display = 'none';
    return;
  }

  await loadData(cat);
  if (loading) loading.style.display = 'none';
  showDetail(cat, id);
}

async function loadFeatured() {
  const grid = document.getElementById('featuredGrid');
  if (!grid) return;
  const entries = Object.entries(DATA_FILES).filter(([k]) => k !== 'business');
  const results = [];
  for (const [cat, file] of entries) {
    try {
      const resp = await fetch(file);
      if (!resp.ok) continue;
      const data = await resp.json();
      const items = Array.isArray(data) ? data : [];
      if (!items.length) continue;
      const pick = items[Math.floor(Math.random() * items.length)];
      const id = pick.url?.match(/(\d+)\/$/)?.[1] || '';
      if (id) results.push({ cat, id, name: pick.name, city: pick.city, phone: pick.phone, description: pick.description });
    } catch (e) { /* skip */ }
  }
  if (!results.length) return;
  results.sort(() => Math.random() - 0.5);
  grid.innerHTML = results.map(item => `
    <a href="listing.html?cat=${item.cat}&id=${item.id}" class="featured-card">
      <span class="featured-badge">Featured</span>
      <div class="featured-card-body">
        <h3>${item.name || 'Unnamed'}</h3>
        <div class="featured-city">${item.city || ''}</div>
        ${item.phone ? `<span class="featured-phone">${item.phone}</span>` : ''}
        ${item.description ? `<p class="featured-desc">${item.description}</p>` : ''}
        <span class="featured-view">View Details &rarr;</span>
      </div>
    </a>
  `).join('');
}

function submitClaim() {
  const success = document.getElementById('claimSuccess');
  const form = document.querySelector('.claim-form');
  if (form) form.style.display = 'none';
  if (success) success.style.display = 'block';
}

window.handleSearch = handleSearch;
window.applyFilters = applyFilters;
window.loadListings = loadListings;
window.loadListingDetail = loadListingDetail;
window.loadFeatured = loadFeatured;
window.submitClaim = submitClaim;
