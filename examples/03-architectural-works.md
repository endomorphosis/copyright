# Example 3: When Did Architectural Works Become Copyrightable?

**Scenario**: A defendant argues that a building design was not copyrightable when it was created in 1988. Or a plaintiff claims architectural works have always been protected. The repository settles the question.

## Step 1: Find every act that amended Section 102 (subject matter)

```
$ git log --oneline -- sections/102.md
69e7597 Architectural Works Copyright Protection Act of 1990
922771e Computer Software Rental Amendments Act of 1990
383d0e5 Copyright Act of 1976
```

## Step 2: See the diff from the Architectural Works Act

```
$ git diff 69e7597~1 69e7597 -- sections/102.md
```

```diff
 (5) pictorial, graphic, and sculptural works;
-(6) motion pictures and other audiovisual works; and
-(7) sound recordings.
+(6) motion pictures and other audiovisual works;
+(7) sound recordings; and
+(8) architectural works.
```

Before December 1, 1990, Section 102(a) listed exactly seven categories of copyrightable works. The Architectural Works Copyright Protection Act added the eighth: "architectural works."

## Step 3: Read the law as it existed during the disputed period

For a building designed in 1988:

```
$ git show 922771e:sections/102.md
```

This shows the version of Section 102 in effect between the Computer Software Rental Amendments Act (also 1990, but earlier) and the Architectural Works Act. No category (8) exists.

## Conclusion

Architectural works were **not** a listed category of copyrightable subject matter until December 1, 1990. A building designed in 1988 could not claim protection as an "architectural work" under Section 102 — though elements of it might have qualified as "pictorial, graphic, and sculptural works" under the pre-existing category (5), subject to the useful article doctrine.

The commit boundary makes this unambiguous: before commit `69e7597`, the category did not exist.
