# Press preview v2 (client update, Nov 6 2026)

v2 applies the client's email of Nov 6. v1 (one folder up) is unchanged for comparison. The templates, fields and Liquid in `../README.md` still apply.

Open `press.html`. Rebuild from this folder:

```
python ../../_press_build/build_v2.py . ../../_press_build/press_data_v2.json
```

Data lives in `_press_build/press_data_v2.json`. Article text comes from `_press_build/transcripts/`, read from the original scans. Don't hand-edit the HTML.

## What changed, by the client's points

| # | Client asked | v2 |
|---|---|---|
| 1 | Only the fonts her website uses | Cormorant Garamond removed. Display text is Montserrat 300 (the theme heading face); everything else is Jost |
| 2 | Her five publications first, then the rest, no duplicates; logos clickable | The band shows her "As seen in" logos (her own files from the home page, styled as the theme does: white, 36px, 0.7). Under them, every other publication appears once. Logos and names link to the first article of each publication. The wall follows the same order |
| 3 | Use what is live on her site (edited cuff colour, wording and dates) | All 20 images are her current live Media images, used as supplied. Tile captions use her live wording and dates |

**Changed from her live captions, where they contradict the printed page:**
- "Courtney" → "Courteney".
- Goldengel: "Gold Angel Bracelet" → "Goldengel". The text credits Mary for the necklace (Kette); the bracelet is inspire company.
- Brides: "and diamond rings" dropped. The rings on the page are other brands.

**Dates added from the scans** where her captions have none: O (August 2006), Life & Style (March 11, 2013), Modern Jeweler (June 2007, from her "2007").

**Kept as the client states, but not printed on the page:** In Touch "Circa 2005", Us Weekly Buzz "2006", Goldengel as "InStyle".


**Article text follows her edits** where her live images carry typed text under the clipping (5 images; InStyle matches the scan exactly):
- **People:** the retailer and phone ("Jennifer Kaufman, 310-854-1058") are dropped.
- **In Touch:** "Penélope" takes the accent, and "neimanmarcus.com" is dropped. ⚠️ Her image still shows the rebuilt clipping text "Dwyer International … www.dwyerintl.com" above her own typed text.
- **FrontDesk:** "14- and 18kt"; the availability line and the photo caption are dropped.
- **Us Weekly Buzz:** only the World Peace Now Necklace item; the Buzz-o-Meter intro is dropped. ⚠️ Her text has "m2designinc.com", while the printed page (also visible in her image) has "m2designint.com". Kept as printed; probably a typo.

## October photos (n = 21–37), page 2

The 17 photos from `2_2 OCTOBER 2026 updates` are laid out on `press-2.html`. Page 1 ends with a "More press" button (Shopify blog pagination, 20 per page). Each photo has its own article page, with text from `_press_build/transcripts_v2/`.

**Images are TEMPORARY:** the whole raw phone photo, only scaled onto a white 2048 square. When the processed squares are ready:
1. Put them in `IMAGE no TEXT WEB ready 2/` as `IMG_04NN.png` or `.jpg`.
2. Run, from the project root: `python _press_build/october_images.py`, then `python _press_build/october_rows.py` (from `_press_build/`).
3. Rebuild v2.

**Text notes:**
- **No printed text about Mary:** GQ (#22) and In Touch "Goodbye Friends!" (#25). The piece is marked only by arrows pasted onto the page, so the text block is hidden.
- **Printed text doesn't name her:** People "50 Most Beautiful" (#28) and the newspaper clippings (#29). Only the page captions are shown.
- **Uncertain readings:**
  - #21 People: the price and the phone's last digit.
  - #27 Us Weekly: the date is blurred, probably November 28, 2005; it is left blank.
  - #31 Shop Etc.: the right edge is cut.
  - #33 Record-Review: a halftone copy; the price and some words are uncertain, and the paper prints "Magrill".
- **Dates that may belong to the cover rather than the item** (item pasted onto a cover): #30 and #37 Modern Jeweler, and #32 Gotham.
- **#34 W** is her own composite. "April 2004" appears only in her typed caption.

## Still open

- **Vogue and Harper's BAZAAR**: no clippings in any folder (not among the 20 or the 17 October photos), so their logos are shown but not linked. They link automatically once a clipping is added.
- **Text in the image plus text below it**: several of her live images now carry the typed text (People, In Touch, FrontDesk, Us Weekly Buzz, InStyle), and the HTML text below repeats it. The HTML text stays for search; how prominent it should be is a design decision to settle.
- **Points 4–6 are questions, not built yet**:
  - SEO/AEO plan.
  - Final image processing of the 17 October photos (see above).
