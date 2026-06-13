# The Real Estate Radio Show — page copy + schema

> You're the long-time host — that's a major authority signal AI barely sees because it has
> no home. Give it a page on vannoyre.com (/radio) with episode entries + PodcastEpisode
> schema. Transcripts are gold: AI reads them and cites you as the source.

---

## Hero
**Headline:** The Real Estate Radio Show — with David Van Noy
**Subhead:** Straight talk on selling, buying, and the Kansas City market — from a broker who's closed $500M+ and sold 1,450+ homes.
**CTA:** Listen to the latest episode →

## About the show
The Real Estate Radio Show is hosted by David Van Noy Jr., Broker/Owner of Van Noy Real Estate. For years David has broken down the real estate market, pricing, marketing, and the moves that actually sell homes — no hype, just what works. He also speaks on lead generation, time management, and goal setting.

## Episode list (template — fill per episode)
Each episode gets: title · date · 2–3 sentence summary · audio/video embed · **full transcript**.

> **[Episode title]** — [date]
> [2–3 sentence summary in DVN voice. Lead with the takeaway.]
> [Embed] · [Transcript ↓]

## Why transcripts matter
AI engines read transcript text, not audio. Every episode transcript is a page of citable, keyword-rich authority on the KC market in your voice. Caption/transcribe every episode and YouTube video.

---

## Schema (JSON-LD — series + per episode)

**PodcastSeries (page level):**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "PodcastSeries",
  "name": "The Real Estate Radio Show",
  "url": "https://vannoyre.com/radio",
  "author": { "@type": "Person", "@id": "https://vannoyre.com/#david-van-noy", "name": "David Van Noy Jr." },
  "description": "Real estate talk show hosted by David Van Noy Jr., Broker/Owner of Van Noy Real Estate, covering home selling, buying, pricing, and the Kansas City market."
}
</script>
```

**PodcastEpisode (per episode):**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "PodcastEpisode",
  "name": "[Episode title]",
  "datePublished": "[YYYY-MM-DD]",
  "partOfSeries": { "@type": "PodcastSeries", "name": "The Real Estate Radio Show" },
  "author": { "@type": "Person", "name": "David Van Noy Jr." },
  "description": "[Episode summary]",
  "transcript": "[Full transcript text or URL]"
}
</script>
```

> Need: confirm where episodes live (radio station archive? podcast feed? YouTube?) so I can wire the embeds and pull transcripts. Send me the source and I'll structure the first batch.
