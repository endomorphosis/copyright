# Example 5: Exploring the Full Timeline

**Scenario**: You want to understand the overall shape of US copyright law — how it grew from a single statute to 122 sections, and how active Congress has been in amending it.

## How many acts have amended copyright law?

```
$ git log --oneline | wc -l
122
```

122 commits (121 acts plus the initial commit), from 1790 to 2025.

## Tags mark the major milestones

```
$ git tag -l
v1790
v1831
v1870
v1909
v1976
v1984-chips
v1988-berne
v1998-ctea
v1998-dmca
v2018-mma
v2020-case
```

## Compare entire eras

### The 1976 rewrite

The Copyright Act of 1976 was the most sweeping change in the repository. It replaced the entire pre-1976 structure with the modern section numbering:

```
$ git diff v1909 v1976 --stat | tail -5
 87 files changed, 2491 insertions(+), 475 deletions(-)
```

87 files changed — the pre-1976 era files were removed and the modern section files were created.

### The digital era (1976 to DMCA)

```
$ git log --oneline v1976..v1998-dmca | wc -l
40
```

40 acts amended copyright law in the 22 years between the 1976 Act and the DMCA. That's roughly two acts per year.

## Read the law at any point in time

Want to know exactly what copyright law said in 1990, after the Architectural Works Act but before the Audio Home Recording Act? Check out that commit:

```
$ git checkout 69e7597
```

Now every file in `sections/` reflects the law as it existed at that moment. Browse freely, then return:

```
$ git checkout main
```

## Trace a single section from birth to present

Example: Section 107 (fair use), perhaps the most cited section in copyright law:

```
$ git log --oneline -- sections/107.md
922771e Computer Software Rental Amendments Act of 1990
383d0e5 Copyright Act of 1976
```

Fair use has been amended only once since the 1976 Act codified it. This is notable — one of the most litigated provisions in copyright law has been left almost entirely to judicial interpretation.

## Count amendments per section

To find the most-amended sections:

```
$ for f in sections/*.md; do
    count=$(git log --oneline -- "$f" | wc -l)
    echo "$count $f"
  done | sort -rn | head -10
```

This reveals which parts of the law Congress returns to most often — useful for understanding where the law is most contested or most in flux.

## The first federal copyright law

```
$ git show v1790 -- pre-1976/copyright-act-of-1790.md
```

The Copyright Act of 1790 protected "maps, charts, and books" for 14 years with a 14-year renewal. Compare that to today's law — life of the author plus 70 years, covering everything from software to architectural works to vessel hull designs — and you can see the full arc of 236 years of legislative expansion in a single `git diff`.
