// US Business Directory Scraper (BBB.org)
// Usage: node scraper/scrape-bbb.js "plumber" "New York, NY" 50
// First run: npm install puppeteer

const puppeteer = require('puppeteer');

const keyword = process.argv[2] || 'plumber';
const location = process.argv[3] || 'New York, NY';
const maxResults = parseInt(process.argv[4]) || 50;

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36');

  const searchUrl = `https://www.bbb.org/search?find_text=${encodeURIComponent(keyword)}&find_loc=${encodeURIComponent(location)}`;
  console.log(`Navigating to: ${searchUrl}`);
  await page.goto(searchUrl, { waitUntil: 'networkidle2', timeout: 30000 });

  // Wait for results to load
  await page.waitForSelector('.search-result-card', { timeout: 10000 }).catch(() => {});

  let results = [];
  let pageNum = 1;

  while (results.length < maxResults) {
    console.log(`Scraping page ${pageNum}...`);

    const pageData = await page.evaluate(() => {
      const cards = document.querySelectorAll('.search-result-card');
      return Array.from(cards).slice(0, 20).map(card => {
        const nameEl = card.querySelector('.search-result-title a, .result-name a, h3 a');
        const phoneEl = card.querySelector('[data-testid="phone"], .phone, .result-phone');
        const addressEl = card.querySelector('[data-testid="address"], .address, .result-address');
        const websiteEl = card.querySelector('[data-testid="website"], .website, .result-website a');
        const ratingEl = card.querySelector('.rating, .result-rating');
        const categoryEl = card.querySelector('.category, .result-category');
        return {
          name: nameEl ? nameEl.textContent.trim() : '',
          phone: phoneEl ? phoneEl.textContent.trim() : '',
          address: addressEl ? addressEl.textContent.trim() : '',
          website: websiteEl ? (websiteEl.href || websiteEl.textContent.trim()) : '',
          rating: ratingEl ? ratingEl.textContent.trim() : '',
          category: categoryEl ? categoryEl.textContent.trim() : keyword,
          source: 'bbb.org',
          verified: true
        };
      });
    });

    results = results.concat(pageData);
    console.log(`  Got ${pageData.length} results (total: ${results.length})`);

    if (pageData.length === 0 || results.length >= maxResults) break;

    // Try next page
    const nextBtn = await page.$('a[rel="next"], .pagination .next, button:has-text("Next")');
    if (!nextBtn) break;
    await nextBtn.click();
    await page.waitForTimeout(3000);
    pageNum++;
  }

  console.log(`\nDone. Total: ${results.length} businesses`);
  console.log(JSON.stringify(results.slice(0, 5), null, 2));
  console.log(`\nFull data (${results.length} records) written to bbb_results.json`);
  require('fs').writeFileSync('bbb_results.json', JSON.stringify(results, null, 2));

  await browser.close();
})();
