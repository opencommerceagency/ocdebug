# OC Debug

**OC Debug** is an evidence-first debugging skill for coding agents. It walks the agent through six steps: reproduce, classify, investigate, fix, guard and verify. 
It also ships a small tool built only on the Python standard library. The tool records which evidence was captured (PASS), which is missing (SKIP) and which could not be gathered (FAIL). 

## Contents

```text
skills/oc-debug/
  SKILL.md               workflow and agent rules
  FINDINGS_SCHEMA.md     findings record contract
  playbooks/             general, regression, backend, frontend, dependencies
  references/            capability inventory and final report guides
  tools/oc_debug.py      collect, append, render, validate (stdlib only)
tests/test_oc_debug.py   unittest suite, run in Docker
examples/                synthetic error excerpt, findings file and capability inventory
Dockerfile               python:3.12-slim pinned by digest, no package installs, non-root
```

## Asking the agent

- `Investigate with oc-debug: the checkout endpoint returns HTTP 500 for empty carts since yesterday. A sanitized error excerpt is in oc-debug-in/error.txt.`
- `Use oc-debug inline: what causes this stack trace? <paste sanitized trace>`
- `oc-debug, regression playbook: the nightly export worked in release 1.3 and times out in 1.4. Don't commit anything.`
- `Render the oc-debug findings and list which signals are still SKIP or FAIL.`

## Requirements
- Docker
- A POSIX shell for the commands below.
- A coding agent that loads skills from a skills directory, for example Claude Code (`~/.claude/skills/`).

## Build

Run this from the root of your local checkout:

```sh
docker build -t oc-debug:rc .
```

## Install the skill

Run this from the root of an existing local checkout:

```sh
dest="$HOME/.claude/skills/oc-debug"
if [ -e "$dest" ] || [ -L "$dest" ]; then
  echo "oc-debug already exists at $dest; leaving it untouched." >&2
else
  mkdir -p "$(dirname "$dest")" && cp -R skills/oc-debug "$dest"
fi
```

For a project-scoped install, set `dest` to `.claude/skills/oc-debug` inside that project.
The snippet never replaces an existing install. To upgrade remove the old copy first.

## Use the tool

The skill runs these commands, and you can also run them yourself. Every run uses:

- a read-only root filesystem
- your own non-root user (`--user`)
- explicit mounts

1. Create private input and output directories:

```sh
mkdir -m 700 oc-debug-in oc-debug-out
```

2. Add **sanitized** excerpts:

- Put a short error excerpt in `oc-debug-in/error.txt`.
- Optionally, put a short log excerpt in `oc-debug-in/logs.txt`. Filter it to the failing request first.

OC Debug performs **no redaction**. Remove secrets, tokens, cookies, personal data and client identifiers before you add a file. Only the first 1500 characters of each file are stored in a finding, with a truncation note. Hand-written `--detail` text is limited to 2000 characters. Never pass a whole log. Keep your sanitized excerpt files: the findings file holds only truncated copies, and container paths such as `/in/error.txt` do not resolve on the host.

3. Collect a new findings file. The tool refuses to overwrite an existing file.

```sh
docker run --rm --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges --user "$(id -u):$(id -g)" \
  -v "$PWD/oc-debug-in:/in:ro" -v "$PWD/oc-debug-out:/out" \
  oc-debug:rc collect --error /in/error.txt --logs /in/logs.txt \
  --correlation-id demo-0001 --out /out/findings.json
```

If you have no log excerpt, leave out `--logs /in/logs.txt`. The `logs` signal is then recorded as SKIP.

`collect` writes one `--correlation-id` to every record it creates. Pass it only when the error and log excerpts are confirmed to share that ID. Otherwise collect without it and add records separately with `append`, giving each its own verified ID or none.

After collection, `code-surface`, `change`, `apm`, `browser` and `docs` are always SKIP. Add them by hand with `append`. Git metadata is never collected automatically.

4. Append evidence you gathered by hand and sanitized:

```sh
docker run --rm --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges --user "$(id -u):$(id -g)" \
  -v "$PWD/oc-debug-out:/out" \
  oc-debug:rc append /out/findings.json --signal change --status PASS \
  --correlation-id demo-0001 \
  --detail "Hand-written summary: failure began after the cart serializer change in release 1.4."
```

5. Validate and render:

```sh
docker run --rm --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges --user "$(id -u):$(id -g)" \
  -v "$PWD/oc-debug-out:/out" \
  oc-debug:rc validate /out/findings.json

docker run --rm --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges --user "$(id -u):$(id -g)" \
  -v "$PWD/oc-debug-out:/out" \
  oc-debug:rc render /out/findings.json --out /out/findings.md
```

To try the synthetic example without any mounts:

```sh
docker run --rm --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges \
  oc-debug:rc render /opt/oc-debug/examples/findings.json
```

## Workflow references

The skill carries its references in its own directory, `skills/oc-debug/references/`, so a copied install includes them:

- `capabilities.md`: the optional capability inventory described below.
- `reporting.md`: the structure and wording of the final report.

Before any fix, the agent writes an investigation checkpoint: symptom, trigger, mechanism, supporting evidence and proposed correction, each marked observed, inferred or unresolved. A mitigation is reported as a mitigation, not as a causal fix. A PASS record shows that evidence was captured; it does not prove the cause.

## Optional capability inventory

A project may add `.oc-debug.json` at its root to tell the agent which evidence sources might help, such as an error tracker, an APM service or a security scanner. See `examples/capabilities.example.json`.

## Status meanings

| Status | proof_of_work | Meaning |
|---|---|---|
| PASS | verified | usable evidence was captured. It does **not** mean the bug is fixed. |
| SKIP | unverified | evidence was absent, not provided or empty |
| FAIL | failed | collection was attempted and failed, for example because the input was missing or unreadable |

There is no overall verdict.

Exit codes:

- `0`: success
- `1`: invalid findings document; the file is left unchanged
- `2`: usage or I/O error

A FAIL finding is evidence, not a tool failure, so it does not change the exit code. The full contract is in `skills/oc-debug/FINDINGS_SCHEMA.md`.

## Limits

- Single writer only. Do not run concurrent `append` commands on one file.
- Rendered reports escape Markdown, HTML and control characters. Their content is still untrusted diagnostic data.
- The tool makes no uploads, runs no shell commands, does not use the Docker socket and does not scrape logs across a repository.

## Licensing

Licensed under the [MIT License](LICENSE). Copyright (c) 2026 Open Commerce.

The Python and Debian components in the Docker base image retain their respective upstream licences.
