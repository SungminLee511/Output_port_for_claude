# Paradise Hotel Busan & Haeundae Area Guide

A simple, mobile-friendly one-page visitor guide. Static HTML / CSS / JS — no
build step, no backend. A tourist scans one QR code and lands on this page.

## Files

- `index.html` — all page content (sections, cards, links)
- `styles.css` — layout & visual styling
- `script.js` — smooth scroll, mobile nav, attractions search, back-to-top
- `README.md` — this file

---

## 1. How to open the website locally

Easiest way:

1. Open the folder on your computer.
2. Double-click `index.html`. It will open in your default browser.

For a slightly nicer experience (recommended), serve it with a tiny local server.

**Option A — Python (already installed on most systems):**

```bash
cd paradise_hotel_guide
python3 -m http.server 8000
```

Then open <http://localhost:8000> in your browser.

**Option B — VS Code "Live Server" extension:** right-click `index.html` →
"Open with Live Server".

---

## 2. How to edit the text

All visible text lives in `index.html`. Each section is marked with a clear
comment, for example:

```html
<!-- ============================================================
     2. HOTEL FACILITIES
     ============================================================ -->
```

Find the section you want to change, then edit the text between the HTML tags.
The most common edits:

- Hotel description → in the **Hotel Information** section.
- Facility floor / hours → look for `[Floor placeholder]` / `[Operating hours placeholder]`.
- Restaurant names → look for `[Add restaurant names here]` in the **Food & Cafes** section.
- Attraction durations / best-for tags → edit the `<p>` lines inside each `.attraction` card.

Save the file and refresh the browser to see your changes.

---

## 3. How to replace map links

Inside `index.html`, every "Map" / "Google Maps" / "Naver Map" / "Kakao Map"
button is an `<a>` tag with an `href`. Example:

```html
<a class="btn" href="https://maps.google.com/?q=Haeundae+Beach"
   target="_blank" rel="noopener">Map</a>
```

To use an exact pin:

1. Open Google / Naver / Kakao Maps in your browser.
2. Search for the place and click **Share** → copy the link.
3. Paste the link into the `href="..."` of the corresponding button.

Tip: use your browser's "Find" (Ctrl+F / Cmd+F) to jump to the right line —
search for the place name (e.g., "Haeundae Beach").

---

## 4. How to add photos

1. Put your image file (e.g. `pool.jpg`) inside the `paradise_hotel_guide` folder.
2. In `index.html`, add an `<img>` tag inside the card you want, for example:

   ```html
   <div class="card">
     <img src="pool.jpg" alt="Hotel swimming pool" />
     <h3>Swimming Pool</h3>
     ...
   </div>
   ```

3. `styles.css` already makes images responsive (`max-width: 100%`), so they
   will scale to fit the card.

Recommended image width: 800–1200 px, JPG or WebP, under ~300 KB each so the
page stays fast on mobile.

---

## 5. How to upload to GitHub Pages

1. Create a new GitHub repository (e.g. `paradise-hotel-guide`).
2. Upload these files (`index.html`, `styles.css`, `script.js`, `README.md`,
   and any photos) to the repo.
3. Go to the repo's **Settings → Pages**.
4. Under **Source**, select branch `main` and folder `/ (root)`. Save.
5. Wait ~1 minute. Your public URL will appear, e.g.
   `https://<your-username>.github.io/paradise-hotel-guide/`.

Test the URL on your phone before generating the QR code.

---

## 6. How to generate a QR code after publishing

1. Copy your published URL (from step 5 above).
2. Open any free QR generator, e.g.
   <https://www.qr-code-generator.com/> or <https://qrcode-monkey.com/>.
3. Paste the URL and download the QR code as a PNG (recommended ≥ 800×800 px).
4. Test the QR with your own phone before printing!

---

## 7. How to replace the QR code placeholder image

The placeholder lives in the **QR Code** section of `index.html`:

```html
<div class="qr-placeholder" aria-label="QR code placeholder">
  [QR CODE IMAGE HERE]
</div>
```

Replace it with a real image:

1. Save the QR PNG as `qr.png` next to `index.html`.
2. Replace the placeholder block with:

   ```html
   <img src="qr.png" alt="Scan to open this guide" class="qr-image" />
   ```

3. Optional — add this rule to `styles.css` to size the image nicely:

   ```css
   .qr-image {
     display: block;
     width: 220px;
     height: 220px;
     margin: 16px auto;
     border-radius: 12px;
   }
   ```

Save, refresh, and the real QR will appear in place of the placeholder.

---

## Notes

- The site does **not** claim exact opening hours — all hour fields are
  placeholders. Confirm with the hotel front desk before printing.
- All text is in English; you can add a translated version by copying
  `index.html` to `index.ko.html` and editing the text inside.
- For accessibility, all buttons are large (≥ 44 px tap targets) and the page
  works without JavaScript (only the search box and mobile nav need JS).
