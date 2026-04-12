# Example 1: Was Copyright Notice Required?

**Scenario**: You're evaluating whether a photograph published in 1985 without a copyright notice entered the public domain. The answer depends on what Section 401 said in 1985.

## Step 1: Find the relevant commits

```
$ git log --oneline -- sections/401.md
ed2801e Berne Convention Implementation Act of 1988
383d0e5 Copyright Act of 1976
```

Section 401 was created by the 1976 Act and then amended by the Berne Convention Implementation Act of 1988. A work published in 1985 was governed by the original 1976 version.

## Step 2: Read the law as it existed before the 1988 amendment

```
$ git show ed2801e~1:sections/401.md
```

This outputs the text of Section 401 as it stood between 1976 and 1988:

> §401. Notice of copyright: Visually perceptible copies
>
> (a) **General Requirement.**—Whenever a work protected under this title is published in the United States or elsewhere by authority of the copyright owner, a notice of copyright as provided by this section **shall be placed on all publicly distributed copies** from which the work can be visually perceived, either directly or with the aid of a machine or device.

Notice was **mandatory** ("shall be placed on all").

## Step 3: See what the 1988 Berne Convention Act changed

```
$ git diff ed2801e~1 ed2801e -- sections/401.md
```

Key changes in the diff:

```diff
-(a) General Requirement.-Whenever a work protected under this title is
-published in the United States or elsewhere by authority of the copyright
-owner, a notice of copyright as provided by this section shall be placed
-on all publicly distributed copies
+(a) General Provisions.-Whenever a work protected under this title is
+published in the United States or elsewhere by authority of the copyright
+owner, a notice of copyright as provided by this section may be placed
+on publicly distributed copies
```

The Berne Convention Implementation Act changed:
- "General Requirement" → "General Provisions"
- "**shall** be placed on **all** publicly distributed copies" → "**may** be placed on publicly distributed copies"
- Removed subsection (d) on evidentiary weight of notice

## Conclusion

For the 1985 photograph: notice **was** required. The mandatory notice regime was in effect until the Berne Convention Implementation Act took effect on March 1, 1989. Whether the omission actually placed the work in the public domain depends on Section 405's cure provisions — which you can also check by examining `sections/405.md` at the same commit.
