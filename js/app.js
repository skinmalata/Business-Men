let allData = [];
let filteredData = [];
let currentCategory = 'hotels';

const DATA_FILES = {
  hotels: 'data/nigeria_hotels.json',
  hospitals: 'data/nigeria_hospitals.json',
  schools: 'data/nigeria_schools.json',
  agriculture: 'data/nigeria_agriculture.json'
};

const CATEGORY_NAMES = {
  hotels: { label: 'Hotels', title: 'Hotels in Nigeria', desc: 'Find hotels, resorts, and accommodation across all Nigerian cities. Browse contact info, addresses, and services.' },
  hospitals: { label: 'Hospitals', title: 'Hospitals in Nigeria', desc: 'Find hospitals, medical centres, and healthcare providers across Nigeria. Browse contact info and services.' },
  schools: { label: 'Schools', title: 'Schools & Universities in Nigeria', desc: 'Find schools, universities, colleges, and educational institutions across all Nigerian states.' },
  agriculture: { label: 'Agriculture', title: 'Agriculture Companies in Nigeria', desc: 'Find agriculture companies, farms, and agribusinesses across Nigeria. Browse contact info and services.' }
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
      const labels = { hotels: 'hotels listed', hospitals: 'hospitals listed', schools: 'schools listed', agriculture: 'agriculture listings' };
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
      <article class="card" onclick="location.href='listing.html?cat=${currentCategory}&id=${id}'" role="listitem">
        <div class="card-body">
          <h3>${item.name || 'Unnamed'}</h3>
          <div class="card-city">${city}</div>
          ${phone ? `<a href="tel:${phone}" class="card-phone" onclick="event.stopPropagation();">${phone}</a>` : ''}
          ${desc ? `<div class="card-desc">${desc}</div>` : ''}
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

async function loadListingDetail() {
  const params = new URLSearchParams(window.location.search);
  const id = params.get('id');
  const cat = params.get('cat') || 'hotels';

  if (!id) {
    loadListings(cat);
    return;
  }

  await loadData(cat);
  const loading = document.getElementById('loading');
  const container = document.getElementById('listingDetail');
  if (loading) loading.style.display = 'none';
  if (!container) return;

  const item = allData.find(d => {
    const match = d.url?.match(/(\d+)\/$/);
    return match && match[1] === id;
  });

  if (!item) {
    container.innerHTML = `<p>Listing not found. <a href="listing.html?cat=${cat}">Browse ${CATEGORY_NAMES[cat]?.label || cat}</a></p>`;
    return;
  }

  const phone = item.phone || '';
  const email = item.email || '';
  const website = item.website || '';
  const city = item.city || '';
  const address = item.address || '';
  const hours = item.working_hours || '';
  const desc = item.description || '';
  const products = item.products || '';

  const catLabel = CATEGORY_NAMES[cat]?.label || 'Listings';

  // Update SEO meta tags for this listing
  const businessName = item.name || 'Business';
  const metaDesc = `${businessName} in ${city || 'Nigeria'}. ${desc ? desc.slice(0, 120) : ''} Contact: ${phone || 'call for details'}. View on BusinessMen Nigeria Directory.`;

  const titleEl = document.getElementById('dynamicTitle');
  const descEl = document.getElementById('dynamicDesc');
  const ogUrl = document.getElementById('ogUrl');
  const ogTitle = document.getElementById('ogTitle');
  const ogDesc = document.getElementById('ogDesc');
  const twTitle = document.getElementById('twTitle');
  const twDesc = document.getElementById('twDesc');

  if (titleEl) titleEl.textContent = `${businessName} | ${city || 'Nigeria'} - BusinessMen Directory`;
  if (descEl) descEl.setAttribute('content', metaDesc);
  if (ogUrl) ogUrl.setAttribute('content', `https://skinmalata.github.io/Business-Men/listing.html?cat=${cat}&id=${id}`);
  if (ogTitle) ogTitle.setAttribute('content', `${businessName} | BusinessMen Nigeria`);
  if (ogDesc) ogDesc.setAttribute('content', metaDesc);
  if (twTitle) twTitle.setAttribute('content', `${businessName} | BusinessMen Nigeria`);
  if (twDesc) twDesc.setAttribute('content', metaDesc);

  // Update breadcrumb schema
  const breadSchema = document.getElementById('breadcrumbSchema');
  if (breadSchema) {
    breadSchema.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "BusinessMen", "item": "https://skinmalata.github.io/Business-Men/"},
        {"@type": "ListItem", "position": 2, "name": catLabel, "item": `https://skinmalata.github.io/Business-Men/listing.html?cat=${cat}`},
        {"@type": "ListItem", "position": 3, "name": businessName}
      ]
    });
  }

  // Build JSON-LD for this LocalBusiness
  const ldScript = document.createElement('script');
  ldScript.type = 'application/ld+json';
  const ld = {
    "@context": "https://schema.org",
    "@type": ["LocalBusiness", ...(cat === 'hospitals' ? ['MedicalBusiness'] : []), ...(cat === 'schools' ? ['EducationalOrganization'] : [])],
    "name": businessName,
    "description": desc || `${businessName} is a ${catLabel.toLowerCase().slice(0, -1)} business in ${city || 'Nigeria'}.`,
    "url": item.url || `https://skinmalata.github.io/Business-Men/listing.html?cat=${cat}&id=${id}`,
    "telephone": phone || undefined,
    "email": email || undefined,
    "address": address ? {
      "@type": "PostalAddress",
      "streetAddress": address,
      "addressLocality": city || undefined,
      "addressCountry": "NG"
    } : undefined,
    "areaServed": { "@type": "City", "name": city || "Nigeria" }
  };
  if (website) ld.sameAs = [website];
  if (hours) ld.openingHours = hours;
  ldScript.textContent = JSON.stringify(ld);
  document.head.appendChild(ldScript);

  // Render detail
  container.innerHTML = `
    <nav aria-label="Breadcrumb">
      <a href="listing.html?cat=${cat}" class="back-link">&larr; Back to ${catLabel}</a>
    </nav>
    <div class="detail-header">
      <div>
        <h1>${item.name || 'Unnamed'}</h1>
        ${city ? `<p style="color:#6b7280;margin-top:4px;">${city}, Nigeria</p>` : ''}
      </div>
      <div class="detail-actions">
        <a href="claim.html?business=${encodeURIComponent(item.name)}" class="btn-secondary" rel="nofollow">Claim this Business</a>
      </div>
    </div>

    <div class="detail-body">
      <section class="detail-section">
        <h2>Contact Information</h2>
        ${address ? `<div class="info-row"><span class="label">Address</span><span class="value">${address}</span></div>` : ''}
        ${phone ? `<div class="info-row"><span class="label">Phone</span><span class="value"><a href="tel:${phone}" rel="nofollow">${phone}</a></span></div>` : ''}
        ${email ? `<div class="info-row"><span class="label">Email</span><span class="value"><a href="mailto:${email}" rel="nofollow">${email}</a></span></div>` : ''}
        ${website ? `<div class="info-row"><span class="label">Website</span><span class="value"><a href="${website}" target="_blank" rel="noopener noreferrer">${website}</a></span></div>` : ''}
        ${hours ? `<div class="info-row"><span class="label">Hours</span><span class="value">${hours}</span></div>` : ''}
        ${!address && !phone && !email && !website && !hours ? '<p>No contact info available.</p>' : ''}

        ${phone || email || website ? '<p style="margin-top:12px;font-size:0.8rem;color:#9ca3af;">Contact information is verified from public sources.</p>' : ''}
      </section>

      <section class="detail-section">
        <h2>About ${businessName}</h2>
        ${desc ? `<p>${desc}</p>` : `<p>${businessName} is a ${catLabel.toLowerCase().slice(0, -1)} business located in ${city || 'Nigeria'}.</p>`}
        ${city ? `<p style="margin-top:10px;color:#6b7280;font-size:0.9rem;">Serving the ${city} area and surrounding regions in Nigeria.</p>` : ''}
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
        <a href="claim.html?business=${encodeURIComponent(item.name)}" class="btn-primary" style="display:inline-block;margin-top:12px;" rel="nofollow">Claim Now</a>
      </section>
    </div>
  `;
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
window.submitClaim = submitClaim;
