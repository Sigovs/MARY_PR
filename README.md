# Press: Shopify preview and implementation notes

Static HTML/CSS previews of the **Press landing page** (`press.html`) and **all 20 Press article pages** for marymargrill.com.

Open either file in a browser. No build step, no server, relative paths.

```
SHOPIFY_PRESS_PREVIEW/
├── press.html      Landing: publication list + wall of all 20 clippings (blog.press)
├── index.html + article-NN-*.html   20 article pages (index.html = #3 Women's Wear Daily)
├── styles.css      §1 tokens · §2 preview-only chrome · §3 shared · §4 article · §5 landing
├── README.md
└── assets/
    ├── press/                           20 web-ready squares, exactly as supplied, resized to 800×800 (landing)
    ├── press/full/                      The same squares at 2048×2048 for the four article pages
    └── mary-margrill-logo.jpg           Live site logo, as served
```

**The idea:** the publications are the headline. Their names are set like mastheads on the theme's own dark band (`#484545`), and their pages are shown whole on white. Clipping files carry a white canvas and a baked paper shadow, so **a clipping is only ever placed on white, never on the dark band.**

---

## 1. Developer handoff

### 1.1 Templates

Create blog **Press** (handle `press`) and two templates. The existing `news` blog and `article.json` stay untouched.

| File | Section | Contents |
|---|---|---|
| `templates/blog.press.json` | `main-blog-press` | Dark band: "As featured in", **Press**, and one link per publication. Then the clipping wall. Then "Explore the collection" → `/collections/all` |
| `templates/article.press.json` | `main-article-press` | Dark band: Back to Press, the publication name at display size, and the original issue date. Then the clipping (once). Then the article text and source. Then previous / next from the archive |
| `assets/section-press.css` | — | `styles.css` §3 + §4 + §5 |

```json
// templates/article.press.json   (blog.press.json is the same, with "main-blog-press")
{ "sections": { "main": { "type": "main-article-press", "settings": {} } }, "order": ["main"] }
```

- **Assign templates:** set the Press blog to template `press`. Set every press article to **Theme template → `press`**; for bulk, use the Admin API's `template_suffix: "press"`.
- **Header and footer:** these come from the live theme's layout. The preview rebuilds them only for context.
- **The wall is not the theme's `.blog-post-card`**, which crops to 16:9. It is an even grid of equal squares built from the web-ready files **exactly as supplied**: all 2048×2048, with the air already composed around each clipping. Never trim, crop or `object-fit` them; their white margin does the spacing.

#### Landing loop (`main-blog-press`)

```liquid
{%- paginate blog.articles by 50 -%}
  {%- comment -%} Publication list: first article of each title {%- endcomment -%}
  <ul class="press-roll" aria-label="Publications">
    {%- assign seen = '|' -%}
    {%- for a in blog.articles -%}
      {%- assign key = a.title | handleize | prepend: '|' | append: '|' -%}
      {%- unless seen contains key -%}
        <li><a href="#{{ a.handle }}">{{ a.title }}</a></li>
        {%- assign seen = seen | append: key -%}
      {%- endunless -%}
    {%- endfor -%}
  </ul>

  <ul class="press-wall">
    {%- for a in blog.articles -%}
      <li class="press-tile" id="{{ a.handle }}">
        <a class="press-tile__link" href="{{ a.url }}">
          <span class="press-tile__media">
            {{ a.image | image_url: width: 900 | image_tag: widths: '300, 450, 600, 900',
               sizes: '(min-width: 1024px) 25vw, 50vw', loading: 'lazy', alt: '' }}
          </span>
          <div class="press-tile__text">
            <h2 class="press-tile__pub">{{ a.title }}</h2>
            {%- render 'press-meta', article: a -%}
            <span class="press-tile__cue">Read the article</span>
          </div>
        </a>
      </li>
    {%- endfor -%}
  </ul>
{%- endpaginate -%}
```

`snippets/press-meta.liquid` prints `<p class="press-tile__meta">` with `<span>`s for the optional label, `press.feature` and `press.issue_date`, skipping any that are blank. In the preview, tiles without an article page are `<div>`s instead of links; on the live site every tile is a link.

#### Article (`main-article-press`)

Markup mirrors `index.html` one-to-one: `.press-band` (back link, `.press-eyebrow`, `h1.press-display` = `article.title`, `.press-article__issue` = `press.issue_date`) → `figure.press-article__figure` (`article.image`, rendered once, plus the full-size link) → `.press-article__body` (`article.content` + credit) → `nav.press-article__pager` using `blog.previous_article` / `blog.next_article` in the same `.press-tile` markup.

**Verify in the theme:** current Liquid documents `blog.previous_article` / `next_article` as article objects (image, title, metafields), but older themes treated them as URLs. If they come back as URLs, render the pager with links only.

**The clipping appears once.** Editors must not also insert it into the content editor. The page never shows `article.published_at`.

### 1.2 Fields

| Page element | Shopify source | Rule |
|---|---|---|
| Publication name (display H1, publication list, tile title, credit) | `article.title` | Publication only, e.g. "Women's Wear Daily" |
| Clipping | `article.image` | The web-ready 2048×2048 square from `IMAGE no TEXT WEB ready`, **as supplied** (no trimming), on both the landing and the article page; one image per article. Alt text in the image's alt field |
| Article text | `article.content` | Verbatim passage about Mary only |
| **Original issue date** | **`press.issue_date`** (single line text) | **Only when printed on the clipping.** Blank hides it everywhere. Text, not a Date type, because many show only a month. |
| Feature name on the tile | `press.feature` (single line text, optional) | The item's headline as printed, e.g. "18-Karat Baby" |
| Byline in the credit | `press.byline` (single line text, optional) | Only when printed, e.g. "Rachel Paula Abrahamson" (Us Weekly) |
| The item's own headline | `<h2>` at the top of `article.content` | Only when the clipping has one (Us Weekly, Modern Jeweler); styled by §4 |
| Shopify publish date | `article.published_at` | Not displayed. Controls grid order (newest first). |

Create the three metafields under Settings → Custom data → Blog posts; all are optional. The credit line is built from the title, issue date and byline.

### 1.3 Styles to port

Port **`styles.css` §3 (shared), §4 (article) and §5 (landing)**. They use only tokens the theme already defines (`--color-primary/-text/-secondary/-bg`, `--font-heading/-body`, `--heading-weight`, `--heading-spacing`, `--max-width`) and don't override existing theme classes. **Do not port §1 or §2.** §2 also holds a preview-only header breakpoint (960px instead of the live 768px; see §5 below).

| Decision | Value |
|---|---|
| Dark band | `--color-primary` ground, white type; the theme already uses this band (Atelier "In The Studio", footer) |
| Display type | **Cormorant Garamond** 300 (italic 400 for the publication list and item headlines), `--font-display`. The live theme already loads it (300/400/600 + italics) and uses it for its home-page hero, so no new font is added. Used only at ≥ ~30px; display H1 `clamp(2.6rem, 9vw, 7.5rem)` |
| Text voice | **Jost**, the theme's body face, for everything smaller: tile titles (16px / 400), labels, body. Montserrat is not used on press pages |
| Publication list | Cormorant Garamond italic 400, `clamp(1.5rem, 2.2vw, 1.85rem)`; names never break; gold `·` separators travel with the name before them; 45px tap targets |
| Wall | Equal squares: 4 columns / 3 (≤1024) / 2 (≤600); gaps 40×24 (32×12 on mobile). The cue switches to sentence case at ≤600 so it stays on one line |
| Article | Clipping max 960px; text column 640px, Jost **400** 17px / 1.8 (the theme's 300 is too thin for reading) |
| Previous / next | Two columns, clipping 260px tall beside its label; stacked ≤900px |
| Small type | Labels, links and button at **14px minimum** (the theme's 12px eyebrow is below the floor) |
| Wall hover (pointer devices) | A faint champagne ground (`--color-secondary` at 9%) comes up behind the tile, 12px outside it (inside the 24px gap, so nothing reflows). The image layer uses `mix-blend-mode: multiply`, so the white square takes the tint instead of showing as a white box. The clipping lifts 6px, the title takes the gold underline, and "Read the article →" fades in (space reserved). Neighbouring clippings are **not** dimmed. Pure CSS; no theme JS |
| Wall on touch | `(hover: none)`: the cue is always visible |
| Reduced motion | Nothing travels (no lift, arrow or slide); the cue and underline still change state, instantly |

---

## 2. Live theme (verified 2026-11-03)

`Shopify.theme` on https://marymargrill.com/: **MME Theme 5.0.0**, `theme_store_id: null`, role main, id 154079690948, assets under `/cdn/shop/t/13/`. The base theme can't be identified from public data, and it is not Dawn. Theme Liquid files were not available. `/blogs/press` returns 404.

---

## 3. Content verification (all 20 clippings)

Every date was read from the clipping itself. **The filename dates are wrong in several cases** and must not be used.

| # | Publication | Feature (as printed) | Date printed on the clipping | Filename said |
|---|---|---|---|---|
| 1 | People | Chain Reaction | **August 23, 2004** (cover) | 2004 ✓ |
| 3 | Women's Wear Daily | 18-Karat Baby | **April 30, 2007** (masthead) | 2008 / 2009 / 2010 ✗ |
| 4 | Modern Jeweler | Inner Goddess | **June 2007** (masthead) | 2008 / 2009 / 2010 ✗ |
| 6 | FrontDesk | Cool = M2 | **March–April 2008** (folio) | — |
| 10 | Neiman Marcus | The Christmas Book | **2004** | 2004 ✓ |
| 12 | O, The Oprah Magazine | Jewelry with Soul | **August 2006** (folio "96 August 2006", on the scan only) | 2007 / 2008 / 2009 ✗ |
| 13 | Life & Style Weekly | Good Vibes | **March 11, 2013** (cover; legible on the web-ready file, faint but consistent on the low-res scan) | 2014 / 2015 / 2016 ✗ |
| 16 | InStyle | — | **January 2005** (folio "94 January 2005 In Style") | 2006 / 2007 ✗ |
| 18 | The New York Times | Sunday Styles | **October 3, 2004** (masthead) | 2005 / 2006 / 2007 ✗ |

**No date is printed** on 2 Us Weekly, 5 In Touch Weekly, 7 Town & Country, 8 ELLE, 9 Neiman Marcus NM InSite, 11 SHAPE, 14 Us Weekly, 15 Goldengel, 17 WeddingChannel.com, 19 Palm Beach Life or 20 Brides. Their date stays blank; it is not guessed.

**Where the article text comes from.** Every transcript was read from the **original scans in `FROM MARY/`**, not from the web-ready files. Many web-ready files were rebuilt, and some rebuilds changed facts. Only the passage about Mary Margrill / M2 / M² and her jewelry is kept; other brands' items on the same page are left out. Nothing is marked illegible.

| # | Publication | Source scan | Web-ready file vs. the printed page |
|---|---|---|---|
| 1 | People | `1.jpg` | **Rebuilt.** Pendants and chain recoloured to yellow gold (silver/white in print), Jennifer Garner photo replaced, retailer credit cut from the caption |
| 2 | Us Weekly, This Minute | `2.jpg` | **Re-typeset.** Wording matches; byline (Rachel Paula Abrahamson) dropped |
| 3 | Women's Wear Daily | `3.jpg` | Cleaned scan; matches |
| 4 | Modern Jeweler | `4.jpg` | Cleaned scan; matches. Caption prints the collection as "DAAE" |
| 5 | In Touch Weekly | `7.jpg` (+ `5.jpeg`) | **Text altered, do not publish as is:** "M2 Design International's Love necklace … neimanmarcus.com" became "Dwyer International's … www.dwyerintl.com"; "still waiting" became "all waiting"; a photo label changed; an enlarged Love-necklace card was added |
| 6 | FrontDesk | `6.jpg` | **Re-typeset.** One quote reworded ("It's how I live, and I truly believe … into each piece"); cuff recoloured |
| 7 | Town & Country | `Scan 22.jpeg` | Re-typeset; wording, price and phone unchanged. Prints "Deae" |
| 8 | ELLE, Positive ID | `Scan 24.jpeg` | **Rebuilt.** New photo render; other brands' credits altered; producer credit replaced with different names. The M2 sentence itself is unchanged. Which tag is M2's (lapis, or the "Love" tag the arrow points at) is unclear |
| 9 | Neiman Marcus NM InSite | `Scan 25.jpeg` (web printout, page 1 of 23) | Re-typeset; two small wording changes. The Q&A may continue on pages not in the folder |
| 10 | Neiman Marcus, The Christmas Book | `Scan 28.jpeg` | **Rebuilt.** Page rearranged; necklace photo looks regenerated (glossy yellow gold vs pale gold in print) |
| 11 | SHAPE | `Scan 29.jpeg` | Cleaned scan; matches. The giveaway has long expired |
| 12 | O, The Oprah Magazine | `Scan 30.jpeg` | Sidebar re-typeset (one comma became a full stop; the printed comma is kept); folio with the date cropped off |
| 13 | Life & Style Weekly | `Scan 32.jpeg` (low-res) | Bracelet looks regenerated (glossy purple/pink vs dull red-brown in print); wording matches |
| 14 | Us Weekly, Buzzzz-o-Meter | `10.jpg` | Cleaned scan; matches. A large "Us WEEKLY" logo was added |
| 15 | German press, "Goldengel" | `12.jpg` | Cleaned scan; matches. Publication unknown; the "Remember" bracelet sentence (another brand) is left out. The InStyle logo on the live Media page is in neither file |
| 16 | InStyle | `17.jpg` | Cleaned scan; matches |
| 17 | WeddingChannel.com | `18.jpg` | **Rebuilt.** Caption re-typeset (wording matches); necklaces re-rendered on white |
| 18 | The New York Times | `Image 9-30-26 …png` | **A Saks Fifth Avenue advertisement, not editorial.** The scan is itself a composite (masthead pasted on a grid), so the date can't be proven to belong to the ad |
| 19 | Palm Beach Life | `Palm Beach Life Path Post.png` (a designed post, not a scan) | No original page in the folder. **Phone differs:** 561-276-5833 in the post vs 561-276-5283 in the web-ready file; neither can be confirmed |
| 20 | Brides | none | Transcribed from the web-ready file (item 10 only); not verifiable against print |

**For the client to decide before publishing:**

1. **Which images to publish.** The rebuilt files (#1, 2, 5, 6, 8, 10, 13, 17) present the jewelry differently from the printed pages. #5 credits another company. The scans are the documentary record.
2. **#5 In Touch and #8 ELLE** name "M2 Design International" or "M2" but not Mary Margrill.
3. **#18** is an advertisement; consider whether it belongs in "Press".
4. **#15**: name the German publication if known.
5. **Old contact details and prices** in the printed text (phone numbers, retailers, expired giveaway) are kept verbatim. The client can ask for any of them to be removed.
6. **Rights:** reproducing clippings stays subject to the publishers' rights.

---

## 4. QA performed

**Verified** in Chrome (DevTools), static preview, local files:

- Both pages: no horizontal overflow at 1920, 1440, 1024, 768 and 390; all 20 images load; no console messages.
- No functional text under 14px; links at least 44px tall; visible 2px focus outline.
- Wall rows are measured equal height (e.g. 1920: 3×323, 4×286, 5×264, 4×290, 4×274; 390: two per row).
- All 17 publication links resolve to their tiles.
- The article renders the clipping exactly once.

**Not verified:** the Liquid (no theme files); Safari, Firefox and real devices; the theme editor; interaction with `theme.js`.

---

## 5. Live-site findings (separate; not part of this work, nothing on the live site was changed)

**Media page (`/pages/videos`), press grid section** (it looks AI-generated; its class names contain `ai_gen_block`):

- **Width:** the grid is full-bleed. At 1440 it runs from 0 to 1441px, while the page title, header and every other section sit in the theme's 1200px container (left edge 145px). At 1920 the tiles grow to 464px. At 390 the captions touch the screen edges. At 1440 one caption is cut off at the right edge ("MODERN JEWELER: Inner Goddess by …").
- **Images:** 2048px square canvases with `object-fit: cover`. The clippings sit high in their squares, so their visual size and the gap to the caption vary from tile to tile. The images mix versions: some have the transcription baked into the image (People, In Touch, FrontDesk), others don't. Every tile loads a 1000px image with no `srcset`, including on mobile.
- **Captions:**
  - Formats are inconsistent ("PUBLICATION: headline", "MARY MARGRILL …", dates as "AUG. 23, 2004", "2007", "Circa 2005", "10/3/2004").
  - "Courtney" should be "Courteney".
  - "Circa 2005" (In Touch) and "2006" (Us Weekly) are not printed on the clippings.
  - The Numerology dog-tag tile (InStyle, January 2005) names no publication.
- **"InStyle: Gold Angel Bracelet":** the live image (`InStyle_Goldengel_Jewelry_Feature.png`) has an InStyle logo above the German "Goldengel" clipping. The folder version has no masthead, and the logo looks digitally added. The caption is also wrong: the text credits Mary for the necklace ("Kette … von m2designint.com"), while the bracelet ("Armreif") is from inspire company. **Confirm the source before keeping this tile.**
- **Tiles don't link** anywhere.
- **Recommendation:** replace the section with a link to the Press blog, or render it from the Press blog's articles, so the press list is maintained in one place.

**Elsewhere:**

- The desktop header overflows between about 769 and 920px (it needs ≈909px; the switch is at 768px).
- All footer links point to `/`.
- `/blogs/news` shows template copy ("Real people. Real rest.").
- The logo is a 300×24 JPG (a vector version exists in the workspace).
- The Atelier page body text in `#C6AA68` on white is about 2.2:1 contrast.
