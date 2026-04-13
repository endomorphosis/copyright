# Presentation Script
## US Copyright Law as Code — Stanford Law Hackathon
### ~5 minutes (plus live demo)

---

## Slide 1: Title (15 sec)

Hi everyone, I'm Kate. Today I'm going to show you a project that turns 230 years of US copyright legislation into something you can explore with a single tool most of you already know — git.

---

## Slide 2: The Problem (30 sec)

Here's a question that comes up constantly in copyright litigation: **What did the law actually say at the time of infringement?**

Copyright law has been amended 121 times since 1790. Courts don't care what the statute says today — they care what it said when the alleged infringement happened. But there's no single source that reconstructs the historical text. Lawyers end up doing expensive, manual research across scattered government archives. What if we could make that as easy as checking out a git commit?

---

## Slide 3: The Solution (30 sec)

That's exactly what this project does. We treat legislation like source code. Each Act of Congress becomes a git commit. The commit message has the act name, the Public Law number, and the Statutes at Large citation. The files changed are the actual sections of Title 17 that the act modified.

So now, if you want to know what copyright law said in 1985, you literally just `git checkout` the right commit. You want to see what the DMCA changed? `git diff`. It's the version control interface applied to law.

---

## Slide 4: By the Numbers (20 sec)

Here's the scope: 121 acts, spanning 236 years, covering all 124 sections of Title 17. We have 413 automated tests that verify the legal accuracy of the reconstructed text. And the whole thing was built in one day — today — with the help of Claude.

---

## Slide 5: Demo — Copyright Duration (40 sec)

Let me show you why this is powerful. Here's the story of copyright duration in America.

In 1790, copyright lasted 14 years. By 1831, that doubled to 28. The 1909 Act added a 28-year renewal. Then the 1976 Act made the jump to life of the author plus 50 years. And in 1998, the Sonny Bono Act extended it to life plus 70.

With this repo, you don't read about that in a textbook. You see the actual diff. Here — `git diff v1976 v1998-ctea`. The word "fifty" becomes "70." That's it. That one word change affected every copyrighted work in America. And now it's visible as a two-line diff.

---

## Slide 6: Demo — Architectural Works (30 sec)

Here's another one. When did buildings become copyrightable? A defendant says "architectural works have always been protected." The repo shows that's wrong. Section 102 listed exactly seven categories of copyrightable works until December 1, 1990, when the Architectural Works Act added category eight. Before that commit, the category simply didn't exist. The commit boundary makes it unambiguous.

---

## Slide 7: The Website (30 sec)

But not everyone lives in a terminal. So we also built a full web app — a static site, no server needed. You get a chronological timeline of every act. Click one to see exactly what it changed. You can read any section at any point in history with a version dropdown. There's a side-by-side diff viewer with word-level highlighting, and a Ramseyer-format redline — that's the congressional style with strikethroughs and underlines inline. There's an "as of" date picker — type in any date from 1790 to today and see the entire copyright statute as it existed then. And there's full-text search across all acts and sections. Let me show you.

---

## Slide 8: Live Demo (~1-2 min)

*[Switch to browser — open site/index.html]*

**Suggested demo flow:**
1. **Home page** — point out the timeline on the left, the era groupings, the "most amended sections" chart
2. **Click an act** (e.g., Sonny Bono CTEA) — show the diff view with green/red additions and deletions
3. **Click a section** (e.g., §302) — show the version dropdown, select the 1976 version vs. 1998 version
4. **Compare versions** — show the side-by-side diff with word-level highlighting
5. **Ramseyer view** — toggle to show the congressional redline format
6. **As-of date** — type "1985-06-15" and show the law as it existed then
7. **Search** — type "DMCA" or "architectural" to show instant results

*[Switch back to slides]*

---

## Slide 9: Who Is This For (20 sec)

The audiences here are broad. Litigators who need the statute text at time of infringement. Legislators who want to see the cumulative effect of 50 years of patchwork amendments. Researchers studying how copyright scope has expanded. And educators who want students to explore the law interactively rather than reading a static casebook.

---

## Slide 10: Bugs in the Law (40 sec)

Here's something we didn't expect. When you apply every amendment mechanically, you find places where Congress's own instructions don't compile. We've found 9 anomalies so far. Let me give you three quick examples.

**Duplicate letters.** In 2019, the NDAA created two subsections of Section 105 both lettered (c) — one for government use, one for definitions. That duplicate lived in the actual United States Code for three years before another act fixed it.

**Letter collision.** In that same fix-up law, two different committees — Armed Services and Intelligence — each added a different institution to the same list as subparagraph (M). One added the Merchant Marine Academy, the other added National Intelligence University. Neither committee knew about the other. The OLRC had to sort out who got (M) and who got bumped to (N).

**History erased.** In 2004, Congress did a wholesale rewrite of Chapter 8 — the Copyright Royalty Board. When they did, 28 years of amendment history to the old Section 802 effectively vanished. The current official notes only cover post-2004 changes. If you want to know what the royalty tribunal rules said in 1995, you can't get there from any current government source. It's the legislative equivalent of a `git push --force` that squashed decades of commits.

The punchline: version control doesn't just record the law — it audits it. These bugs are invisible unless you try to apply every amendment programmatically.

---

## Slide 11: What's Next (15 sec)

We're nearly there — 413 tests passing, only 8 acts remaining. Those last 8 are the hardest — sections like §114 and §119 that went through complete chapter-level rewrites, so you can't reconstruct them from amendment notes alone. Beyond that: expand to patent and trademark law, and open it up for law students to contribute.

---

## Slide 12: Closing (10 sec)

So the next time someone asks "what did the law say then?" — now you can `git checkout` and find out. Thank you.

---

## Demo Tips

- **Before presenting**: Open `site/index.html` in a browser tab, ready to switch to on Slide 8. Pre-navigate to the home page so it loads instantly.
- **Browser zoom**: Set browser zoom to ~125-150% so the audience can read the text.
- **Fallback**: If the live demo has issues, the slides (5, 6, 7) already have the key code blocks and feature descriptions — just talk through them.
- **Timing**: The live demo is flexible. If you're running short, show just the as-of date picker (biggest "wow"). If you have time, walk through all 7 demo steps.
- **Questions to anticipate**:
  - "How accurate is the reconstructed text?" → 413 automated tests verify specific legal facts (e.g., that "fifty years" appears in the 1976 version of §302). The tests caught multiple bugs during development.
  - "What about pre-1976 law?" → We have the full text for all 38 pre-1976 acts, sourced from the Statutes at Large and historical U.S. Code.
  - "Could this work for other areas of law?" → Absolutely. Any title of the U.S. Code that has editorial amendment notes could be reconstructed the same way.
  - "Is it open source?" → Yes, public domain statute text under CC0.
