# Open Issues / Things to Verify

## Missing Sections
- [ ] Sections 1402, 1403, 1404 (Chapter 14 - Pre-1972 Sound Recordings) — returned 0 bytes from OLRC. Are they real sections? Were they repealed? Added by Music Modernization Act 2018.

## Text Quality
- [ ] Verify HTML-to-text conversion didn't lose formatting or content in any section
- [ ] Section 115 is 119K chars — verify it extracted correctly (very long section)
- [ ] Check that amendment notes extraction didn't cut off section text prematurely

## Acts List Completeness
- [ ] Two PLs excluded as cross-references (91-375, 99-474) — confirm they truly don't amend Title 17
- [ ] Pre-1976 acts citations (especially 1874, 1879, 1882) sourced from secondary references — verify against Statutes at Large

## Pre-1976 Text
- [ ] Only have full text for 1790 Act so far — all other pre-1976 acts need primary source text
- [ ] Pre-1976 PDF sources should be downloaded and saved to data/source-pdfs/

## Historical Reconstruction
- [ ] Need to reverse-apply all post-1976 amendments to reconstruct section text at each point in time
- [ ] Amendment notes describe changes but may not capture every detail — manual verification needed for complex amendments
