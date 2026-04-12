# Example 8: Finding Stale vs. Active Sections

**Scenario**: A legislator wants to know which parts of copyright law are actively maintained and which parts haven't been touched in decades. This helps prioritize which sections may need modernization.

## Step 1: Count amendments per section

```
$ for f in sections/*.md; do
    count=$(git log --oneline -- "$f" | wc -l)
    echo "$count $f"
  done | sort -rn | head -10
```

Output:

```
9 sections/119.md
9 sections/111.md
7 sections/101.md
6 sections/501.md
5 sections/506.md
5 sections/303.md
4 sections/803.md
4 sections/504.md
4 sections/411.md
4 sections/301.md
```

## What the most-amended sections tell us

**Section 119** (9 amendments) covers secondary transmissions by satellite carriers. It has been reauthorized and amended repeatedly — nearly every few years — because it contains sunset provisions that force Congress to revisit it.

**Section 111** (9 amendments) covers secondary transmissions by cable systems. Like 119, this section deals with compulsory licensing for retransmission, an area where technology constantly outpaces the law.

**Section 101** (7 amendments) is the definitions section. It grows every time Congress adds a new concept — "digital transmission," "work of visual art," "architectural work" — each requiring a formal definition.

**Section 506** (5 amendments) is criminal penalties, which Congress has ratcheted up repeatedly. See [Example 4](04-criminal-penalties.md).

## Step 2: Find sections never amended since 1976

```
$ for f in sections/*.md; do
    count=$(git log --oneline -- "$f" | wc -l)
    if [ "$count" -eq 1 ]; then
        echo "$f"
    fi
  done
```

These sections have only the original 1976 Act commit — they've been untouched for nearly 50 years. Candidates for review: do they still make sense in the digital age?

## Step 3: Compare the busiest and quietest sections

The contrast is striking:

- **Section 119** (satellite retransmission): 9 acts in ~40 years. Congress revisits this constantly.
- **Section 107** (fair use): 2 acts in ~50 years. One of the most litigated provisions in copyright law, yet Congress has barely touched it, leaving the courts to develop the doctrine through case law.

This asymmetry is itself a finding: Congress actively maintains the sections that deal with specific technology licensing (cable, satellite) but leaves the broad doctrinal provisions (fair use, idea/expression) to judicial interpretation.

## Why this matters

For a legislator, this analysis answers a practical question: where should we focus? Sections that have been amended 7+ times may have become internally inconsistent through accumulated patches. Sections that haven't been touched since 1976 may contain assumptions about technology or markets that no longer hold. Either pattern is a signal that review is warranted.
