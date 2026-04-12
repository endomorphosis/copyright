# Example 2: How Copyright Duration Changed

**Scenario**: You need to determine when a specific work enters the public domain, or you want to show how Congress has repeatedly extended copyright terms.

## Step 1: Find every act that amended Section 302

```
$ git log --oneline -- sections/302.md
c3ae9a7 Fairness in Music Licensing Act of 1998
a28fefd Sonny Bono Copyright Term Extension Act of 1998
81814ae Copyright Act of 1976
```

## Step 2: See the original 1976 Act's duration terms

```
$ git show 81814ae:sections/302.md
```

The original terms established by the 1976 Act:
- Individual authors: life of the author + **fifty years**
- Joint works: life of the last surviving author + **fifty years**
- Works for hire / anonymous / pseudonymous: **seventy-five years** from publication or **one hundred years** from creation

## Step 3: See exactly what the CTEA changed in 1998

```
$ git diff a28fefd~1 a28fefd -- sections/302.md
```

The diff shows the precise substitutions:

```diff
-(a) In General.-Copyright in a work created on or after January 1, 1978,
-subsists from its creation and, except as provided by the following
-subsections, endures for a term consisting of the life of the author and
-fifty years after the author's death.
+(a) In General.-Copyright in a work created on or after January 1, 1978,
+subsists from its creation and, except as provided by the following
+subsections, endures for a term consisting of the life of the author and
+70 years after the author's death.
```

```diff
-(c) ...the copyright endures for a term of seventy-five years from the
-year of its first publication, or a term of one hundred years from the
-year of its creation, whichever expires first.
+(c) ...the copyright endures for a term of 95 years from the year of
-its first publication, or a term of 120 years from the year of its
+creation, whichever expires first.
```

## The full timeline of copyright duration

You can trace the entire arc by checking out each era:

| Era | Term | Source |
|-----|------|--------|
| 1790 | 14 years + 14-year renewal | `git show v1790 -- pre-1976/copyright-act-of-1790.md` |
| 1831 | 28 years + 14-year renewal | `git show v1831 -- pre-1976/copyright-act-of-1831.md` |
| 1909 | 28 years + 28-year renewal | `git show v1909 -- pre-1976/copyright-act-of-1909.md` |
| 1976 | Life + 50 years | `git show 81814ae:sections/302.md` |
| 1998 | Life + 70 years | `git show a28fefd:sections/302.md` |

This table — built entirely from repository data — is a ready-made exhibit for any argument about the expansion of copyright terms.
