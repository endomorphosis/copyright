# Contributing

Thank you for helping build a complete legislative history of US copyright law.

## How to Contribute

### Adding a Missing Act

1. Identify the Public Law number, enactment date, and Statutes at Large citation.
2. Find the full text of the act (see Sources in README.md).
3. Determine which sections of the statute were affected.
4. Create a commit with the changes, following the commit conventions below.

### Correcting Existing Text

If you find an error in the statute text (typo, missing section, incorrect amendment), please open an issue with:
- The specific section and text that is wrong
- The correct text with a citation to the authoritative source
- The act/commit where the error was introduced

### Commit Format

```
<Act Name> (<Year>)

Public Law: <Pub.L. number or Statutes at Large citation>
Effective date: <YYYY-MM-DD>
Summary: <1-3 sentence description of what changed>
```

Set the author date to the enactment date:
```bash
GIT_AUTHOR_DATE="YYYY-MM-DD" git commit -m "..."
```

### File Format

- Statute text is in Markdown (.md)
- Use `#` headings for section titles
- Preserve original formatting, spelling, and punctuation from the source
- Use `> [Note]` blockquotes for editorial annotations (not part of the statute text)

### What Counts as a Copyright Act?

Include any Public Law that:
- Creates or amends provisions of Title 17 U.S.C. (post-1976)
- Creates or amends federal copyright statutes (pre-1976)
- Directly affects copyright protection, registration, duration, remedies, or related rights

Do not include:
- Appropriations acts (unless they contain substantive copyright provisions)
- Treaties (unless implemented by domestic legislation)
- Administrative regulations (Copyright Office rules)

## Code of Conduct

Be respectful and constructive. This is a factual/historical project -- edits should be based on authoritative legal sources, not opinions about what the law should say.
