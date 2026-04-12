# Example 4: How Criminal Penalties Escalated Over Time

**Scenario**: A legislator wants to understand how Congress has ratcheted up criminal copyright penalties. Or a defense attorney needs to know what penalties applied at the time of the alleged offense.

## Step 1: Find every act that amended Section 506

```
$ git log --oneline -- sections/506.md
2c4a452 Family Entertainment and Copyright Act of 2005
dd0f26d No Electronic Theft Act of 1997 (NET Act)
922771e Computer Software Rental Amendments Act of 1990
e27c447 Piracy and Counterfeiting Amendments Act of 1982
383d0e5 Copyright Act of 1976
```

Five versions across nearly 30 years — each one expanding what counts as a criminal offense or increasing the penalties.

## Step 2: See the original 1976 provision

```
$ git show 383d0e5:sections/506.md
```

The original Section 506(a) was a single sentence:

> Any person who infringes a copyright willfully and for purposes of commercial advantage or private financial gain shall be fined not more than $10,000 or imprisoned for not more than one year, or both.

Key features: criminal infringement required **both** willfulness **and** commercial motive. Maximum fine: $10,000. Maximum imprisonment: 1 year.

## Step 3: Trace the escalation

### 1982 — Piracy and Counterfeiting Amendments Act

```
$ git diff e27c447~1 e27c447 -- sections/506.md
```

Added enhanced penalties specifically for sound recordings and motion pictures:
- First offense: up to **$25,000** fine or **1 year** imprisonment
- Subsequent offenses: up to **$50,000** fine or **2 years**

### 1997 — No Electronic Theft Act (NET Act)

The NET Act was transformative. Before 1997, criminal infringement required "commercial advantage or private financial gain." The NET Act removed that requirement for large-scale infringement, making it a crime to reproduce or distribute copyrighted works even without profit motive, if the total retail value exceeded $1,000 in a 180-day period.

### 2005 — Family Entertainment and Copyright Act

Added pre-release piracy provisions: distributing a work "being prepared for commercial distribution" by making it available on a public computer network became a distinct criminal act.

## The full escalation at a glance

| Year | Act | Key change |
|------|-----|-----------|
| 1976 | Copyright Act | $10K max fine, 1 year max. Requires willfulness + commercial motive. |
| 1982 | Piracy and Counterfeiting Amendments | $25K/$50K for sound recordings and motion pictures. |
| 1990 | Computer Software Rental Amendments | Extended to cover software. |
| 1997 | NET Act | Removed commercial motive requirement for large-scale infringement. |
| 2005 | Family Entertainment Act | Criminalized pre-release distribution on computer networks. |

Each row is a commit. Each change is a diff.
