# Open Issues / Things to Verify (In Progress)

## Acts Requiring Complex Manual Reconstruction (in progress)
These acts involve very large sections (§110, §111, §112, §114, §118, §119) that underwent multiple complete chapter-level rewrites (PL 108-419 in 2004 rewrote the entire royalty chapter; PL 111-175 in 2010 rewrote §119). Reconstructing intermediate versions requires access to the full text of each version, which is beyond what can be derived from amendment notes alone.

### Partial fixes applied (CRJ anachronism removal, structural changes)
All six sections had "Copyright Royalty Judges" (a 2004 term) in pre-2004 versions. Fixed to use "Copyright Royalty Tribunal" (pre-1993) or "Librarian of Congress" (1993-2004) as appropriate. §112 subsec (f) addition/removal reconstructed. §110 par. (10)/(11) addition/removal reconstructed. §118 fully reconstructed with correct CRT/LoC/CRJ transitions across all versions.

### Substantive fixes applied
- [x] TEACH Act of 2002 — §110 par. (2) replaced with original pre-TEACH text in v0-v3; TEACH concluding provisions (mediated instructional activities, accreditation, transient storage) removed from pre-TEACH versions
- [x] Satellite Home Viewer Act of 1994 — §111: removed "microwave," insertion, satellite carrier subsec (a)(4), and television market §76.55(e) reference from pre-1994 versions
- [x] Small Webcaster Amendments Act of 2002 — §114: removed webcaster agreement paragraph (f)(4), restored original subsec (g)(2), removed (g)(3)-(4) from pre-2002 versions
- [x] Webcaster Settlement Acts of 2008/2009 — §114: reversed WSA-specific changes (dates, references, "small commercial" terminology) in pre-WSA versions
- [x] Letter of direction (PL 115-264) — §114: removed subsec (g)(5) from all pre-2018 versions
- [x] §119 pre-STELA reconstruction — replaced all pre-2010 versions with authentic pre-STELA text sourced from GovInfo 2009 U.S. Code edition; applied correct date substitutions for 2010 temporary extension acts (PL 111-118, 111-144, 111-151, 111-157)

### Remaining (intermediate version differentiation — in progress)
- [x] §119 post-STELA reconstruction — v17 (PL 111-175) and v18 (PL 113-200) replaced with authentic post-STELA text sourced from GovInfo 2018 U.S. Code edition; 14 paragraphs in (a), subsections through (h), "non-network station" terminology, "paragraphs (4), (5), and (7)" references
- [x] §119 pre-STELA base text — v0-v16 replaced with authentic pre-STELA text from GovInfo 2009 U.S. Code edition; uses "superstation", 16 paragraphs in (a), correct paragraph cross-references
- [x] §119 institutional terminology — CRT (v0, 1988), LoC (v1-v7, 1993-2002), CRJ (v8+, 2004+)
- [x] §119 PL 110-403 (Pro-IP Act 2008) — reversed "sections 509 and 510" → "section 510" and "506 and 509" removals for v0-v10
- [x] §119 PL 111-118 date changes — v0-v11 use "December 31, 2009"; v12-v13 use "February 28, 2010"; v14-v16 use progressive temp extension dates
- [x] §119 PL 103-369 (SHVA 1994) — reversed cents amounts (12→17.5/14, 3→6), date of enactment text, (d)(2) network station definition, (d)(6) FCC service language for v0-v1
- [x] §119 PL 104-39 (DPRA 1995) — removed "and section 114(d)" insertion from v0-v2
- [x] §111 intermediate version differentiation — v0-v3 differentiated: PL 100-667 (a)(4)→(5) renumbering + §119 exclusion; PL 101-318 "recorded the notice" removal; PL 103-198 CRT consultation phrases + d(2)/d(4)(B) text restoration

§119 still has 8 identical adjacent version pairs remaining (v3-v7 share LoC pre-STELA text; v8-v10 share CRJ pre-v11 text; v12-v13; v19-v20). Further differentiation requires identifying specific text changes from PL 105-80, 106-44, 106-113, 107-273, 108-447, 109-303 within the pre-STELA structure.

## Acts With No File Changes (23 total — in progress)

These acts exist as commits in the repo but have empty `files_changed` in acts.json. All 23 should have changed Title 17 text based on OLRC amendment notes.

### Full snapshots ready (10 — in progress, ready to apply) — all expected section files exist in data/act-snapshots/
- [ ] Individuals with Disabilities Education Improvement Act of 2004 (PL 108-446) — §121
- [ ] Intellectual Property Protection and Courts Amendments Act of 2004 (PL 108-482) — §504
- [ ] Temporary Extension Act of 2010 (PL 111-144) — §119
- [ ] Continuing Extension Act of 2010 (PL 111-157) — §119
- [ ] Unlocking Consumer Choice and Wireless Competition Act of 2014 (PL 113-144) — §1201
- [ ] Library of Congress Technical Corrections Act of 2019 (PL 116-94) — 6 sections
- [ ] Protecting Lawful Streaming Act of 2020 (PL 116-260) — 3 sections
- [ ] James M. Inhofe NDAA for FY2023 (PL 117-263) — §105
- [ ] NDAA for FY2025 (PL 118-159) — §105
- [ ] NDAA for FY2026 (PL 119-60) — §105

### Partial snapshots — missing §101 reconstruction (11 — in progress, blocked on §101)
- [ ] Copyright Royalty Tribunal Reform and Miscellaneous Pay Act of 1989 (PL 101-319) — has §701, missing §101, §802
- [ ] Semiconductor International Protection Extension Act of 1991 (PL 102-64) — has §914, missing §101
- [ ] Satellite Home Viewer Act of 1994 (PL 103-369) — has §111/§119, missing §101
- [ ] Digital Theft Deterrence and Copyright Damages Improvement Act of 1999 (PL 106-160) — has §504, missing §101
- [ ] Small Webcaster Amendments Act of 2002 (PL 107-321) — has §114, missing §101
- [ ] Vessel Hull Design Protection Amendments of 2008 (PL 110-434) — has §1301, missing §101
- [ ] Webcaster Settlement Act of 2008 (PL 110-435) — has §114, missing §101
- [ ] Webcaster Settlement Act of 2009 (PL 111-36) — has §114, missing §101
- [ ] Satellite Television Extension Act of 2010 (PL 111-151) — has §119, missing §101
- [ ] Marrakesh Treaty Implementation Act of 2018 (PL 115-261) — has §121, missing §101
- [ ] Artistic Recognition for Talented Students Act of 2022 (PL 117-201) — has §708, missing §101

### Partial snapshots — other missing sections (2 — in progress)
- [ ] TEACH Act of 2002 (PL 107-273) — has 12 sections, missing §802
- [ ] Fairness in Music Licensing Act of 1998 (PL 105-298 Title II) — has §101/§110/§504/§513; NOTE: sections_expected in acts.json is wrong (includes CTEA Title I sections 108, 203, 301, 302, 303, 304 — should only list 101, 110, 504, 513)
