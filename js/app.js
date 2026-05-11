let allData = [];
let filteredData = [];
let currentCategory = 'hotels';
let currentPage = 1;
const ITEMS_PER_PAGE = 20;
let searchTimeout = null;

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
  construction: 'data/nigeria_construction.json',
  automobile: 'data/nigeria_automobile.json',
  food: 'data/nigeria_food.json'
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
  construction: { label: 'Construction', title: 'Construction Companies in Nigeria', desc: 'Find construction companies, building contractors, and civil engineering firms across all Nigerian states.' },
  automobile: { label: 'Automobile', title: 'Automobile Companies in Nigeria', desc: 'Find automobile dealers, car manufacturers, auto repair shops, and automotive service providers across all Nigerian states.' },
  food: { label: 'Food & Restaurants', title: 'Food & Restaurants in Nigeria', desc: 'Find restaurants, food companies, caterers, bakeries, and food processing companies across all Nigerian states.' }
};

async function loadData(category) {
  currentCategory = category || 'hotels';
  const file = DATA_FILES[currentCategory] || DATA_FILES.hotels;
  showSkeletons();
  try {
    const resp = await fetch(file);
    allData = await resp.json();
    const countEl = document.getElementById('totalCount');
    if (countEl) countEl.textContent = allData.length;
    const labelEl = document.getElementById('categoryLabel');
    if (labelEl) {
      const labels = { hotels: 'hotels listed', hospitals: 'hospitals listed', schools: 'schools listed', agriculture: 'agriculture listings', transportation: 'transport listings', shopping: 'shopping listings', business: 'business listings', realestate: 'real estate listings', oilgas: 'oil & gas listings', construction: 'construction listings', automobile: 'automobile listings', food: 'food & restaurants listed' };
      labelEl.textContent = labels[currentCategory] || 'listings';
    }
    const cityCountEl = document.getElementById('cityCount');
    if (cityCountEl) {
      const cities = new Set(allData.map(d => d.city).filter(Boolean));
      cityCountEl.textContent = cities.size;
    }
    const verifiedEl = document.getElementById('statVerified');
    if (verifiedEl) {
      const verifiedCount = allData.filter(d => d.verified === true).length;
      verifiedEl.textContent = verifiedCount;
    }
    populateCityFilter();
    return allData;
  } catch (e) {
    console.error('Failed to load data:', e);
    return [];
  }
}

function showSkeletons() {
  const grid = document.getElementById('listingGrid');
  const skeletonContainer = document.getElementById('skeletonGrid');
  if (skeletonContainer) skeletonContainer.style.display = 'grid';
  if (grid) grid.innerHTML = '';
  currentPage = 1;
}

function hideSkeletons() {
  const el = document.getElementById('skeletonGrid');
  if (el) el.style.display = 'none';
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
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
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

    currentPage = 1;
    applyFilters();
  }, 250);
}

function handleSort(sortBy) {
  const grid = document.getElementById('listingGrid');
  if (!grid) return;
  currentPage = 1;
  applyFilters();
}

function applyFilters() {
  const cityFilter = document.getElementById('cityFilter');
  const sortBy = document.getElementById('sortFilter');
  const grid = document.getElementById('listingGrid');
  if (!grid) return;

  let results = filteredData.length ? filteredData : allData;

  if (cityFilter && cityFilter.value) {
    results = results.filter(d => d.city === cityFilter.value);
  }

  if (sortBy && sortBy.value) {
    const val = sortBy.value;
    if (val === 'verified') results.sort((a, b) => (b.verified === true) - (a.verified === true));
    else if (val === 'name') results.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
    else if (val === 'city') results.sort((a, b) => (a.city || '').localeCompare(b.city || ''));
  }

  const noResults = document.getElementById('noResults');
  if (noResults) noResults.style.display = results.length ? 'none' : 'block';

  const totalPages = Math.max(1, Math.ceil(results.length / ITEMS_PER_PAGE));
  if (currentPage > totalPages) currentPage = totalPages;

  const start = (currentPage - 1) * ITEMS_PER_PAGE;
  const pageItems = results.slice(start, start + ITEMS_PER_PAGE);

  hideSkeletons();
  renderGrid(pageItems);
  renderPagination(results.length, totalPages);
  updateResultsCount(results.length, start, pageItems.length);
}

function updateResultsCount(total, start, count) {
  const el = document.getElementById('resultsCount');
  if (!el) return;
  if (total === 0) {
    el.textContent = 'No results found';
    return;
  }
  el.textContent = `Showing ${start + 1}\u2013${start + count} of ${total}`;
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
    const verified = item.verified === true;

    const reviewCount = item.review_count || 0;
    const starsHtml = reviewCount > 0 ? `<span class="card-stars" title="${reviewCount} review${reviewCount > 1 ? 's' : ''}">${'★'.repeat(Math.min(reviewCount, 5))}${'☆'.repeat(Math.max(0, 5 - Math.min(reviewCount, 5)))} <small>${reviewCount}</small></span>` : '';

    return `
      <article class="card" onclick="showDetail('${currentCategory}', '${id}')" role="listitem">
        <div class="card-body">
          <h3>${escapeHtml(item.name || 'Unnamed')} ${verified ? '<span class="verified-badge" title="Verified Business">\u2713</span>' : ''}</h3>
          <div class="card-city">${escapeHtml(city)}</div>
          ${phone ? `<a href="tel:${phone}" class="card-phone" onclick="event.stopPropagation();">${escapeHtml(phone)}</a>` : ''}
          ${desc ? `<div class="card-desc">${escapeHtml(desc)}</div>` : ''}
          <div class="card-footer">
            <span class="card-badge ${verified ? 'verified' : 'unverified'}">${verified ? 'Verified' : 'Unverified'}</span>
            ${starsHtml}
            <span class="card-claim">View Details &rarr;</span>
          </div>
        </div>
      </article>
    `;
  }).join('');
}

function renderPagination(total, totalPages) {
  const container = document.getElementById('pagination');
  if (!container) return;

  if (total <= ITEMS_PER_PAGE) {
    container.innerHTML = '';
    return;
  }

  let html = '';
  html += `<button onclick="goToPage(${currentPage - 1})" ${currentPage <= 1 ? 'disabled' : ''}>&larr; Prev</button>`;

  const startPage = Math.max(1, currentPage - 2);
  const endPage = Math.min(totalPages, currentPage + 2);

  if (startPage > 1) {
    html += `<button onclick="goToPage(1)">1</button>`;
    if (startPage > 2) html += `<span class="page-info">...</span>`;
  }

  for (let i = startPage; i <= endPage; i++) {
    html += `<button onclick="goToPage(${i})" class="${i === currentPage ? 'active' : ''}">${i}</button>`;
  }

  if (endPage < totalPages) {
    if (endPage < totalPages - 1) html += `<span class="page-info">...</span>`;
    html += `<button onclick="goToPage(${totalPages})">${totalPages}</button>`;
  }

  html += `<button onclick="goToPage(${currentPage + 1})" ${currentPage >= totalPages ? 'disabled' : ''}>Next &rarr;</button>`;

  container.innerHTML = html;
  container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function goToPage(page) {
  currentPage = page;
  applyFilters();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function loadListings(category) {
  await loadData(category);
  filteredData = allData;
  updateListingPageMeta(category);
  applyFilters();
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
  window.scrollTo({ top: 0, behavior: 'smooth' });
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
  const verified = item.verified === true;

  const id = item.url?.match(/(\d+)\/$/)?.[1] || '';
  const reviewCount = item.review_count || 0;
  const savedReviews = getReviews(id);
  const totalReviews = reviewCount + savedReviews.length;
  const avgRating = calcAvgRating(savedReviews);

  container.innerHTML = `
    <nav aria-label="Breadcrumb">
      <a href="#" onclick="closeDetail(); return false;" class="back-link">&larr; Back to ${escapeHtml(catLabel)}</a>
    </nav>
    <div class="detail-header">
      <div>
        <h1>${escapeHtml(businessName)} ${verified ? '<span class="verified-badge-lg" title="Verified Business">\u2713 Verified</span>' : '<span class="unverified-badge" title="Unverified Business">Unverified</span>'}</h1>
        ${city ? `<p style="margin-top:6px;">${escapeHtml(city)}, Nigeria</p>` : ''}
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
        ${phone || email || website ? '<p style="margin-top:16px;font-size:0.8rem;color:#94a3b8;">Contact information sourced from public business directories.</p>' : ''}
      </section>

      <section class="detail-section">
        <h2>About ${escapeHtml(businessName)}</h2>
        ${desc ? `<p>${escapeHtml(desc)}</p>` : `<p>${escapeHtml(businessName)} is a ${catLabel.toLowerCase().slice(0, -1)} business located in ${escapeHtml(city || 'Nigeria')}.</p>`}
        ${city ? `<p style="margin-top:12px;color:#64748b;font-size:0.9rem;">Serving the ${escapeHtml(city)} area and surrounding regions in Nigeria.</p>` : ''}
      </section>

      ${products ? `
      <section class="detail-section">
        <h2>Products & Services</h2>
        <div class="products-box">${products}</div>
      </section>
      ` : ''}

      <section class="detail-section detail-section-full reviews-section">
        <h2>Reviews & Ratings ${totalReviews > 0 ? `<span class="review-count-badge">${totalReviews}</span>` : ''}</h2>
        ${totalReviews > 0 ? `
        <div class="review-summary">
          <div class="review-summary-stars">
            ${renderStars(avgRating, 24)}
            <span class="review-summary-text">${avgRating > 0 ? avgRating.toFixed(1) : '?'} out of 5</span>
          </div>
          <p class="review-summary-count">Based on ${totalReviews} review${totalReviews !== 1 ? 's' : ''}</p>
        </div>
        ` : '<p style="color:#64748b;">No reviews yet. Be the first to review!</p>'}

        <div class="review-list" id="reviewList">
          ${savedReviews.map(r => `
          <div class="review-card">
            <div class="review-header">
              <div class="review-avatar">${(r.name || 'A')[0].toUpperCase()}</div>
              <div>
                <div class="review-name">${escapeHtml(r.name || 'Anonymous')}</div>
                <div class="review-stars">${renderStars(r.rating || 0, 14)}</div>
              </div>
              <span class="review-date">${r.date || ''}</span>
            </div>
            ${r.text ? `<p class="review-text">${escapeHtml(r.text)}</p>` : ''}
          </div>
          `).join('')}
        </div>

      </section>

      <section class="detail-section detail-section-full">
        <h2>Write a Review</h2>
        <form class="review-form" onsubmit="submitReview(event, '${id}')">
          <div class="form-group">
            <label for="reviewName">Your Name</label>
            <input type="text" id="reviewName" required placeholder="Enter your name">
          </div>
          <div class="form-group">
            <label>Your Rating</label>
            <div class="star-rating" id="starRating">
              ${[1,2,3,4,5].map(i => `<span class="star" data-value="${i}" onclick="setRating(${i})" onmouseover="hoverRating(${i})" onmouseout="resetRating()">☆</span>`).join('')}
            </div>
            <input type="hidden" id="reviewRating" value="0">
          </div>
          <div class="form-group">
            <label for="reviewText">Your Review</label>
            <textarea id="reviewText" rows="4" placeholder="Share your experience with this business..." required></textarea>
          </div>
          <button type="submit" class="btn-primary">Submit Review</button>
        </form>
      </section>

      <section class="detail-section">
        <h2>Claim This Listing</h2>
        <p style="color:#64748b;font-size:0.9rem;">Is this your business? Claim your page on BusinessMen to update information, add products and services, and respond to customer inquiries.</p>
        <a href="claim.html?business=${encodeURIComponent(businessName)}" class="btn-primary" style="display:inline-block;margin-top:14px;" rel="nofollow">Claim Now</a>
      </section>
    </div>
  `;
}

// === REVIEWS ===
function getReviews(businessId) {
  try {
    return JSON.parse(localStorage.getItem('reviews_' + businessId)) || [];
  } catch { return []; }
}

function saveReviews(businessId, reviews) {
  localStorage.setItem('reviews_' + businessId, JSON.stringify(reviews));
}

function calcAvgRating(reviews) {
  if (!reviews.length) return 0;
  return reviews.reduce((s, r) => s + (r.rating || 0), 0) / reviews.length;
}

function renderStars(rating, size) {
  const full = Math.round(rating);
  let s = '';
  for (let i = 1; i <= 5; i++) {
    s += i <= full
      ? `<span class="star-filled" style="font-size:${size}px">★</span>`
      : `<span class="star-empty" style="font-size:${size}px">☆</span>`;
  }
  return s;
}

let selectedRating = 0;
function setRating(val) {
  selectedRating = val;
  document.getElementById('reviewRating').value = val;
  const stars = document.querySelectorAll('#starRating .star');
  stars.forEach((s, i) => {
    s.textContent = i < val ? '★' : '☆';
    s.style.color = i < val ? '#f59e0b' : '#d1d9e6';
  });
}
function hoverRating(val) {
  const stars = document.querySelectorAll('#starRating .star');
  stars.forEach((s, i) => {
    s.textContent = i < val ? '★' : '☆';
    s.style.color = i < val ? '#f59e0b' : '#d1d9e6';
  });
}
function resetRating() {
  const stars = document.querySelectorAll('#starRating .star');
  stars.forEach((s, i) => {
    s.textContent = i < selectedRating ? '★' : '☆';
    s.style.color = i < selectedRating ? '#f59e0b' : '#d1d9e6';
  });
}

function submitReview(e, businessId) {
  e.preventDefault();
  const name = document.getElementById('reviewName').value.trim();
  const rating = parseInt(document.getElementById('reviewRating').value);
  const text = document.getElementById('reviewText').value.trim();

  if (!name || !rating || !text) {
    alert('Please fill in all fields and select a rating.');
    return;
  }

  const reviews = getReviews(businessId);
  reviews.unshift({
    name,
    rating,
    text,
    date: new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
  });
  saveReviews(businessId, reviews);

  // Re-render the detail view to show the new review
  const params = new URLSearchParams(window.location.search);
  const cat = params.get('cat') || 'hotels';
  const item = allData.find(d => {
    const match = d.url?.match(/(\d+)\/$/);
    return match && match[1] === businessId;
  });
  if (item) renderDetailView(item, cat);

  // Scroll to reviews section
  const reviewsSection = document.querySelector('.reviews-section');
  if (reviewsSection) reviewsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
      const verifiedItems = items.filter(d => d.verified === true);
      const pool = verifiedItems.length > 0 ? verifiedItems : items;
      const pick = pool[Math.floor(Math.random() * pool.length)];
      const id = pick.url?.match(/(\d+)\/$/)?.[1] || '';
      if (id) results.push({ cat, id, name: pick.name, city: pick.city, phone: pick.phone, description: pick.description, verified: pick.verified });
    } catch (e) { /* skip */ }
  }
  if (!results.length) return;
  results.sort(() => Math.random() - 0.5);
  grid.innerHTML = results.map(item => `
    <a href="listing.html?cat=${item.cat}&id=${item.id}" class="featured-card">
      <span class="featured-badge">Featured</span>
      <div class="featured-card-body">
        <h3>${item.name || 'Unnamed'} ${item.verified ? '<span class="verified-badge" title="Verified Business">\u2713</span>' : ''}</h3>
        <div class="featured-city">${item.city || ''}</div>
        ${item.phone ? `<span class="featured-phone">${item.phone}</span>` : ''}
        ${item.description ? `<p class="featured-desc">${item.description}</p>` : ''}
        <span class="featured-view">View Details</span>
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
window.goToPage = goToPage;
window.handleSort = handleSort;
window.submitReview = submitReview;
window.setRating = setRating;
window.hoverRating = hoverRating;
window.resetRating = resetRating;
