# OC Debug

> **Status: release candidate, not yet public.** The unit tests, the example `validate` and `render` runs and the install-copy snippet passed in Docker. See [Verification](#verification) for the scope and test environment. Integration with live coding agents and with a software factory is still in progress.

**OC Debug** is an evidence-first debugging skill for coding agents. It walks the agent through six steps: reproduce, classify, investigate, fix, guard and verify. It also ships a small tool built only on the Python standard library. The tool records which evidence was captured (PASS), which is missing (SKIP) and which could not be gathered (FAIL). It never declares a bug fixed.

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

## Requirements

- Docker (Engine or Desktop) that can build Linux images. The build pulls `python:3.12-slim`, pinned to the digest given in `Dockerfile`, and installs nothing else.
- No third-party Python packages. The tool and tests use only the Python standard library, so no lockfile is needed.
- A POSIX shell for the commands below.
- A coding agent that loads skills from a skills directory, for example Claude Code (`~/.claude/skills/`).
- Nothing else on the host: no Python, pip or packages. The tool and the tests run only inside the container.

## Build

Run this from the root of your local checkout:

```sh
docker build -t oc-debug:rc .
```

## Test (Docker only)

```sh
docker run --rm --network none --read-only \
  --tmpfs /tmp:rw,nosuid,nodev,size=64m \
  --cap-drop ALL --security-opt no-new-privileges \
  --entrypoint python \
  oc-debug:rc -B -m unittest discover -s /opt/oc-debug/tests -v
```

The tests run as the image's non-root user and write only to the container's `/tmp`. They never write to the package: the root filesystem is read-only, `PYTHONDONTWRITEBYTECODE=1` is set and Python runs with `-B`. The expected result is a unittest summary ending in `OK`.

## Verification

These results were observed for this release candidate. It was built from the pinned base in `Dockerfile` with Docker Engine 29.1.3 on Linux x86_64 (CPython 3.12.15, running as uid 65532). The tree was not yet a tagged commit:

- All 15 unit tests passed. They cover `collect`, `append`, `validate`, `render` and CLI error exits.
- `validate` and `render` succeeded on `examples/findings.json` (9 records).
- The install snippet in the next section ran in a disposable home inside the container. It copied the skill with its references, and a second run left the existing install untouched.

Not yet verified: use by a live coding agent, integration with a software factory, the mounted `--user` commands under "Use the tool", and other platforms such as arm64 or Docker Desktop.

## Install the skill (copy, never overwrite)

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

The snippet never replaces an existing install. To upgrade, review the old copy and move it aside yourself.

Build the image from the same checkout, so the installed skill and the tool inside the container match.

## Use the tool (Docker only)

The skill runs these commands, and you can also run them yourself. Every run uses:

- no network
- a read-only root filesystem
- no capabilities
- your own non-root user (`--user`)
- explicit mounts

Do not run these containers as root. Do not add `--privileged`, capabilities, network access or the Docker socket.

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

- Only the agent reads it. The CLI ignores it, and nothing executes it.
- It holds hints only: no commands, endpoints, secrets or instructions.
- It does not prove access or grant permission. The agent's runtime tool discovery and permissions decide what is available.
- It is never required. Without it, the agent discovers tools at runtime.

## Asking the agent

- `Investigate with oc-debug: the checkout endpoint returns HTTP 500 for empty carts since yesterday. A sanitized error excerpt is in oc-debug-in/error.txt.`
- `Use oc-debug inline: what causes this stack trace? <paste sanitized trace>`
- `oc-debug, regression playbook: the nightly export worked in release 1.3 and times out in 1.4. Don't commit anything.`
- `Render the oc-debug findings and list which signals are still SKIP or FAIL.`

## Software factory integration (in progress)

OC Debug is meant to be callable from a software factory or another automated pipeline. The intended contract:

- The caller supplies a sanitized reproduction and a description of the environment.
- The caller invokes OC Debug through its coding agent.
- OC Debug returns the evidence (findings), the identified cause or the open unknowns, a proposed fix with a regression check and its verification, and a human-readable report.

The factory owns its workflow, including routing, approvals and what happens to a proposed fix. This package contains no automatic routing or factory adapters. The contract has not yet been verified against a real factory. An optional `.oc-debug.json` stays a hint for the agent. It does not configure the CLI or authorize anything to run.

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
