# Findings schema

A findings file is UTF-8 JSON whose top level is an **array** of records.

Each record is an object with **exactly** six fields:

- No field may be missing.
- No other field is allowed.
- Duplicate keys and non-standard constants (`NaN`, `Infinity`) are rejected.

| Field | Type | Rule |
|---|---|---|
| `signal` | string | one of `baseline`, `code-surface`, `logs`, `change`, `apm`, `browser`, `docs` |
| `status` | string | one of `PASS`, `SKIP`, `FAIL` |
| `proof_of_work` | string | one of `verified`, `unverified`, `failed`; must pair with `status` |
| `correlation_id` | string or null | user-supplied identifier linking related evidence |
| `logfile` | string or null | input path as given to the tool; null for absent or manual evidence |
| `detail` | string | at most 2000 characters; a sanitized excerpt or an explanation |

## Status pairs

| status | proof_of_work | Meaning |
|---|---|---|
| `PASS` | `verified` | Usable evidence was captured for this signal. It never means the bug is fixed or a hypothesis is confirmed. |
| `SKIP` | `unverified` | The evidence is absent, was not provided, is empty or is not collected automatically. |
| `FAIL` | `failed` | Collection was attempted but failed, for example because the input was missing, unreadable or not a regular file. |

Any other combination is invalid. The schema has no overall verdict field, by design.

## Signals

- `baseline`: the reproduced error, from the `--error` file.
- `code-surface`: the code path involved. Recorded by hand.
- `logs`: a log excerpt, from the optional `--logs` file.
- `change`: what changed and when. Recorded by hand as a sanitized summary.
  - Git metadata is never collected automatically, because author names and commit messages can leak data.
- `apm`: a trace or metrics summary. Recorded by hand.
- `browser`: a console or network excerpt. Recorded by hand.
- `docs`: a documentation, changelog or release-note reference. Recorded by hand.

A signal may appear more than once. Records are kept in the order they were added. A later record adds to earlier records; it never erases them.

## Collection behaviour

`collect` writes one record per signal, in the order listed above:

- An input that is missing, unreadable or not a regular file gives `FAIL`.
- An input that is empty or contains only whitespace gives `SKIP`.
- An optional input that was not supplied gives `SKIP`.
- Signals with no automatic collection give `SKIP`.

The tool does **no redaction**:

- Only the first 1500 characters of a trimmed input are stored.
- The stored text is prefixed with a note saying it was not redacted and, if applicable, that it was truncated.
- The rest of the file is not copied.
- Sanitize inputs before collection.

## Write guarantees

- `collect` and `render --out` only create new files. They refuse an existing path.
- New parent directories are created with mode `0700`. Files are written with mode `0600`.
- `collect` and `render --out` write a temporary file, then hard-link it into place.
  - This is atomic and never overwrites.
  - On filesystems without hard links, the tool falls back to an exclusive create, which is non-atomic but still never overwrites.
- `append` validates the whole existing document first.
  - If the document is invalid, the command exits `1` and the file's bytes are untouched.
  - Otherwise the tool validates the new document and swaps it in atomically, via a temporary file and a rename.
- Single writer only. Concurrent `append` runs on one file are not supported.

## Exit codes

- `0`: success. A `FAIL` record is evidence, not a process failure.
- `1`: the findings document is invalid. Errors are listed on stderr.
- `2`: usage or I/O error, including a refusal to overwrite.

## Example

```json
[
  {
    "signal": "logs",
    "status": "SKIP",
    "proof_of_work": "unverified",
    "correlation_id": "demo-0001",
    "logfile": null,
    "detail": "No logs file provided (optional)."
  }
]
```

See `examples/findings.json` in the repository for a complete synthetic document.
