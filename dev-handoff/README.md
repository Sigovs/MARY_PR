# Mary Margrill: Press on the Media page (developer handoff)

**What to build:** the approved press design on marymargrill.com.

**Approved design (v4, the version the client signed off):** https://sigovs.github.io/MARY_PR/v4/press.html. Open it next to this README; the Shopify version must match it.

What changes on the live site:

- **Media page (`/pages/videos`):** the current AI press grid (20 images) is replaced by the new press section. Everything else on that page stays exactly as it is: her heading "MEDIA / PRESS and VIDEOS", her three video sections and her "Get in touch" contact section.
- **37 article pages, one per clipping**, at `/blogs/press/<handle>`.

Theme: MME Theme 5.0.0 (live). **Work on a duplicate of the live theme** and publish only after the QA list at the end.

## 1. What's in this folder

```
theme/                          drop into the theme (no existing file is overwritten)
  sections/press-wall.liquid          Media page section: 5 logos, clipping grid (12 per page), page numbers, "More press"
  sections/main-article-press.liquid  article page
  snippets/press-tile.liquid          one clipping tile (grid + article pager)
  snippets/press-icon.liquid          arrow / chevron icons
  assets/section-press.css            all styles, scoped to these sections; uses the theme's own tokens
  templates/article.press.json        article template "press"
  templates/blog.press.json           /blogs/press: the same section with the heading on (fallback / direct link)
paste/media-page-section.json   the section entry for her Media page template (logos pre-filled)
content/
  press_articles.json           the 37 articles, in grid order: title, handle, body HTML, metafields, image, SEO
  press_articles.csv            the same, readable in Excel (UTF-8)
  import_press_articles.py      creates / updates the articles through the Admin API (Python 3, no packages)
images/press/<handle>.jpg       the 37 clipping images (full size, as used in the design)
images/logos/                   the 5 logos (the store already has them, see 3.4)
```

Theme Check (Shopify CLI): 6 files, no offenses.

## 2. How it works

- **One blog "Press" (handle `press`) holds every clipping.** One article per clipping:

  | Article field | Holds | Example |
  |---|---|---|
  | `title` | The publication only | "People" |
  | `image` | The clipping square | — |
  | `body` | The transcribed text | — |

  Two clippings (GQ, In Touch "Goodbye Friends!") have no text. Their article page shows only the image and the source line.
- **Three article metafields,** namespace `press`, all single line text, all optional:

  | Metafield | Shown where | Rule |
  |---|---|---|
  | `press.feature` | Under the publication on the tile | The client's caption for the item, e.g. "StyleWatch: Chain Gang" |
  | `press.issue_date` | On the tile and the article page (gold) | Only when printed on the clipping. It's text ("June 2007", "Circa 2005"), because many show only a month. Blank = no date anywhere |
  | `press.byline` | Added to the source line on the article | Only when printed |

  `article.published_at` is **never shown**. It only sets the order.
- **The publish date sets the order.** The blog lists newest first. The import gives article 1 the newest publish date and each next one a minute older, all in the past (1 Nov 2026). To move a clipping, change its publish date so it falls between its new neighbours.

  Example: People "StyleWatch: Chain Gang" was moved to 6th on page 1 at the client's request; its date sits between People #5 and Us Weekly #7.
- **The grid** shows 12 per page (3 rows of 4; 3 columns ≤1024px, 2 columns ≤600px). With 37 clippings that's 4 pages, and page 4 has 1 clipping.

  Page numbers: "← Previous | 1 2 3 4 | Next →", with the numbers always centred and the current page underlined in gold.
- **The images are web-ready squares** (2048×2048, with the white margin already composed in). Show them **exactly as supplied**: no crop, no `object-fit`, no trimming. Their white margin does the spacing; the client rejected trimmed versions.
- **The five logos** (Vogue, InStyle, O, Harper's BAZAAR, ELLE) are section blocks. Each links automatically to the first article whose title matches its "Publication" text.
  - Vogue and Harper's BAZAAR have no clipping yet, so they show unlinked. They start linking by themselves once such an article exists.
  - Hover dims the logo. There is no underline (the client's choice).
- **"More press"** lists every other publication once, in grid order, each linking to its first article. Seven names show (one line on desktop); "See more" opens the rest (a few lines of inline JS). Without JS the full list shows. A thin gold line under the list closes the press part before her videos.
- **The article page:**
  - Heading: "← Back to Media", the publication (dark, Montserrat 300), the issue date (gold).
  - The clipping, once, with "View full-size clipping".
  - The text, then the source line: "Source: People, March 22, 2004. Text transcribed from the original magazine page."
  - "More from the archive": the previous and next clippings in grid order (`blog.previous_article` = newer, `blog.next_article` = older), plus "All media".
  - The back links go to the Media page (section setting, default `/pages/videos`).
- **Styles:** everything is in `section-press.css` and scoped to `.press-landing` / `.press-article`, so nothing else on the site changes.
  - It uses only the theme's tokens: `--color-primary/-text/-secondary`, `--font-heading/-body`, `--heading-spacing`, `--max-width`. Fallbacks are the live values.
  - Fonts are only the site's own (Montserrat 300 for headings, Jost for the rest).
  - Hover on tiles: a faint champagne ground, a 6px lift, a gold underline on the title, and "Read the article →".
  - Neighbouring tiles are never dimmed (rejected). Touch devices always show the cue. Reduced motion: nothing moves.

## 3. Setup, in order

### 3.1 Theme files
Duplicate the live theme. Add the files from `theme/` (Shopify CLI `theme push`, or Edit code → add each file). They are all new files.

### 3.2 Blog
Online Store → Blog posts → Manage blogs → **Add blog: "Press"**, handle `press`. Set its theme template to **press**. The existing `news` blog and its templates stay untouched.

### 3.3 Articles (37)
Recommended: the import script. It sets title, handle, body, image + alt, the three metafields, SEO title/description, template suffix `press` and the publish date.

1. Settings → Apps and sales channels → Develop apps → create an app with Admin API scopes `read_content`, `write_content`. Install it and copy the Admin API token.
2. Optional: Settings → Custom data → Blog posts: add `press.feature`, `press.issue_date`, `press.byline` (single line text). The script tries to create them as well.
3. Run:
   ```
   cd content
   python import_press_articles.py --dry-run
   set SHOPIFY_ADMIN_TOKEN=shpat_...          (macOS/Linux: export SHOPIFY_ADMIN_TOKEN=...)
   python import_press_articles.py --shop <store>.myshopify.com
   ```

   Re-running updates the existing articles (matched by handle); it never duplicates them. `--only <handle>` imports one article.
4. Images: Shopify fetches them from `image_url` (the public design preview). The same files are in `images/press/` if you'd rather upload them by hand.

If you enter them by hand instead, take every value from `press_articles.csv`. Paste the body as HTML, set the theme template to **press**, and keep the publish dates so the order is right.

### 3.4 Media page
Her Media page is `/pages/videos`, page template `template--21085114106052`. In order, its sections are:

| Section | What it is |
|---|---|
| `main` | Her heading: keep |
| `17863923637cd2315a` | Empty |
| **`17921926842387129d`** | **The AI press grid (20 images, classes `ai-image-row-…`): remove** |
| `1792707170469a96f3` | Empty |
| `story_pmdVX4`, `story_RFMCxL`, `story_EN3EBH` | Her three videos: keep |
| `contact_section_fBxykx` | Her contact form: keep |

1. In the theme editor, open that page template. **Add section → "Press clippings"** directly under her heading, where the AI grid is now.
2. Set **Press blog → Press**.
3. In the five Logo blocks, pick her existing files. These are the ones her home page "As seen in" strip uses:
   - `VOGUE_logo_logotype.png`
   - `InStyle.svg_4cf06552-0402-4d19-a83e-4c964285b9c2.png`
   - `oprah.png`
   - `Harpers_Bazaar_logo_logotype.png`
   - `2560px-Elle-Logo.svg_bfa4e4ce-cda2-4bf4-8827-7d25508baaf2.png`

   Their alt texts on the home page are celebrity names. Here the alt is the publication.
4. Or, instead of steps 1–3, paste `paste/media-page-section.json` into the template JSON: add the `"press"` entry to `sections`, and put `"press"` in `order` where `17921926842387129d` is.
5. Remove the AI grid section `17921926842387129d`. The two empty sections around it can go too.
6. Leave her heading, the three video sections and the contact section untouched.

The "Space above the logos" setting adjusts the gap under her heading (default 24px).

### 3.5 Menu
No change: "MEDIA" keeps pointing to `/pages/videos`. `/blogs/press` also works on its own; it shows the same section with the heading.

## 4. Check before publishing

At 1920, 1440, 1024, 768 and 390px, against the approved preview:

- [ ] Media page: her heading, then the 5 logos in one row (3 + 2 on phones), then 12 clippings.
- [ ] Every "Read the article" in a row sits on one line.
- [ ] The page numbers are centred. `?page=2`…`?page=4` work, and page 4 shows 1 clipping. Previous is hidden on page 1, Next on page 4.
- [ ] "More press": 7 names, then "See more" opens all of them; then the gold line, then her videos and contact form, unchanged.
- [ ] No horizontal scroll at any width.
- [ ] Logos link to the first InStyle / O / ELLE article; Vogue and BAZAAR are shown unlinked.
- [ ] An article: back link, gold date only where one exists, the image uncropped, "View full-size clipping", the text, the source line, previous/next tiles.
- [ ] Check the no-text articles (GQ, In Touch "Goodbye Friends!") and the first and last articles (one neighbour only).
- [ ] Console: no errors. The rest of the site is unchanged (scoped CSS).

## 5. Verified and not verified

**Verified:**
- The Liquid was rendered locally (LiquidJS with mocked Shopify objects and filters, the real 37 articles) into copies of the preview pages, with styles from `section-press.css` only.
- The output was measured in Chrome against the approved preview at 1440 and 390px: Media page 1 and 4, three article pages.
- Every measured position, size, font and colour matched; the rendered press pages have no horizontal scroll.
- "See more" toggles 7 ↔ 24. Theme Check: no offenses.

**Not verified (no store access):**
- **Rendering on the real store and theme.** In particular, `paginate` over `section.settings.blog.articles` on a page template is documented as supported but has not been tested on this theme.

  If it fails, the fallback: point the MEDIA menu item at `/blogs/press`, and add her three video sections and contact section to `templates/blog.press.json` under `main`. Copy them from the page template, same types and settings.
- **The import script against the API** (dry run only).
- **Interaction with the theme's own `theme.js` and CSS,** for example a global rule with higher specificity than the scoped styles.

## 6. Open content items (not blocking the build)

- **17 clippings (the October photos) still have temporary images:** raw photos scaled onto a white square. One of them is on page 1: People "StyleWatch: Chain Gang", 6th.

  The processed squares will come from us. Then replace each image in the admin, or re-run the importer with the updated JSON; it updates by handle.

  Their `image_temporary` is `true` in the JSON/CSV.
- **No Vogue or Harper's BAZAAR clipping yet.** Their logos link automatically once one is added with the matching title.
- **The article text is verbatim from the original pages.** Old phone numbers, prices and retailers are kept as printed.
