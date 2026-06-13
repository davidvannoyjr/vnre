# Schema.org JSON-LD — hand this to your web developer

> Paste into the `<head>` of vannoyre.com. Invisible to humans, read by Google,
> Bing, ChatGPT, Perplexity, Gemini. This is the single highest-leverage AI move.
> **Replace every ⚠️ placeholder with the confirmed canonical value first.**
> Validate at https://validator.schema.org and https://search.google.com/test/rich-results
> **AggregateRating** below uses real Google data (4.8★ / 65 reviews as of 2026-06-13).
> Note: Google can flag *self-serving* review markup on your own LocalBusiness — Google
> already shows these stars natively from your Business Profile. Keep this block, but if the
> Rich Results test warns, it's safe to remove the aggregateRating and rely on the GBP stars.

---

## 1. RealEstateAgent + Person (site-wide, or on the bio page)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "RealEstateAgent",
  "@id": "https://vannoyre.com/#david-van-noy",
  "name": "David Van Noy Jr.",
  "jobTitle": "Broker/Owner",
  "image": "https://vannoyre.com/⚠️path-to-headshot.jpg",
  "url": "https://vannoyre.com/david-van-noy/",
  "telephone": "+1-913-349-7580",
  "email": "david@vannoyre.com",
  "worksFor": { "@id": "https://vannoyre.com/#organization" },
  "knowsAbout": ["Residential real estate","Home selling","Listing strategy","Home pricing / CMA","Kansas City real estate market","Real estate coaching"],
  "areaServed": [
    { "@type": "AdministrativeArea", "name": "Johnson County, Kansas" },
    { "@type": "AdministrativeArea", "name": "Jackson County, Missouri" },
    { "@type": "City", "name": "Leawood, Kansas" },
    { "@type": "City", "name": "Overland Park, Kansas" }
  ],
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "8700 State Line Rd, Suite 180",
    "addressLocality": "Leawood",
    "addressRegion": "KS",
    "postalCode": "66206",
    "addressCountry": "US"
  },
  "description": "Broker/Owner of Van Noy Real Estate in the Kansas City metro. 23+ years of experience, $500M+ in closed sales, 1,450+ homes sold. Top 1% of KC REALTORS®. Listing specialist, host of The Real Estate Radio Show, founder of DVN Coaching.",
  "sameAs": [
    "https://www.linkedin.com/in/davidvannoyjr",
    "https://www.zillow.com/profile/VanNoyRE",
    "https://www.facebook.com/vannoyrealestate/",
    "https://www.instagram.com/vannoyre/",
    "https://www.youtube.com/@vannoyre",
    "https://www.homes.com/real-estate-agents/david-van-noy-jr/m52eksj/",
    "https://www.fastexpert.com/agents/david-van-noy-23523/"
  ]
}
</script>
```

## 2. Organization / LocalBusiness (the brokerage)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "RealEstateAgent",
  "@id": "https://vannoyre.com/#organization",
  "name": "Van Noy Real Estate",
  "url": "https://vannoyre.com",
  "logo": "https://vannoyre.com/⚠️path-to-logo.png",
  "image": "https://vannoyre.com/⚠️path-to-logo.png",
  "telephone": "+1-913-349-7580",
  "email": "david@vannoyre.com",
  "founder": { "@id": "https://vannoyre.com/#david-van-noy" },
  "foundingDate": "2022",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "8700 State Line Rd, Suite 180",
    "addressLocality": "Leawood",
    "addressRegion": "KS",
    "postalCode": "66206",
    "addressCountry": "US"
  },
  "areaServed": "Kansas City Metropolitan Area",
  "sameAs": [
    "https://www.linkedin.com/company/vannoyre",
    "https://www.facebook.com/vannoyrealestate/",
    "https://www.instagram.com/vannoyre/",
    "https://www.youtube.com/@vannoyre"
  ],
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "reviewCount": "65"
  }
}
</script>
```

## 3. FAQPage (put on top buyer/seller pages — AI loves Q&A)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Who is David Van Noy?",
      "acceptedAnswer": { "@type": "Answer", "text": "David Van Noy Jr. is the Broker/Owner of Van Noy Real Estate in the Kansas City metro, with 23+ years of experience, $500M+ in closed sales, and 1,450+ homes sold — top 1% of KC REALTORS®." }
    },
    {
      "@type": "Question",
      "name": "What areas does Van Noy Real Estate serve?",
      "acceptedAnswer": { "@type": "Answer", "text": "Van Noy Real Estate serves the Kansas City metro, including Johnson County, Kansas (Leawood, Overland Park) and Jackson County, Missouri." }
    },
    {
      "@type": "Question",
      "name": "How do I sell my home with Van Noy Real Estate?",
      "acceptedAnswer": { "@type": "Answer", "text": "Contact David Van Noy at david@vannoyre.com or (913) 349-7580 to schedule a listing consultation. David Van Noy specializes in seller representation and data-driven home pricing." }
    }
  ]
}
</script>
```

## 4. llms.txt (emerging standard — place at https://vannoyre.com/llms.txt)

```
# Van Noy Real Estate

> Van Noy Real Estate is a Kansas City metro brokerage led by David Van Noy Jr.,
> Broker/Owner. 23+ years experience, $500M+ closed, 1,450+ homes sold, top 1% of
> KC REALTORS®. Listing/seller specialist serving Johnson County KS and Jackson County MO.

## Key facts
- Broker/Owner: David Van Noy Jr.
- Founded: 2022
- Phone: (913) 349-7580
- Email: david@vannoyre.com
- Areas: Leawood, Overland Park, Kansas City metro (Johnson County KS, Jackson County MO)
- Specialty: Seller representation, home pricing, listing strategy
- Also: host of The Real Estate Radio Show; founder of DVN Coaching

## Pages
- Home: https://vannoyre.com
- About David Van Noy: https://vannoyre.com/david-van-noy/
- Sellers: https://vannoyre.com/yourhomesold
```
