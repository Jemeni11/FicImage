Add my own attribution just after FicHub's

Adding your own attribution line is generally fine, _if_ it’s transparent, non-intrusive, and easy to disable (opt-out), and it shouldn’t imply ownership of the fic or of FicHub’s work. FicHub already presents itself as an export tool and includes attribution in its outputs, so adding a “processed by FicImage” line in the same area is consistent with that pattern.[1]

## What’s “safe” to do

- Add something like: `Images added with FicImage (version X) — <project URL>` directly after FicHub’s attribution line, keeping it short and factual.
- Make it a config option: default **on**, but clearly documented and easy to set to `false`.
- Keep it to attribution only (no tracking, no ads, no modifying story content beyond that footer/credits area).

## What to avoid (this is what triggers the “sketchy” feeling)

- Don’t add it in multiple places, don’t add it mid-chapter, and don’t add anything that looks like author credit.
- Don’t make it hard to remove; the opt-out is the key “trust signal”.

## Config suggestion

Name it something obvious like `add_ficimage_attribution` (default `true`) and document it next to your other config keys, similar to how you documented `zip_embed_images`.

If you want, paste the exact HTML snippet around FicHub’s attribution in EPUB vs zipped-HTML and the line you want to add; I can suggest the least disruptive insertion point so it doesn’t break formatting.
