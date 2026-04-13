# Congressional Amendment Anomalies and Ambiguities

> **Status: In progress — to be verified.** These anomalies were discovered
> during reconstruction and have not all been independently verified against
> primary sources (Statutes at Large, enrolled bill text). Treat as preliminary
> findings until confirmed.

Discovered during manual reconstruction of version histories. These are cases
where the statutory amendment language is ambiguous, contradictory, or
under-specified — making it impossible to mechanically derive the correct
post-amendment text from the amendment notes alone.

---

## 1. §701 — Contradictory Redesignation in PL 105-304 (1998)

**Amendment notes say (two separate paragraphs):**

> **Subsecs. (b) to (e).** Pub. L. 105-304, §401(b)(1), added subsec. (b) and
> redesignated former subsecs. (b) to (d) as (c) to (e), respectively. Former
> subsec. (e) redesignated (f).

> **Subsec. (f).** Pub. L. 105-304 redesignated subsec. (e) as (f) and
> substituted "III" for "IV" and "5314" for "5315" in first sentence.

**The problem:** The first paragraph says former (b)-(d) become (c)-(e), and
former (e) becomes (f). This implies:
- old (d) [compensation] → new (e)
- old (e) [APA provision, added 1990] → new (f)

But the "Subsec. (f)" paragraph says it "redesignated subsec. (e) as (f) and
substituted 'III' for 'IV' and '5314' for '5315'." The substitutions only make
sense for the **compensation** subsection (which has Executive Schedule level
references), not the APA subsection. This means (f) must be the compensation
subsection.

**The contradiction:** If old (d)[compensation] → (e) per the first paragraph,
and then (e) → (f) per the second paragraph, that's a two-step redesignation
described across two separate amendment note entries. But the first entry says
"Former subsec. (e) redesignated (f)" — which would be the APA provision, not
compensation. You can't have both old (d) and old (e) redesignated to (f).

**Resolution:** The current law has (e) = APA, (f) = compensation. This means
the actual redesignation was:
- old (b)[seal] → (c)
- old (c)[report] → (d)
- old (d)[compensation] → skipped (e), went to (f)
- old (e)[APA] → stayed at (e)

Or, more likely, it was a two-phase operation: first (b)-(d) → (c)-(e), then
the compensation subsec (now at (e)) was further moved to (f), leaving (e) for
the APA provision. The amendment notes describe this as two separate entries
that, read sequentially, appear contradictory.

**Impact:** An automated parser reading "redesignated former subsecs. (b) to (d)
as (c) to (e)" followed by "Former subsec. (e) redesignated (f)" would
incorrectly place the APA provision at (f) and compensation at (e) — the
opposite of the actual result.

---

## 2. §504 — Berne Convention Act (PL 100-568) Amount Changes Not Fully Documented

**Amendment notes say:**

> 1988—Subsec. (c)(1). Pub. L. 100-568, §10(b)(1), substituted "$500" for
> "$250" and "$20,000" for "$10,000".
>
> Subsec. (c)(2). Pub. L. 100-568, §10(b)(2), substituted "$100,000" for
> "$50,000" and "$200" for "$100".

**The issue:** The amendment notes list four separate substitutions across two
subsections. An automated reverser that only handles one substitution per
pattern match (e.g., only reversing "$500" → "$250") would leave the other
amounts unreversed. The existing auto-reverser appears to have only caught the
first substitution in (c)(1), producing a version with "$250" but "$20,000"
(should have been "$10,000").

**Lesson:** When amendment notes list multiple substitutions with "and", all
must be applied atomically. A reverser that processes substitutions one at a
time may leave inconsistent intermediate states.

---

## 3. §105 — Duplicate Subsection Letters in PL 116-92 (2019)

**Amendment notes say:**

> Pub. L. 116-92 designated existing provisions as subsec. (a), inserted
> heading, and added subsec. (b) and **two subsecs. (c)**.

**The issue:** PL 116-92 created two subsections both lettered (c) — one for
"Use by Federal Government" and one for "Definitions." This is explicitly
noted in the amendment history ("two subsecs. (c)"). This is a genuine
drafting error in the enrolled bill that persisted until PL 117-263 (2022)
fixed it by redesignating the definitions subsec. (c) as (d).

**Impact:** Any system tracking subsection letters would need to handle
duplicate letters as a valid (if erroneous) state. The OLRC preserves this
duplication in the amendment notes.

---

## 4. §105 — Identical Amendments from Different Sections of Same PL

**Amendment notes say:**

> Subsec. (d). Pub. L. 117-263, §§3514(3), 6306(1), **made identical
> amendments**, redesignating subsec. (c) relating to definitions as (d).

**The issue:** Two completely separate sections of PL 117-263 (§3514 from
Division C, Title XXXV and §6306 from Division F, Title LXIII) independently
enacted the same amendment. This is a coordination failure in the legislative
drafting process — both the Armed Services Committee and the Intelligence
Committee included provisions amending §105, and neither was aware of the
other.

**Impact:** A version tracker must recognize that "made identical amendments"
means the amendment is applied once, not twice. Two provisions that each say
"redesignate (c) as (d)" don't result in redesignating (d) as (e).

---

## 5. §105 — PL 117-263 Added Two Different Subparagraph (M)s

**Amendment notes say:**

> Subsec. (d)(2)(M). Pub. L. 117-263, §6306(3), added subpar. (M) relating
> to National Intelligence University.
>
> Pub. L. 117-263, §3514(4)(A), added subpar. (M) relating to United States
> Merchant Marine Academy.

**The issue:** Two sections of the same Public Law each added a subparagraph
(M) to the same list — one for National Intelligence University, one for the
Merchant Marine Academy. This is another coordination failure. In practice,
both institutions were added to the list, but the letter assignments had to be
sorted out by the OLRC (one became (M), the other (N)).

**Impact:** Automated amendment application cannot handle two "add subpar. (M)"
instructions — the second would overwrite the first. The OLRC presumably
resolved this editorially.

---

## 6. §121 — PL 108-446 "Added pars. (3) and (4) and struck out former par. (3)"

**Amendment notes say:**

> Pub. L. 108-446, §306(3), added pars. (3) and (4) and struck out former par.
> (3) which read as follows: "'specialized formats' means braille, audio, or
> digital text which is exclusively for use by blind or other persons with
> disabilities."

**The issue:** The amendment simultaneously struck a paragraph and added two new
paragraphs at the same position. The ordering of operations matters:
1. If you strike first, then add: old (1) and (2) remain, new (3) and (4) are
   added. Result: 4 paragraphs.
2. If you add first, then strike: you'd have (1), (2), old (3), new (3), new
   (4) — then strike old (3). Result: same 4 paragraphs, but the intermediate
   state is ambiguous.

What actually happened: The old definitions had (1) authorized entity,
(2) blind or other persons, (3) specialized formats. After the amendment:
(1) authorized entity, (2) blind or other persons, (3) print instructional
materials, (4) specialized formats [new version]. The new par. (4) is also
a "specialized formats" definition — but the amendment notes don't clarify
that the new par. (4) retained the same term as the struck par. (3).

**Impact:** Without knowing that new (4) = "specialized formats" (and what its
new text was), you cannot reconstruct the post-amendment state from the
amendment notes alone. The struck text is quoted but the added text is not.

---

## 7. §708 — Version Convention Ambiguity

**Not a congressional bug, but a data model issue discovered during
reconstruction.**

The manually reconstructed §708 versions (from a previous session) stored each
version's text as the state *after* that PL was applied, while the pipeline
(prepare_build_data.py) expected the state *before*. This caused act-snapshots
to be off by one amendment — e.g., the 2010 STELA snapshot incorrectly
included the 2022 ARTS Act's subsec. (e).

**Lesson:** The version data model comment says "text BEFORE that amendment was
applied" but this convention was not enforced or validated. A consistency check
(comparing version[i] text against version[i-1] text with the documented
amendment applied) would catch this class of error.

---

## 8. §802 — Complete Section Replacement Makes History Unrecoverable

**Amendment notes say:**

> A prior section 802, Pub. L. 94-553, title I, §101, Oct. 19, 1976, 90 Stat.
> 2596; Pub. L. 101-319, §2(a), July 3, 1990... related to membership and
> proceedings of copyright arbitration royalty panels, prior to the general
> amendment of this chapter by Pub. L. 108-419.

**The issue:** PL 108-419 (2004) "generally amended" Chapter 8, completely
replacing §802. The amendment notes for the current §802 only cover post-2004
amendments. The pre-2004 §802 (about the Copyright Royalty Tribunal, later
CARP) had 6+ amendments over 28 years, none of which are recoverable from the
current amendment notes.

**Impact:** For acts like PL 101-319 (1990) that amended the old §802, the
post-amendment text cannot be reconstructed from any data available in the
current OLRC materials. You would need to consult historical Statutes at Large
or the US Code as published at that time (e.g., via HeinOnline or GPO's
historical editions).

---

## 9. §1301 — PL 106-113 "Amended par. (3) generally" Without Quoting New Text

**Amendment notes say:**

> 1999—Subsec. (b)(3). Pub. L. 106-113 amended par. (3) generally. Prior to
> amendment, par. (3) read as follows: "A 'vessel' is a craft, especially one
> larger than a rowboat, designed to navigate on water, but does not include
> any such craft that exceeds 200 feet in length."

**The issue:** The amendment notes quote the *old* text ("Prior to amendment...
read as follows") but do not quote the new text. For a reverser working
backward from current text, this is actually helpful — you know exactly what
to substitute. But for a forward builder (starting from old text and applying
amendments), you'd need to look up the current text to find what the new
paragraph says.

**Observation:** This asymmetry is common in OLRC notes. "Amended... generally"
entries always quote the old text but never the new text, since the new text is
the current law. This works for backward reconstruction but not forward
reconstruction. When multiple "amended generally" notes stack up (as in §119),
you need the full text at each intermediate point.

---

## 10. §110(6) — "Concessionnaire" Typo (1976–present)

The word "concessionnaire" in §110(6) has been misspelled since the original
1976 Copyright Act (PL 94-553). The standard English spelling is
"concessionaire." The OLRC carries a footnote: "So in original. Probably should
be 'concessionaire.'" Despite dozens of amendments to §110 over ~50 years —
including the TEACH Act completely rewriting par. (2) and the Family Movie Act
adding par. (11) — no Congress has ever fixed this one-letter typo in par. (6).

**Impact:** A curiosity rather than a functional problem, but it illustrates
that conforming/technical corrections are easy to overlook when an amendment
targets specific paragraphs and leaves others untouched.

---

## 11. §119 — Section Heading Not Updated by PL 108-447 (2004–2010)

PL 108-447 (2004) expanded §119's scope to cover viewing "in a commercial
establishment," removing the limitation to private home viewing. But the
section heading was never updated from "Secondary transmissions of
superstations and network stations for private home viewing." The OLRC noted:
"So in original. Heading was not amended to conform to amendments by
Pub. L. 108-447."

The heading remained stale for six years until PL 111-175 (STELA, 2010)
completely rewrote the section.

**Impact:** Heading/body mismatches can mislead readers about a section's scope.
This is a common class of drafting error — conforming amendments to headings
are frequently forgotten because headings are not considered part of the
operative statutory text.

---

## 12. §119 — Three Uncorrected Grammatical Errors (1988–2010)

The pre-STELA §119 text contained at least three grammatical errors flagged by
the OLRC with "So in original" footnotes:
- "is" that should be "are" (subject-verb agreement)
- The word "to" that "probably should not appear"
- A missing word "station" at the end of a clause

These persisted through 22 years and dozens of amendments. They were only fixed
when STELA (PL 111-175, 2010) replaced the entire section text.

**Observation:** Congress does not proofread existing text when amending
specific provisions. Grammatical errors in untouched portions of a section can
persist indefinitely. The OLRC flags them but has no authority to correct them.

---

## 13. §119 — Four Stopgap Extensions in Five Months (2009–2010)

Congress passed four separate temporary extension acts to keep §119's satellite
compulsory license alive while the STELA rewrite was still being negotiated:

| Public Law | Enacted | Extended license to |
|---|---|---|
| PL 111-118 | Dec 19, 2009 | Feb 28, 2010 |
| PL 111-144 | Mar 2, 2010 | Mar 28, 2010 |
| PL 111-151 | Mar 26, 2010 | Apr 30, 2010 |
| PL 111-157 | Apr 26, 2010 | May 31, 2010 |
| PL 111-175 (STELA) | May 27, 2010 | *(complete rewrite)* |

Each stopgap only changed expiration dates. The satellite license came within
days of lapsing multiple times. This pattern mirrors the §304 term-extension
saga (1962–1974), where Congress passed twelve serial extensions while working
on what became the 1976 Copyright Act.

**Impact on version reconstruction:** Each stopgap produces a version entry
that differs from the previous only in date strings. When the base text is
wrong (as it was before reconstruction), these date-only versions are
indistinguishable from each other.

---

## 14. §105 — Duplicate Subsection (c) Persisted for Two Years (2019–2022)

*(Extends anomaly #3.)* The duplicate subsection (c) created by PL 116-92
(2019) was not just a momentary drafting error — it persisted as the
authoritative text of §105 for over two years until PL 117-263 (2022) fixed it.
During that period, the U.S. Code officially contained two subsections with the
same letter in the same section. Any legal citation to "§105(c)" during
2020–2022 was inherently ambiguous.

**Observation:** Unlike software, where a duplicate identifier would cause a
compile error, statutory law has no validation step. Drafting errors become
binding law the moment the President signs the bill, and can only be fixed by
another act of Congress.
