let allData = [];
let filteredData = [];
let currentCategory = 'all';
let currentPage = 1;
const ITEMS_PER_PAGE = 20;
let searchTimeout = null;
var __listingEditsList = [];

const CONSOLIDATED_DATA_FILE = 'data/nigeria_all_businesses.json';
const DATA_CACHE = {};

const CATEGORY_FILE_MAP = {
  all: 'data/nigeria_all_businesses.json',
  hotels: ['data/cat_hotel.json', 'data/cat_hotels.json'],
  hospitals: ['data/cat_hospital.json', 'data/cat_hospitals.json'],
  schools: ['data/cat_school.json', 'data/cat_schools.json'],
  agriculture: 'data/cat_agriculture.json',
  transportation: 'data/cat_transportation.json',
  shopping: 'data/cat_shopping.json',
  business: 'data/cat_business.json',
  realestate: 'data/cat_realestate.json',
  oilgas: 'data/cat_oilgas.json',
  construction: 'data/cat_construction.json',
  automobile: 'data/cat_automobile.json',
  food: ['data/cat_food.json', 'data/cat_restaurant.json'],
  general: 'data/cat_general.json'
};

async function applyListingEdits() {
  if (typeof db === 'undefined') return;
  try {
    var snapshot = await db.collection('listingEdits').get();
    var edits = {};
    __listingEditsList = [];
    snapshot.forEach(function(doc) {
      edits[doc.id] = doc.data();
      __listingEditsList.push({ id: doc.id, data: doc.data() });
    });
    allData.forEach(function(b) {
      var override = edits[b._uid];
      if (!override && b.url) {
        var numId = b.url.match(/(\d+)\/$/)?.[1];
        if (numId) {
          var slug = (b.name || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
          override = edits[slug + '-' + numId] || edits[numId];
        }
      }
      if (!override && b.name && __listingEditsList.length) {
        var bName = (b.name || '').toLowerCase().trim();
        var bCity = (b.city || '').toLowerCase().trim();
        for (var li = 0; li < __listingEditsList.length; li++) {
          var ed = __listingEditsList[li].data;
          var edName = (ed._businessName || '').toLowerCase().trim();
          var edCity = (ed._businessCity || '').toLowerCase().trim();
          if (edName && edName === bName && edCity && edCity === bCity) {
            override = ed;
            break;
          }
        }
      }
      if (override) {
        if (override.phone) b.phone = override.phone;
        if (override.whatsapp) b.whatsapp = override.whatsapp;
        if (override.address) b.address = override.address;
      }
    });
  } catch (e) {
    console.warn('Failed to load listing edits:', e);
  }
}

async function loadCategoryFiles(files) {
  if (typeof files === 'string') files = [files];
  const cacheKey = files.join('|');
  if (DATA_CACHE[cacheKey]) return DATA_CACHE[cacheKey];

  let combined = [];
  for (const file of files) {
    try {
      const resp = await fetch(file);
      const data = await resp.json();
      combined = combined.concat(data);
    } catch (e) {
      console.warn(`Failed to load ${file}:`, e);
    }
  }
  DATA_CACHE[cacheKey] = combined;
  return combined;
}

async function loadUserListings() {
  if (typeof db === 'undefined') return [];
  try {
    var snapshot = await db.collection('pendingSubmissions').get();
    var results = [];
    snapshot.forEach(function(doc) {
      var d = doc.data();
      if (d.confirmed === true && d.type === 'business') {
        results.push({
          name: d.name || 'Unnamed',
          city: d.state || '',
          phone: d.phone || '',
          website: d.website || '',
          email: d.email || '',
          address: d.address || '',
          description: d.description || '',
          category: (d.category || '').toLowerCase().replace(/[^a-z]+/g, ''),
          verified: true,
          _uid: 'user_' + doc.id,
          source: 'user_submitted'
        });
      }
    });
    return results;
  } catch (e) {
    console.warn('Failed to load user listings:', e);
    return [];
  }
}

async function loadData(category) {
  currentCategory = category || 'all';
  showSkeletons();
  try {
    const files = CATEGORY_FILE_MAP[currentCategory] || CATEGORY_FILE_MAP.general;
    allData = await loadCategoryFiles(files);

    var userListings = await loadUserListings();
    if (userListings.length > 0) {
      if (currentCategory === 'all') {
        allData = allData.concat(userListings);
      } else {
        var dataCat = CATEGORY_MAP[currentCategory] || currentCategory;
        var matching = userListings.filter(function(b) {
          if (Array.isArray(dataCat)) return dataCat.includes(b.category);
          return b.category === dataCat;
        });
        allData = allData.concat(matching);
      }
    }
    
    const countEl = document.getElementById('totalCount');
    if (countEl) countEl.textContent = allData.length;
    const labelEl = document.getElementById('categoryLabel');
    if (labelEl) {
      const labels = { all: 'businesses listed', hotels: 'hotels listed', hospitals: 'hospitals listed', schools: 'schools listed', agriculture: 'agriculture listings', transportation: 'transport listings', shopping: 'shopping listings', business: 'business listings', realestate: 'real estate listings', oilgas: 'oil & gas listings', construction: 'construction listings', automobile: 'automobile listings', food: 'food & restaurants listed', general: 'other listings' };
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
    allData.forEach(function(b, i) {
      var urlId = b.url && b.url.match(/(\d+)\/$/);
      b._uid = urlId ? urlId[1] : ((b.name || 'business').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '') + '-' + i);
    });
    await applyListingEdits();
    populateCityFilter();
    return allData;
  } catch (e) {
    console.error('Failed to load data:', e);
    return [];
  }
}

const CATEGORY_NAMES = {
  all: { label: 'All', title: 'All Businesses in Nigeria', desc: 'Browse all businesses across Nigeria. Search by name, city, or service.' },
  hotels: { label: 'Hotels', title: 'Hotels in Nigeria', desc: 'Find hotels, resorts, and accommodation across all Nigerian cities.' },
  hospitals: { label: 'Hospitals', title: 'Hospitals in Nigeria', desc: 'Find hospitals, medical centres, and healthcare providers across Nigeria.' },
  schools: { label: 'Schools', title: 'Schools & Universities in Nigeria', desc: 'Find schools, universities, colleges, and educational institutions across Nigeria.' },
  agriculture: { label: 'Agriculture', title: 'Agriculture Companies in Nigeria', desc: 'Find agriculture companies, farms, and agribusinesses across Nigeria.' },
  transportation: { label: 'Transport', title: 'Transportation Companies in Nigeria', desc: 'Find transport, logistics, courier, and shipping companies across Nigeria.' },
  shopping: { label: 'Shopping', title: 'Shopping & Retail in Nigeria', desc: 'Find online stores, supermarkets, and retail shops across Nigeria.' },
  business: { label: 'Business', title: 'Business Services in Nigeria', desc: 'Find business services, consulting firms, and professional services across Nigeria.' },
  realestate: { label: 'Real Estate', title: 'Real Estate Companies in Nigeria', desc: 'Find real estate agents, property developers, and estate surveyors across Nigeria.' },
  oilgas: { label: 'Oil & Gas', title: 'Oil & Gas Companies in Nigeria', desc: 'Find oil and gas companies, petroleum marketers, and energy providers across Nigeria.' },
  construction: { label: 'Construction', title: 'Construction Companies in Nigeria', desc: 'Find construction companies, building contractors, and engineering firms across Nigeria.' },
  automobile: { label: 'Automobile', title: 'Automobile Companies in Nigeria', desc: 'Find automobile dealers, car manufacturers, and auto repair shops across Nigeria.' },
  food: { label: 'Food & Restaurants', title: 'Food & Restaurants in Nigeria', desc: 'Find restaurants, food companies, caterers, and bakeries across Nigeria.' },
  general: { label: 'General', title: 'Other Businesses in Nigeria', desc: 'Find other businesses and services across Nigeria.' }
};

const CATEGORY_MAP = {
  'all': 'all',
  'hotels': 'hotel',
  'hospitals': 'hospital',
  'schools': ['school', 'schools'],
  'agriculture': 'agriculture',
  'transportation': 'transportation',
  'shopping': 'shopping',
  'business': 'business',
  'realestate': 'realestate',
  'oilgas': 'oilgas',
  'construction': 'construction',
  'automobile': 'automobile',
  'food': ['food', 'restaurant'],
  'general': 'general'
};

async function loadData(category) {
  currentCategory = category || 'all';
  showSkeletons();
  try {
    const resp = await fetch(CONSOLIDATED_DATA_FILE);
    const allBusinesses = await resp.json();
    
    const dataCat = CATEGORY_MAP[currentCategory] || currentCategory;
    if (currentCategory === 'all') {
      allData = allBusinesses;
    } else if (Array.isArray(dataCat)) {
      allData = allBusinesses.filter(b => dataCat.includes((b.category || '').toLowerCase()));
    } else {
      allData = allBusinesses.filter(b => (b.category || '').toLowerCase() === dataCat);
    }

    var userListings = await loadUserListings();
    if (userListings.length > 0) {
      if (currentCategory === 'all') {
        allData = allData.concat(userListings);
      } else {
        var matching = userListings.filter(function(b) {
          if (Array.isArray(dataCat)) return dataCat.includes(b.category);
          return b.category === dataCat;
        });
        allData = allData.concat(matching);
      }
    }
    
    allData.forEach(function(b, i) {
      var urlId = b.url && b.url.match(/(\d+)\/$/);
      b._uid = urlId ? urlId[1] : ((b.name || 'business').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '') + '-' + i);
    });
    await applyListingEdits();
    
    const countEl = document.getElementById('totalCount');
    if (countEl) countEl.textContent = allData.length;
    const labelEl = document.getElementById('categoryLabel');
    if (labelEl) {
      const labels = { all: 'businesses listed', hotels: 'hotels listed', hospitals: 'hospitals listed', schools: 'schools listed', agriculture: 'agriculture listings', transportation: 'transport listings', shopping: 'shopping listings', business: 'business listings', realestate: 'real estate listings', oilgas: 'oil & gas listings', construction: 'construction listings', automobile: 'automobile listings', food: 'food & restaurants listed', general: 'other listings' };
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

function normalizeCityDisplay(city) {
  if (!city) return '';
  return city.replace(/\s*State\s*$/i, '').trim();
}

function normalizeStateMatch(dataCity, filterValue) {
  if (!dataCity || !filterValue) return false;
  const normalized = normalizeCityDisplay(dataCity);
  if (normalized === filterValue) return true;
  if (filterValue === 'Abuja FCT' && (normalized.includes('Abuja') || normalized.includes('FCT') || normalized.toLowerCase().includes('abuja fct'))) return true;
  if (normalized.includes(filterValue) || filterValue.includes(normalized)) return true;
  return false;
}

function populateCityFilter() {
  const select = document.getElementById('cityFilter');
  if (!select) return;
  const states = ['Abia','Adamawa','Akwa Ibom','Anambra','Bauchi','Bayelsa','Benue','Borno','Cross River','Delta','Ebonyi','Edo','Ekiti','Enugu','Abuja FCT','Gombe','Imo','Jigawa','Kaduna','Kano','Katsina','Kebbi','Kogi','Kwara','Lagos','Nasarawa','Niger','Ogun','Ondo','Osun','Oyo','Plateau','Rivers','Sokoto','Taraba','Yobe','Zamfara'];
  select.innerHTML = '<option value="">All States</option>' + states.map(s => '<option>' + s + '</option>').join('');
}

function handleSearch(query) {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    const grid = document.getElementById('listingGrid');
    if (!grid) return;
    query = (query || '').trim().toLowerCase();

    if (query.length === 0) {
      filteredData = [];
      currentPage = 1;
      applyFilters();
      return;
    }

    filteredData = allData.filter(item => {
      const name = (item.name || '').toLowerCase();
      const city = (item.city || '').toLowerCase();
      const desc = (item.description || '').toLowerCase();
      const phone = (item.phone || '');
      const address = (item.address || '').toLowerCase();
      const searchable = `${name} ${city} ${desc} ${phone} ${address}`;
      const terms = query.split(/\s+/);
      return terms.every(term => searchable.includes(term));
    });

    if (filteredData.length === 0 && currentCategory !== 'all' && query) {
      const params = new URLSearchParams();
      params.set('cat', 'all');
      params.set('q', query);
      window.location.href = 'listing.html?' + params.toString();
      return;
    }

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
    results = results.filter(d => normalizeStateMatch(d.city, cityFilter.value));
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
    const id = item._uid || '';
    const phone = item.phone || '';
    const desc = item.description || '';
    const city = item.city || '';
    const verified = item.verified === true;

    const reviewCount = item.review_count || 0;
    const starsHtml = reviewCount > 0 ? `<span class="card-stars" title="${reviewCount} review${reviewCount > 1 ? 's' : ''}">${'★'.repeat(Math.min(reviewCount, 5))}${'☆'.repeat(Math.max(0, 5 - Math.min(reviewCount, 5)))} <small>${reviewCount}</small></span>` : '';

    const hasWebsite = !!(item.website || '').trim();

    return `
      <article class="card" onclick="showDetail('${currentCategory}', '${id}')" role="listitem">
        <div class="card-body">
          <h3>${escapeHtml(item.name || 'Unnamed')} ${verified ? '<span class="verified-badge" title="Verified Business">\u2713</span>' : ''} ${hasWebsite ? '<span class="website-badge" title="Has Website">\uD83C\uDF10</span>' : ''}</h3>
          <div class="card-city">${escapeHtml(city)}</div>
          ${phone ? `<a href="tel:${phone}" class="card-phone" onclick="event.stopPropagation();">${escapeHtml(phone)}</a>` : ''}
          ${desc ? `<div class="card-desc">${escapeHtml(desc)}</div>` : ''}
          <div class="card-footer">
            <span class="card-badge ${verified ? 'verified' : 'unverified'}">${verified ? 'Verified' : 'Unverified'}</span>
            ${hasWebsite ? '<span class="card-badge website">Website</span>' : ''}
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

  if (titleEl) titleEl.textContent = `${catInfo.title} - BusinessMen.com.ng Nigeria Directory`;
  if (descEl) descEl.setAttribute('content', catInfo.desc);
  if (ogTitle) ogTitle.setAttribute('content', `${catInfo.title} | BusinessMen.com.ng Nigeria`);
  if (ogDesc) ogDesc.setAttribute('content', catInfo.desc);
  if (twTitle) twTitle.setAttribute('content', `${catInfo.title} | BusinessMen.com.ng Nigeria`);
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
  var item = allData.find(d => d._uid === id);
  if (!item) item = allData.find(d => { var m = d.url && d.url.match(/(\d+)\/$/); return m && m[1] === id; });
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

  const id = item._uid || '';
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
        ${getClaim(id)?.verified ? `<span class="claimed-badge" title="Verified Owner">\u2713 Verified Owner</span>` : `<a href="claim.html?cat=${cat}&id=${id}&name=${encodeURIComponent(businessName)}&phone=${encodeURIComponent(phone)}&city=${encodeURIComponent(city)}" class="btn-secondary" rel="nofollow">Edit This Business</a>`}
      </div>
    </div>
    <div class="detail-toolbar">
      <button class="toolbar-btn" onclick="getDirections('${escapeHtml(businessName)}', '${escapeHtml(city)}', '${escapeHtml(address)}')" title="Get Directions">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
        Directions
      </button>
      ${getWhatsAppNumber(phone) ? `<button class="toolbar-btn toolbar-btn-whatsapp" onclick="whatsappBusiness('${encodeURIComponent(businessName)}', '${phone}')" title="Send WhatsApp Message">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
        WhatsApp
      </button>` : ''}
      <button class="toolbar-btn" onclick="scrollToReviews()" title="Leave a Review">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        Review
      </button>
      <button class="toolbar-btn" onclick="shareBusiness('${escapeHtml(businessName)}', '${cat}', '${id}')" title="Share">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
        Share
      </button>
      <button class="toolbar-btn ${isBookmarked(id) ? 'bookmarked' : ''}" onclick="toggleBookmark('${id}', '${cat}')" title="Bookmark">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="${isBookmarked(id) ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
        ${isBookmarked(id) ? 'Saved' : 'Save'}
      </button>
      <button class="toolbar-btn toolbar-btn-danger" onclick="reportBusiness('${id}')" title="Report">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        Report
      </button>
    </div>

    <div class="detail-body">
      <section class="detail-section">
        <h2>Contact Information</h2>
        ${address ? `<div class="info-row"><span class="label">Address</span><span class="value">${escapeHtml(address)}</span></div>` : ''}
        ${phone ? `<div class="info-row"><span class="label">Phone</span><span class="value"><a href="tel:${phone}" rel="nofollow">${escapeHtml(phone)}</a></span></div>` : ''}
        ${email ? `<div class="info-row"><span class="label">Email</span><span class="value"><a href="mailto:${email}" rel="nofollow">${escapeHtml(email)}</a></span></div>` : ''}
        ${website ? `<div class="info-row"><span class="label">Website</span><span class="value"><a href="${website}" target="_blank" rel="nofollow noopener noreferrer">${escapeHtml(website)}</a></span></div>` : `<div class="info-row"><span class="label">Website</span><span class="value"><span class="no-website-badge-sm">No Website</span> <a href="services.html" class="get-website-link" target="_blank" rel="noopener">Get Website</a></span></div>`}
        ${hours ? `<div class="info-row"><span class="label">Hours</span><span class="value">${escapeHtml(hours)}</span></div>` : ''}
        ${getClaim(id)?.whatsapp ? `<div class="info-row"><span class="label">WhatsApp</span><span class="value"><a href="https://wa.me/${getClaim(id).whatsapp}" target="_blank" rel="noopener">${escapeHtml(getClaim(id).whatsapp)}</a></span></div>` : ''}
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
          <div class="form-group">
            <div class="cf-turnstile" data-sitekey="0x4AAAAAADSQX4TZupvwvbTC"></div>
          </div>
          <button type="submit" class="btn-primary">Submit Review</button>
        </form>
      </section>

      <section class="detail-section">
        <h2>Edit This Listing</h2>
        ${getClaim(id)?.verified
          ? `<div class="claimed-notice"><span class="claimed-badge-lg">\u2713 Verified Owner</span><p style="color:#166534;margin-top:8px;">You have verified ownership and edited this listing.</p></div>`
          : `<p style="color:#64748b;font-size:0.9rem;">Is this your business? Edit your listing on BusinessMen.com.ng to update contact info, add a WhatsApp number, and keep your information current.</p>
        <a href="claim.html?cat=${cat}&id=${id}&name=${encodeURIComponent(businessName)}&phone=${encodeURIComponent(phone)}&city=${encodeURIComponent(city)}" class="btn-primary" style="display:inline-block;margin-top:14px;" rel="nofollow">Edit Now</a>`}
      </section>
    </div>
  `;

  // Firestore override — apply admin-approved listing edits
  if (typeof db !== 'undefined') {
    var possibleIds = [id];
    var numFromUrl = item.url && item.url.match(/(\d+)\/$/)?.[1];
    if (numFromUrl && possibleIds.indexOf(numFromUrl) === -1) possibleIds.push(numFromUrl);
    var nameSlug = (item.name || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    if (numFromUrl && nameSlug) possibleIds.push(nameSlug + '-' + numFromUrl);

    var matched = null;
    for (var pi = 0; pi < possibleIds.length; pi++) {
      for (var li = 0; li < __listingEditsList.length; li++) {
        if (__listingEditsList[li].id === possibleIds[pi]) {
          matched = __listingEditsList[li].data;
          break;
        }
      }
      if (matched) break;
    }

    if (!matched && item.name) {
      var bName = (item.name || '').toLowerCase().trim();
      var bCity = (item.city || '').toLowerCase().trim();
      for (var li = 0; li < __listingEditsList.length; li++) {
        var ed = __listingEditsList[li].data;
        var edName = (ed._businessName || '').toLowerCase().trim();
        var edCity = (ed._businessCity || '').toLowerCase().trim();
        if (edName && edName === bName && edCity && edCity === bCity) {
          matched = ed;
          break;
        }
      }
    }

    if (matched) {
      applyListingEditOverride(container, matched);
    }
  }

  // Firestore override — apply claimed edits on top of static JSON data
  if (id && typeof db !== 'undefined') {
    db.collection('edits').doc(id).get().then(function(doc) {
      if (doc.exists && doc.data().verified === true) {
        applyClaimedEdit(container, doc.data());
      }
    }).catch(function(err) {
      console.warn('Firestore edit fetch failed:', err);
    });
  }
}

function applyClaimedEdit(container, editData) {
  var ed = editData;
  var rows = container.querySelectorAll('.info-row');

  function findRow(labelText) {
    for (var i = 0; i < rows.length; i++) {
      var lbl = rows[i].querySelector('.label');
      if (lbl && lbl.textContent.trim() === labelText) return rows[i];
    }
    return null;
  }

  // Override phone
  if (ed.phone) {
    var r = findRow('Phone');
    if (r) {
      var v = r.querySelector('.value');
      if (v) v.innerHTML = '<a href="tel:' + ed.phone.replace(/"/g,'') + '" rel="nofollow">' + escapeHtml(ed.phone) + '</a>';
    }
  }

  // Override email
  if (ed.email) {
    var r = findRow('Email');
    if (r) {
      var v = r.querySelector('.value');
      if (v) v.innerHTML = '<a href="mailto:' + ed.email.replace(/"/g,'') + '" rel="nofollow">' + escapeHtml(ed.email) + '</a>';
    }
  }

  // Override website
  if (ed.website) {
    var r = findRow('Website');
    if (r) {
      var v = r.querySelector('.value');
      if (v) v.innerHTML = '<a href="' + ed.website.replace(/"/g,'') + '" target="_blank" rel="nofollow noopener noreferrer">' + escapeHtml(ed.website) + '</a>';
    }
  }

  // Add WhatsApp row if claimed has one
  if (ed.whatsapp) {
    var existingWa = findRow('WhatsApp');
    if (!existingWa) {
      var contactSection = container.querySelector('.detail-section');
      if (contactSection) {
        var waRow = document.createElement('div');
        waRow.className = 'info-row';
        waRow.innerHTML = '<span class="label">WhatsApp</span><span class="value"><a href="https://wa.me/' + ed.whatsapp.replace(/"/g,'') + '" target="_blank" rel="noopener">' + escapeHtml(ed.whatsapp) + '</a></span>';
        contactSection.appendChild(waRow);
      }
    }
  }

  // Replace "Edit This Business" button with "Verified Owner" badge
  var detailActions = container.querySelector('.detail-actions');
  if (detailActions) {
    detailActions.innerHTML = '<span class="claimed-badge" title="Verified Owner">\u2713 Verified Owner</span>';
  }

  // Replace bottom "Edit Now" section with verified notice
  var sections = container.querySelectorAll('.detail-section');
  var lastSection = sections[sections.length - 1];
  if (lastSection) {
    var h2 = lastSection.querySelector('h2');
    if (h2 && h2.textContent.trim() === 'Edit This Listing') {
      lastSection.innerHTML = '<h2>Edit This Listing</h2><div class="claimed-notice"><span class="claimed-badge-lg">\u2713 Verified Owner</span><p style="color:#166534;margin-top:8px;">You have verified ownership and edited this listing.</p></div>';
    }
  }
}

function applyListingEditOverride(container, overrideData) {
  var ed = overrideData;
  var rows = container.querySelectorAll('.info-row');
  function findRow(labelText) {
    for (var i = 0; i < rows.length; i++) {
      var lbl = rows[i].querySelector('.label');
      if (lbl && lbl.textContent.trim() === labelText) return rows[i];
    }
    return null;
  }
  if (ed.phone) {
    var r = findRow('Phone');
    if (r) {
      var v = r.querySelector('.value');
      if (v) v.innerHTML = '<a href="tel:' + ed.phone.replace(/"/g,'') + '" rel="nofollow">' + escapeHtml(ed.phone) + '</a>';
    } else {
      var contactSection = container.querySelector('.detail-section');
      if (contactSection) {
        var row = document.createElement('div');
        row.className = 'info-row';
        row.innerHTML = '<span class="label">Phone</span><span class="value"><a href="tel:' + ed.phone.replace(/"/g,'') + '" rel="nofollow">' + escapeHtml(ed.phone) + '</a></span>';
        var firstRow = contactSection.querySelector('.info-row');
        if (firstRow) contactSection.insertBefore(row, firstRow);
        else contactSection.appendChild(row);
      }
    }
  }
  if (ed.whatsapp) {
    var existingWa = findRow('WhatsApp');
    if (!existingWa) {
      var contactSection = container.querySelector('.detail-section');
      if (contactSection) {
        var waRow = document.createElement('div');
        waRow.className = 'info-row';
        waRow.innerHTML = '<span class="label">WhatsApp</span><span class="value"><a href="https://wa.me/' + ed.whatsapp.replace(/"/g,'') + '" target="_blank" rel="noopener">' + escapeHtml(ed.whatsapp) + '</a></span>';
        contactSection.appendChild(waRow);
      }
    }
  }
  if (ed.address) {
    var r = findRow('Address');
    if (r) {
      var v = r.querySelector('.value');
      if (v) v.textContent = escapeHtml(ed.address);
    } else {
      var contactSection = container.querySelector('.detail-section');
      if (contactSection) {
        var addrRow = document.createElement('div');
        addrRow.className = 'info-row';
        addrRow.innerHTML = '<span class="label">Address</span><span class="value">' + escapeHtml(ed.address) + '</span>';
        var firstRow = contactSection.querySelector('.info-row');
        if (firstRow) contactSection.insertBefore(addrRow, firstRow);
        else contactSection.appendChild(addrRow);
      }
    }
  }
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

  if (typeof turnstile !== 'undefined' && turnstile.getResponse().length === 0) {
    alert('Please complete the verification.');
    return;
  }

  const name = document.getElementById('reviewName').value.trim();
  const rating = parseInt(document.getElementById('reviewRating').value);
  const text = document.getElementById('reviewText').value.trim();

  if (!name || !rating || !text) {
    alert('Please fill in all fields and select a rating.');
    return;
  }

  if (/https?:\/\/[^\s]+|www\.[^\s]+/i.test(text) || /https?:\/\/[^\s]+|www\.[^\s]+/i.test(name)) {
    alert('Links are not allowed in reviews. Please remove any URLs.');
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

  if (typeof turnstile !== 'undefined') turnstile.reset();

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

    if (query) {
      const el = document.getElementById('heroQuery');
      if (el) el.value = query;
    }
    if (cityParam) {
      const el = document.getElementById('cityFilter');
      if (el) el.value = cityParam;
    }

    if (query) {
      filteredData = allData.filter(item => {
        const name = (item.name || '').toLowerCase();
        const city = (item.city || '').toLowerCase();
        const desc = (item.description || '').toLowerCase();
        const phone = (item.phone || '');
        const address = (item.address || '').toLowerCase();
        const searchable = `${name} ${city} ${desc} ${phone} ${address}`;
        const terms = query.toLowerCase().split(/\s+/);
        return terms.every(term => searchable.includes(term));
      });
    } else {
      filteredData = [];
    }

    currentPage = 1;
    applyFilters();

    if (loading) loading.style.display = 'none';
    return;
  }

  await loadData(cat);
  if (loading) loading.style.display = 'none';
  showDetail(cat, id);
}

function getCategoryKey(catValue) {
  for (const [key, val] of Object.entries(CATEGORY_MAP)) {
    if (Array.isArray(val) && val.includes(catValue)) return key;
    if (val === catValue) return key;
  }
  return 'general';
}

async function loadFeatured() {
  const grid = document.getElementById('featuredGrid');
  if (!grid) return;
  try {
    const resp = await fetch(CONSOLIDATED_DATA_FILE);
    const allBusinesses = await resp.json();
    
    const categories = ['hotel', 'hospital', 'school', 'schools', 'realestate', 'shopping', 'agriculture', 'automobile', 'construction', 'restaurant', 'oilgas', 'transportation', 'business', 'food', 'general'];
    const results = [];
    
    for (const cat of categories) {
      const catItems = allBusinesses.filter(b => (b.category || '').toLowerCase() === cat);
      if (!catItems.length) continue;
      
      const verifiedItems = catItems.filter(d => d.verified === true);
      const pool = verifiedItems.length > 0 ? verifiedItems : catItems;
      const pick = pool[Math.floor(Math.random() * pool.length)];
      const id = pick.url?.match(/(\d+)\/$/)?.[1] || '';
      if (id) results.push({ cat: getCategoryKey(cat), id, name: pick.name, city: pick.city, phone: pick.phone, description: pick.description, verified: pick.verified });
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
  } catch (e) {
    console.error('Failed to load featured:', e);
  }
}

function submitClaim() {
  const success = document.getElementById('claimSuccess');
  const form = document.querySelector('.claim-form');
  if (form) form.style.display = 'none';
  if (success) success.style.display = 'block';
}

// === CLAIMS ===
function getClaim(businessId) {
  try {
    return JSON.parse(localStorage.getItem('claim_' + businessId)) || null;
  } catch { return null; }
}

function saveClaim(businessId, data) {
  localStorage.setItem('claim_' + businessId, JSON.stringify(data));
}

function verifyClaim(businessId, enteredPhone) {
  const params = new URLSearchParams(window.location.search);
  const listingPhone = params.get('phone') || '';
  const normalizedEntered = enteredPhone.replace(/[\s\-\(\)\+]/g, '').toLowerCase();
  const normalizedListing = listingPhone.replace(/[\s\-\(\)\+]/g, '').toLowerCase();
  const partialMatch = normalizedListing.length > 6 && normalizedListing.includes(normalizedEntered.slice(-7));

  return partialMatch;
}

// === ACTION BUTTONS ===
function getDirections(name, city, address) {
  const q = encodeURIComponent([name, address, city, 'Nigeria'].filter(Boolean).join(', '));
  window.open('https://maps.google.com?q=' + q, '_blank', 'noopener');
}

function getWhatsAppNumber(phone) {
  if (!phone) return '';
  var parts = phone.split(/[,;\/]+/);
  for (var i = 0; i < parts.length; i++) {
    var p = parts[i].trim().replace(/[\s\-\(\)]/g, '');
    if (p.length >= 10 && p.length <= 15 && /^\+?\d+$/.test(p)) {
      var digits = p.replace(/\D/g, '');
      return digits.startsWith('234') ? digits : '234' + digits.replace(/^0+/, '');
    }
  }
  return '';
}

function whatsappBusiness(name, phone) {
  const number = getWhatsAppNumber(phone);
  if (!number) {
    alert('No valid phone number available for WhatsApp.');
    return;
  }
  const text = encodeURIComponent('Hi, I found your business on BusinessMen.com.ng. I would like to know more about your services.');
  window.open('https://wa.me/' + number + '?text=' + text, '_blank', 'noopener');
}

function scrollToReviews() {
  const el = document.querySelector('.reviews-section');
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function shareBusiness(name, cat, id) {
  const url = window.location.origin + '/listing.html?cat=' + cat + '&id=' + id;
  if (navigator.share) {
    navigator.share({ title: name, url: url }).catch(function() {});
  } else {
    navigator.clipboard.writeText(url).then(function() {
      var btn = event.target.closest('.toolbar-btn');
      if (btn) { var orig = btn.innerHTML; btn.innerHTML = 'Copied!'; setTimeout(function() { btn.innerHTML = orig; }, 2000); }
    }).catch(function() {});
  }
}

function isBookmarked(id) {
  try {
    var b = JSON.parse(localStorage.getItem('bookmarks') || '[]');
    return b.indexOf(id) !== -1;
  } catch { return false; }
}

function toggleBookmark(id, cat) {
  var bookmarks = [];
  try { bookmarks = JSON.parse(localStorage.getItem('bookmarks') || '[]'); } catch {}
  var idx = bookmarks.indexOf(id);
  if (idx === -1) {
    bookmarks.push(id);
  } else {
    bookmarks.splice(idx, 1);
  }
  localStorage.setItem('bookmarks', JSON.stringify(bookmarks));
  var params = new URLSearchParams(window.location.search);
  var item = allData.find(function(d) { var m = d.url && d.url.match(/(\d+)\/$/); return m && m[1] === id; });
  if (item) renderDetailView(item, params.get('cat') || 'hotels');
}

function reportBusiness(id) {
  var reason = prompt('Why are you reporting this listing? (e.g., wrong number, closed business, spam)');
  if (!reason || !reason.trim()) return;

  var params = new URLSearchParams(window.location.search);
  var cat = params.get('cat') || currentCategory;
  var item = allData.find(function(d) { var m = d.url && d.url.match(/(\d+)\/$/); return m && m[1] === id; });
  var businessName = item ? item.name : 'Unknown';

  var reportData = {
    businessId: id,
    businessName: businessName,
    category: cat,
    reason: reason.trim(),
    url: window.location.href,
    createdAt: new Date().toISOString(),
    userAgent: navigator.userAgent
  };

  if (typeof db !== 'undefined') {
    db.collection('reports').add(reportData)
      .then(function() {
        alert('Thank you. Your report has been submitted for review.');
      })
      .catch(function(err) {
        console.error('Report submission failed:', err);
        alert('Failed to submit report. Please try again later.');
      });
  } else {
    var reports = [];
    try { reports = JSON.parse(localStorage.getItem('reports') || '[]'); } catch {}
    reports.push(reportData);
    localStorage.setItem('reports', JSON.stringify(reports));
    alert('Thank you. Your report has been submitted for review.');
  }
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
window.getDirections = getDirections;
window.whatsappBusiness = whatsappBusiness;
window.getWhatsAppNumber = getWhatsAppNumber;
window.scrollToReviews = scrollToReviews;
window.shareBusiness = shareBusiness;
window.toggleBookmark = toggleBookmark;
window.reportBusiness = reportBusiness;
