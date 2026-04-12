# Example 6: What Statutory Damages Were Available?

**Scenario**: A rights holder discovers that their work was infringed in 1990. They want to know what statutory damages were available under Section 504 at the time. Or: a defendant is arguing that the current damages range is a recent escalation and not what Congress originally intended.

## Step 1: Find every act that amended Section 504

```
$ git log --oneline -- sections/504.md
e5b9264 Intellectual Property Protection and Courts Amendments Act of 2004
54472f4 Copyright Technical Amendments Act of 1997
b78267c Berne Convention Implementation Act of 1988
81814ae Copyright Act of 1976
```

Four versions. The damages range has been adjusted multiple times.

## Step 2: See the damages range after the Berne Convention Act

```
$ git show b78267c:sections/504.md
```

After the Berne Convention Implementation Act, the statutory damages range was:

- **Minimum**: $250 per work
- **Maximum**: $10,000 per work
- **Willful infringement**: up to $50,000
- **Innocent infringement**: as low as $100

For a 1990 infringement, these were the numbers in effect.

## Step 3: See how the 1997 amendments changed the range

```
$ git diff b78267c 54472f4 -- sections/504.md
```

Key changes in the diff:

```diff
-in a sum of not less than $250 or more than $10,000 as the court considers just.
+in a sum of not less than $500 or more than $30,000 as the court considers just.
```

```diff
-may increase the award of statutory damages to a sum of not more than $50,000.
+may increase the award of statutory damages to a sum of not more than $100,000.
```

```diff
-may reduce the award of statutory damages to a sum of not less than $100.
+may reduce the award of statutory damages to a sum of not less than $200.
```

Every dollar figure was raised — the minimum doubled, the maximum tripled, and the willful cap doubled.

## The escalation at a glance

| Era | Min | Max | Willful Max | Innocent Min |
|-----|-----|-----|-------------|--------------|
| 1976-1997 | $250 | $10,000 | $50,000 | $100 |
| 1997-present | $500 | $30,000 | $100,000 | $200 |

## Why this matters

Statutory damages are often the most important remedy in copyright cases, especially when actual damages are hard to prove. The difference between a $10,000 cap and a $30,000 cap per work — multiplied across dozens or hundreds of works — can be the difference between a nuisance settlement and a bet-the-company lawsuit. Knowing which range applied at the time of infringement is essential for both sides.
