# BusinessMen

Nigeria business directory — a searchable, static directory site hosted on GitHub Pages with 3,091 verified business listings across 11 categories.

## Getting Started

### 1. Run the scraper (optional — data included)

```bash
pip install requests beautifulsoup4
python scraper/scrape_finelib.py
```

### 2. Preview locally

```bash
cd africa-directory
python -m http.server 8000
# Open http://localhost:8000
```

### 3. Deploy to GitHub Pages

```bash
# Create a new repository on GitHub first

# In your local folder:
git init
git add .
git commit -m "Initial commit: Nigeria business directory"
git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git
git push -u origin main
```

Then:
1. Go to your repo on GitHub → **Settings** → **Pages**
2. Under "Source", select **Deploy from a branch**
3. Choose **main** / **root**
4. Click **Save**

Your site will be live at `https://YOUR_USER.github.io/YOUR_REPO/`

## Structure

```
africa-directory/
├── index.html           # Home page with search + listing grid
├── listing.html         # Individual business detail page
├── claim.html           # Claim/add business form
├── css/style.css        # Styles
├── js/app.js            # All JavaScript
└── data/
    ├── nigeria_hotels.json        # 386 hotels
    ├── nigeria_hospitals.json     # 142 hospitals
    ├── nigeria_schools.json       # 294 schools & universities
    ├── nigeria_agriculture.json   # 499 agriculture companies
    ├── nigeria_transportation.json # 299 transport companies
    ├── nigeria_shopping.json      # 550 shopping & retail
    ├── nigeria_business.json      # 300 business services
    ├── nigeria_realestate.json    # 398 real estate companies
    ├── nigeria_oilgas.json        # 63 oil & gas companies
    ├── nigeria_construction.json  # 127 construction companies
    └── nigeria_automobile.json    # 33 automobile companies
```

## Data Fields

| Field | Description |
|---|---|
| name | Business name |
| phone | Contact phone number(s) |
| email | Email address (where available) |
| website | Website URL (where available) |
| address | Full street address |
| city | City/state location |
| description | Business description |
| working_hours | Operating hours |
| products | Product/service listings (where available) |

## Features

- Search by name, city, or keyword
- Filter by city
- Individual listing pages with full details
- "Claim this Business" flow for listing owners
- Mobile responsive
- Zero server costs (GitHub Pages)
