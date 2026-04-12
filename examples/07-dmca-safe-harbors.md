# Example 7: When Did DMCA Safe Harbors Appear?

**Scenario**: A platform operator is sued for user-uploaded infringing content hosted in 1997. They claim protection under Section 512's safe harbor provisions. The plaintiff argues those protections didn't exist yet. Who's right?

## Step 1: Check whether Section 512 existed

```
$ git log --oneline -- sections/512.md
cf4710f Digital Millennium Copyright Act of 1998 (DMCA)
```

One commit. Section 512 was created entirely by the DMCA in 1998 — it did not exist before.

## Step 2: Verify the section didn't exist before the DMCA

```
$ git show cf4710f~1:sections/512.md
```

This fails with a "path does not exist" error — confirming that there was no Section 512 before the DMCA commit. The safe harbor framework did not exist in 1997.

## Step 3: Read the safe harbor as created

```
$ git show cf4710f:sections/512.md
```

Section 512 established four safe harbors for online service providers:

- **(a) Transitory Digital Network Communications** — mere conduit (routing, transmitting)
- **(b) System Caching** — intermediate and temporary storage
- **(c) Information Residing on Systems at Direction of Users** — hosting user-uploaded content
- **(d) Information Location Tools** — linking to infringing material

Each safe harbor has conditions: the provider must not have actual knowledge of infringement, must not receive a financial benefit directly attributable to infringement (where they have the ability to control it), and must comply with the notice-and-takedown procedures.

## Step 4: Check whether Section 512 has been amended since

```
$ git log --oneline -- sections/512.md
cf4710f Digital Millennium Copyright Act of 1998 (DMCA)
```

Only one commit — Section 512 has never been amended since its creation. One of the most consequential provisions in internet law has remained unchanged for over 25 years, even as the internet transformed around it.

## Conclusion

The platform operating in 1997 cannot claim Section 512 protection — it did not exist yet. The DMCA was signed into law on October 28, 1998. Before that date, there was no statutory safe harbor for service providers, and platform liability was governed by common law and a handful of circuit court decisions.

The commit boundary makes the answer unambiguous: before commit `cf4710f`, the file `sections/512.md` does not exist.
