let allData = [];
let filteredData = [];
let currentCategory = 'hotels';

const DATA_FILES = {
    hotels: 'data/nigeria_hotels.json',
    hospitals: 'data/nigeria_hospitals.json',
    schools: 'data/nigeria_schools.json',
    agriculture: 'data/nigeria_agriculture.json'
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

    grid.innerHTML = items.map(item => {
        const id = item.url?.match(/(\d+)\/$/)?.[1] || '';
        const phone = item.phone || '';
        const desc = item.description || '';
        const city = item.city || '';
        const email = item.email || '';

        return `
            <div class="card" onclick="location.href='listing.html?cat=${currentCategory}&id=${id}'">
                <div class="card-body">
                    <h3>${item.name || 'Unnamed'}</h3>
                    <div class="card-city">${city}</div>
                    ${phone ? `<a href="tel:${phone}" class="card-phone">${phone}</a>` : ''}
                    ${desc ? `<div class="card-desc">${desc}</div>` : ''}
                    <div class="card-footer">
                        ${email ? `<span class="card-badge">Has Email</span>` : `<span class="card-badge">Phone Only</span>`}
                        <span class="card-claim">Claim this &rarr;</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

async function loadListings(category) {
    await loadData(category);
    filteredData = allData;
    renderGrid(allData);
}

async function loadListingDetail() {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');
    const cat = params.get('cat') || 'hotels';

    if (!id) {
        window.location.href = '/';
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
        container.innerHTML = `<p>Listing not found. <a href="/listing.html?cat=${cat}">Back to ${cat}</a></p>`;
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

    const catLabels = { hotels: 'Hotels', hospitals: 'Hospitals', schools: 'Schools', agriculture: 'Agriculture' };
    const catLabel = catLabels[cat] || 'Listings';

    container.innerHTML = `
        <a href="/listing.html?cat=${cat}" class="back-link">&larr; Back to ${catLabel}</a>
        <div class="detail-header">
            <div>
                <h1>${item.name || 'Unnamed'}</h1>
                ${city ? `<p style="color:#6b7280;margin-top:4px;">${city}</p>` : ''}
            </div>
            <div class="detail-actions">
                <a href="claim.html?business=${encodeURIComponent(item.name)}" class="btn-secondary">Claim this Business</a>
            </div>
        </div>

        <div class="detail-body">
            <div class="detail-section">
                <h2>Contact Information</h2>
                ${address ? `<div class="info-row"><span class="label">Address</span><span class="value">${address}</span></div>` : ''}
                ${phone ? `<div class="info-row"><span class="label">Phone</span><span class="value"><a href="tel:${phone}">${phone}</a></span></div>` : ''}
                ${email ? `<div class="info-row"><span class="label">Email</span><span class="value"><a href="mailto:${email}">${email}</a></span></div>` : ''}
                ${website ? `<div class="info-row"><span class="label">Website</span><span class="value"><a href="${website}" target="_blank">${website}</a></span></div>` : ''}
                ${hours ? `<div class="info-row"><span class="label">Hours</span><span class="value">${hours}</span></div>` : ''}
                ${!address && !phone && !email && !website && !hours ? '<p style="color:#9ca3af;">No contact info available.</p>' : ''}
            </div>

            <div class="detail-section">
                <h2>About</h2>
                ${desc ? `<p>${desc}</p>` : '<p style="color:#9ca3af;">No description available.</p>'}
            </div>

            ${products ? `
            <div class="detail-section">
                <h2>Products & Services</h2>
                <div class="products-box">${products}</div>
            </div>
            ` : ''}

            <div class="detail-section">
                <h2>Claim This Listing</h2>
                <p style="color:#6b7280;font-size:0.9rem;">Is this your business? Claim your page to update information and add services.</p>
                <a href="claim.html?business=${encodeURIComponent(item.name)}" class="btn-primary" style="display:inline-block;margin-top:12px;">Claim Now</a>
            </div>
        </div>
    `;
}

function submitClaim() {
    const success = document.getElementById('claimSuccess');
    const form = document.querySelector('.claim-form');
    if (form) form.style.display = 'none';
    if (success) success.style.display = 'block';
}

document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const business = params.get('business');
    if (business && document.getElementById('claimName')) {
        document.getElementById('claimName').value = business;
    }
});

window.handleSearch = handleSearch;
window.applyFilters = applyFilters;
window.loadListings = loadListings;
window.loadListingDetail = loadListingDetail;
window.submitClaim = submitClaim;
