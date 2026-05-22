import os
import re

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir("..")

BLOG_DIR = "blog"

RELATED_MAP = {
    "how-to-register-a-business-in-nigeria": [
        ("understanding-nigerian-tax-laws-small-business", "understanding Nigerian tax obligations"),
        ("protect-business-name-trademark-nigeria", "protecting your business name and trademark"),
        ("10-mistakes-starting-business-nigeria", "common mistakes to avoid when starting"),
        ("how-to-write-a-business-plan-nigeria", "writing a solid business plan"),
    ],
    "how-to-write-a-business-plan-nigeria": [
        ("how-to-register-a-business-in-nigeria", "registering your business with the CAC"),
        ("find-investors-startup-nigeria", "finding investors for your startup"),
        ("10-mistakes-starting-business-nigeria", "mistakes to avoid as a new entrepreneur"),
        ("how-to-start-tech-company-nigeria", "starting a tech company"),
    ],
    "10-mistakes-starting-business-nigeria": [
        ("how-to-register-a-business-in-nigeria", "registering your business properly"),
        ("benefits-listing-business-online-directory", "listing your business online"),
        ("market-small-business-budget-nigeria", "marketing on a tight budget"),
        ("understanding-nigerian-tax-laws-small-business", "staying compliant with tax laws"),
    ],
    "understanding-nigerian-tax-laws-small-business": [
        ("how-to-register-a-business-in-nigeria", "registering your business and getting a TIN"),
        ("choose-right-bank-business-account-nigeria", "choosing the right business bank account"),
        ("guide-hiring-managing-employees-nigeria", "hiring employees and managing payroll"),
        ("importance-business-insurance-nigeria", "protecting your business with insurance"),
    ],
    "protect-business-name-trademark-nigeria": [
        ("how-to-register-a-business-in-nigeria", "registering your business name with the CAC"),
        ("build-strong-brand-identity-business", "building a strong brand identity"),
        ("benefits-listing-business-online-directory", "establishing your online presence"),
        ("how-to-write-a-business-plan-nigeria", "planning your business strategy"),
    ],
    "choose-right-bank-business-account-nigeria": [
        ("how-to-register-a-business-in-nigeria", "getting your CAC certificate and TIN"),
        ("understanding-nigerian-tax-laws-small-business", "understanding your tax obligations"),
        ("guide-hiring-managing-employees-nigeria", "setting up payroll for employees"),
        ("how-to-write-a-business-plan-nigeria", "including financial projections in your plan"),
    ],
    "guide-hiring-managing-employees-nigeria": [
        ("understanding-nigerian-tax-laws-small-business", "understanding payroll taxes"),
        ("importance-business-insurance-nigeria", "getting employee insurance coverage"),
        ("how-to-register-a-business-in-nigeria", "registering your business first"),
        ("top-skills-nigerian-entrepreneur-needs", "developing leadership skills"),
    ],
    "importance-business-insurance-nigeria": [
        ("how-to-register-a-business-in-nigeria", "registering your business"),
        ("understanding-nigerian-tax-laws-small-business", "tax deductions for insurance premiums"),
        ("guide-hiring-managing-employees-nigeria", "employee-related insurance requirements"),
        ("10-mistakes-starting-business-nigeria", "avoiding the mistake of operating uninsured"),
    ],
    "transition-side-hustle-full-time-business": [
        ("how-to-write-a-business-plan-nigeria", "writing a transition business plan"),
        ("10-mistakes-starting-business-nigeria", "avoiding common startup mistakes"),
        ("market-small-business-budget-nigeria", "marketing your new full-time business"),
        ("find-investors-startup-nigeria", "finding funding to support your transition"),
    ],
    "understanding-franchising-opportunities-nigeria": [
        ("how-to-register-a-business-in-nigeria", "registering your franchise business"),
        ("how-to-write-a-business-plan-nigeria", "writing a franchise business plan"),
        ("choose-right-bank-business-account-nigeria", "opening a business account for your franchise"),
        ("find-investors-startup-nigeria", "finding investors for your franchise"),
    ],
    "top-10-things-choosing-hotel-nigeria": [
        ("verify-business-before-purchase-nigeria", "verifying a hotel before booking"),
        ("choose-right-real-estate-agent-lagos", "finding property in Lagos"),
        ("find-reliable-logistics-delivery-services-nigeria", "arranging transport to your hotel"),
        ("find-reliable-auto-mechanics-nigeria", "finding auto services if driving"),
    ],
    "find-verified-contractors-construction-project": [
        ("guide-starting-construction-company-nigeria", "understanding the construction industry"),
        ("choose-best-location-retail-store-nigeria", "choosing the right location for your project"),
        ("verify-business-before-purchase-nigeria", "verifying any business before hiring"),
        ("tips-negotiating-better-deals-suppliers", "negotiating better deals with contractors"),
    ],
    "choose-right-real-estate-agent-lagos": [
        ("guide-commercial-real-estate-investment-nigeria", "investing in commercial real estate"),
        ("choose-best-location-retail-store-nigeria", "choosing the best retail location"),
        ("verify-business-before-purchase-nigeria", "verifying the agent's credentials"),
        ("how-to-register-a-business-in-nigeria", "registering your property business"),
    ],
    "questions-ask-before-hiring-moving-company": [
        ("verify-business-before-purchase-nigeria", "verifying any business before hiring"),
        ("find-reliable-logistics-delivery-services-nigeria", "finding reliable logistics services"),
        ("find-verified-contractors-construction-project", "finding verified service providers"),
        ("tips-negotiating-better-deals-suppliers", "negotiating better moving rates"),
    ],
    "verify-business-before-purchase-nigeria": [
        ("how-to-register-a-business-in-nigeria", "checking if a business is registered with CAC"),
        ("find-vet-reliable-suppliers-business", "vetting suppliers for your business"),
        ("find-verified-contractors-construction-project", "finding verified contractors"),
        ("importance-customer-reviews-nigerian-businesses", "checking customer reviews"),
    ],
    "find-reliable-auto-mechanics-nigeria": [
        ("verify-business-before-purchase-nigeria", "verifying any mechanic before hiring"),
        ("find-reliable-logistics-delivery-services-nigeria", "finding reliable transport services"),
        ("choose-best-location-retail-store-nigeria", "finding mechanics near your business"),
        ("importance-customer-reviews-nigerian-businesses", "checking reviews before choosing"),
    ],
    "find-vet-reliable-suppliers-business": [
        ("tips-negotiating-better-deals-suppliers", "negotiating better deals once you find them"),
        ("verify-business-before-purchase-nigeria", "verifying suppliers before committing"),
        ("how-to-start-agriculture-business-nigeria", "finding suppliers for agriculture"),
        ("how-to-start-restaurant-business-nigeria", "finding food suppliers"),
    ],
    "tips-negotiating-better-deals-suppliers": [
        ("find-vet-reliable-suppliers-business", "finding reliable suppliers to negotiate with"),
        ("choose-best-location-retail-store-nigeria", "negotiating rent for your retail space"),
        ("how-to-start-restaurant-business-nigeria", "negotiating with food suppliers"),
        ("market-small-business-budget-nigeria", "saving money through good negotiation"),
    ],
    "choose-best-location-retail-store-nigeria": [
        ("guide-commercial-real-estate-investment-nigeria", "understanding commercial real estate"),
        ("choose-right-real-estate-agent-lagos", "finding a good real estate agent"),
        ("market-small-business-budget-nigeria", "marketing your new retail store"),
        ("how-to-start-fashion-clothing-business-nigeria", "starting a fashion retail business"),
    ],
    "find-reliable-logistics-delivery-services-nigeria": [
        ("how-to-start-logistics-delivery-business-nigeria", "understanding the logistics industry"),
        ("verify-business-before-purchase-nigeria", "verifying logistics companies"),
        ("questions-ask-before-hiring-moving-company", "hiring moving services"),
        ("role-technology-nigerian-business-growth", "using technology to track deliveries"),
    ],
    "complete-guide-opening-school-nigeria": [
        ("how-to-register-a-business-in-nigeria", "registering your school business"),
        ("guide-hiring-managing-employees-nigeria", "hiring teachers and staff"),
        ("choose-best-location-retail-store-nigeria", "choosing the right school location"),
        ("understanding-nigerian-tax-laws-small-business", "understanding tax obligations for schools"),
    ],
    "how-to-start-restaurant-business-nigeria": [
        ("how-to-register-a-business-in-nigeria", "registering your restaurant"),
        ("find-vet-reliable-suppliers-business", "finding reliable food suppliers"),
        ("choose-best-location-retail-store-nigeria", "choosing the right restaurant location"),
        ("how-to-start-catering-business-nigeria", "expanding into catering"),
    ],
    "how-to-start-agriculture-business-nigeria": [
        ("how-to-register-a-business-in-nigeria", "registering your agriculture business"),
        ("find-vet-reliable-suppliers-business", "finding farming supplies and equipment"),
        ("guide-starting-transportation-business-nigeria", "transporting your produce"),
        ("understanding-nigerian-tax-laws-small-business", "agricultural tax incentives"),
    ],
    "how-to-start-logistics-delivery-business-nigeria": [
        ("how-to-register-a-business-in-nigeria", "registering your logistics company"),
        ("guide-starting-transportation-business-nigeria", "understanding the transport sector"),
        ("role-technology-nigerian-business-growth", "using technology for fleet management"),
        ("find-investors-startup-nigeria", "finding investors for your logistics startup"),
    ],
    "guide-commercial-real-estate-investment-nigeria": [
        ("choose-right-real-estate-agent-lagos", "finding the right agent"),
        ("choose-best-location-retail-store-nigeria", "evaluating retail locations"),
        ("how-to-register-a-business-in-nigeria", "registering your real estate business"),
        ("find-investors-startup-nigeria", "finding investment partners"),
    ],
    "how-to-start-cleaning-services-business-nigeria": [
        ("how-to-register-a-business-in-nigeria", "registering your cleaning business"),
        ("market-small-business-budget-nigeria", "marketing your cleaning services"),
        ("guide-hiring-managing-employees-nigeria", "hiring and training cleaners"),
        ("importance-business-insurance-nigeria", "getting liability insurance"),
    ],
    "how-to-start-event-planning-business-nigeria": [
        ("how-to-register-a-business-in-nigeria", "registering your event planning business"),
        ("market-small-business-budget-nigeria", "marketing your event services"),
        ("build-strong-brand-identity-business", "building your event brand"),
        ("role-social-media-growing-nigerian-business", "using social media to showcase events"),
    ],
    "complete-guide-opening-pharmacy-nigeria": [
        ("how-to-register-a-business-in-nigeria", "registering your pharmacy"),
        ("understanding-nigerian-tax-laws-small-business", "pharmacy tax obligations"),
        ("guide-hiring-managing-employees-nigeria", "hiring licensed pharmacists"),
        ("importance-business-insurance-nigeria", "pharmacy insurance requirements"),
    ],
    "how-to-start-security-services-company-nigeria": [
        ("how-to-register-a-business-in-nigeria", "registering your security company"),
        ("guide-hiring-managing-employees-nigeria", "hiring and vetting security personnel"),
        ("importance-business-insurance-nigeria", "liability insurance for security firms"),
        ("understanding-nigerian-tax-laws-small-business", "tax obligations for security companies"),
    ],
    "guide-starting-transportation-business-nigeria": [
        ("how-to-register-a-business-in-nigeria", "registering your transport business"),
        ("how-to-start-logistics-delivery-business-nigeria", "expanding into logistics"),
        ("importance-business-insurance-nigeria", "vehicle and liability insurance"),
        ("find-investors-startup-nigeria", "finding investors for fleet expansion"),
    ],
    "how-to-start-fashion-clothing-business-nigeria": [
        ("how-to-register-a-business-in-nigeria", "registering your fashion brand"),
        ("choose-best-location-retail-store-nigeria", "choosing the right shop location"),
        ("role-social-media-growing-nigerian-business", "marketing fashion on social media"),
        ("build-strong-brand-identity-business", "building a memorable fashion brand"),
    ],
    "how-to-start-tech-company-nigeria": [
        ("how-to-register-a-business-in-nigeria", "registering your tech company"),
        ("find-investors-startup-nigeria", "finding tech investors in Nigeria"),
        ("build-professional-website-business", "building your company website"),
        ("role-technology-nigerian-business-growth", "leveraging technology for growth"),
    ],
    "how-to-start-catering-business-nigeria": [
        ("how-to-start-restaurant-business-nigeria", "understanding the food industry"),
        ("how-to-register-a-business-in-nigeria", "registering your catering business"),
        ("find-vet-reliable-suppliers-business", "finding reliable food suppliers"),
        ("market-small-business-budget-nigeria", "marketing your catering services"),
    ],
    "understanding-ecommerce-regulations-nigeria": [
        ("how-to-register-a-business-in-nigeria", "registering your e-commerce business"),
        ("build-professional-website-business", "building your online store"),
        ("role-technology-nigerian-business-growth", "technology tools for e-commerce"),
        ("how-to-start-tech-company-nigeria", "building a tech platform"),
    ],
    "guide-starting-construction-company-nigeria": [
        ("how-to-register-a-business-in-nigeria", "registering your construction company"),
        ("importance-business-insurance-nigeria", "construction insurance requirements"),
        ("guide-hiring-managing-employees-nigeria", "hiring skilled construction workers"),
        ("find-investors-startup-nigeria", "finding investors for construction projects"),
    ],
    "benefits-listing-business-online-directory": [
        ("why-every-nigerian-business-needs-online-presence", "why online presence matters"),
        ("build-professional-website-business", "building a professional website"),
        ("market-small-business-budget-nigeria", "affordable marketing strategies"),
        ("importance-customer-reviews-nigerian-businesses", "the power of customer reviews"),
    ],
    "market-small-business-budget-nigeria": [
        ("benefits-listing-business-online-directory", "listing on online directories for free"),
        ("role-social-media-growing-nigerian-business", "using social media for marketing"),
        ("build-strong-brand-identity-business", "building your brand on a budget"),
        ("encourage-customers-leave-reviews-business", "getting reviews as free marketing"),
    ],
    "role-social-media-growing-nigerian-business": [
        ("market-small-business-budget-nigeria", "social media as a low-cost marketing tool"),
        ("build-strong-brand-identity-business", "building your brand on social media"),
        ("benefits-listing-business-online-directory", "combining directory listings with social media"),
        ("encourage-customers-leave-reviews-business", "encouraging reviews through social media"),
    ],
    "build-strong-brand-identity-business": [
        ("market-small-business-budget-nigeria", "branding on a budget"),
        ("build-professional-website-business", "your website as a brand asset"),
        ("protect-business-name-trademark-nigeria", "protecting your brand legally"),
        ("role-social-media-growing-nigerian-business", "amplifying your brand on social media"),
    ],
    "top-skills-nigerian-entrepreneur-needs": [
        ("10-mistakes-starting-business-nigeria", "learning from common mistakes"),
        ("how-to-write-a-business-plan-nigeria", "planning as a core skill"),
        ("benefits-networking-small-business-owners", "networking as a business skill"),
        ("use-customer-feedback-improve-business", "listening to customers"),
    ],
    "benefits-networking-small-business-owners": [
        ("top-skills-nigerian-entrepreneur-needs", "networking as an essential skill"),
        ("find-investors-startup-nigeria", "finding investors through networking"),
        ("market-small-business-budget-nigeria", "networking as free marketing"),
        ("how-to-start-tech-company-nigeria", "networking in the tech community"),
    ],
    "find-investors-startup-nigeria": [
        ("how-to-write-a-business-plan-nigeria", "writing a plan that attracts investors"),
        ("benefits-networking-small-business-owners", "networking to find investors"),
        ("how-to-start-tech-company-nigeria", "investing in tech startups"),
        ("transition-side-hustle-full-time-business", "funding your transition"),
    ],
    "role-technology-nigerian-business-growth": [
        ("build-professional-website-business", "your website as a technology foundation"),
        ("how-to-start-tech-company-nigeria", "building a tech business"),
        ("understanding-ecommerce-regulations-nigeria", "e-commerce technology"),
        ("market-small-business-budget-nigeria", "affordable technology tools"),
    ],
    "build-professional-website-business": [
        ("benefits-listing-business-online-directory", "combining your website with directory listings"),
        ("role-technology-nigerian-business-growth", "technology tools for your website"),
        ("build-strong-brand-identity-business", "your website as your brand"),
        ("why-every-nigerian-business-needs-online-presence", "why a website is essential"),
    ],
    "use-customer-feedback-improve-business": [
        ("importance-customer-reviews-nigerian-businesses", "the value of customer feedback"),
        ("best-practices-managing-online-business-reviews", "managing feedback professionally"),
        ("how-to-respond-negative-reviews-professionally", "handling negative feedback"),
        ("top-skills-nigerian-entrepreneur-needs", "listening as a business skill"),
    ],
    "importance-customer-reviews-nigerian-businesses": [
        ("best-practices-managing-online-business-reviews", "managing your reviews effectively"),
        ("encourage-customers-leave-reviews-business", "getting more reviews"),
        ("how-to-respond-negative-reviews-professionally", "responding to negative reviews"),
        ("benefits-listing-business-online-directory", "reviews on directory listings"),
    ],
    "best-practices-managing-online-business-reviews": [
        ("importance-customer-reviews-nigerian-businesses", "why reviews matter"),
        ("how-to-respond-negative-reviews-professionally", "responding to negative reviews"),
        ("encourage-customers-leave-reviews-business", "encouraging positive reviews"),
        ("use-customer-feedback-improve-business", "using reviews to improve"),
    ],
    "why-every-nigerian-business-needs-online-presence": [
        ("benefits-listing-business-online-directory", "starting with a directory listing"),
        ("build-professional-website-business", "building your own website"),
        ("role-social-media-growing-nigerian-business", "using social media for presence"),
        ("importance-customer-reviews-nigerian-businesses", "reviews as part of your presence"),
    ],
    "how-to-respond-negative-reviews-professionally": [
        ("best-practices-managing-online-business-reviews", "overall review management"),
        ("importance-customer-reviews-nigerian-businesses", "why every review matters"),
        ("use-customer-feedback-improve-business", "turning feedback into improvement"),
        ("encourage-customers-leave-reviews-business", "balancing negative with positive reviews"),
    ],
    "encourage-customers-leave-reviews-business": [
        ("importance-customer-reviews-nigerian-businesses", "why you need more reviews"),
        ("best-practices-managing-online-business-reviews", "managing the reviews you get"),
        ("how-to-respond-negative-reviews-professionally", "responding to all reviews"),
        ("market-small-business-budget-nigeria", "reviews as free marketing"),
    ],
}

def add_interlinks(content, slug):
    if slug not in RELATED_MAP:
        return content

    related = RELATED_MAP[slug]
    links_added = 0

    for related_slug, anchor_text in related:
        if links_added >= 3:
            break

        link_html = f'<a href="{related_slug}.html">{anchor_text}</a>'

        pattern = rf'(<p>[^<]*?)({re.escape(anchor_text.split()[0])})([^<]*?</p>)'
        match = re.search(pattern, content, re.IGNORECASE)

        if match:
            full_match = match.group(0)
            if f'{related_slug}.html' in full_match:
                continue

            before = match.group(1)
            word = match.group(2)
            after = match.group(3)

            replacement = f'{before}<a href="{related_slug}.html">{word}'
            if after.strip().startswith(' '):
                replacement += after.lstrip()
            else:
                replacement += after

            content = content.replace(full_match, replacement, 1)
            links_added += 1

    if links_added < 3:
        for related_slug, anchor_text in related:
            if links_added >= 3:
                break

            link_html = f'<a href="{related_slug}.html">{anchor_text}</a>'

            paragraphs = content.split('</p>')
            for i, p in enumerate(paragraphs):
                if f'{related_slug}.html' in p:
                    continue
                if '<a href=' in p and p.count('<a href=') >= 2:
                    continue
                if '<h' in p:
                    continue
                if len(p) > 100:
                    words = p.split()
                    mid = len(words) // 2
                    insertion_point = ' '.join(words[:mid])
                    rest = ' '.join(words[mid:])
                    paragraphs[i] = f'{insertion_point} <a href="{related_slug}.html">{anchor_text}</a>{rest}'
                    content = '</p>'.join(paragraphs)
                    links_added += 1
                    break

    return content

def update_related_section(content, slug):
    if slug not in RELATED_MAP:
        return content

    related = RELATED_MAP[slug]
    related_html = ""

    for related_slug, anchor_text in related[:4]:
        related_html += f'''
            <div class="post-related-card">
              <a href="{related_slug}.html">{anchor_text.title()}</a>
            </div>'''

    content = re.sub(
        r'(<div class="post-related-grid">).*?(</div>\s*</div>\s*</article>)',
        f'\\1{related_html}\\2',
        content,
        flags=re.DOTALL
    )

    return content

print("Processing blog posts...")
updated_count = 0

for filename in os.listdir(BLOG_DIR):
    if not filename.endswith('.html') or filename == 'index.html':
        continue

    slug = filename.replace('.html', '')
    filepath = os.path.join(BLOG_DIR, filename)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    content = add_interlinks(content, slug)
    content = update_related_section(content, slug)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        updated_count += 1
        print(f"  Updated: {filename}")

print(f"\nDone. Updated {updated_count} blog posts with interlinks.")
