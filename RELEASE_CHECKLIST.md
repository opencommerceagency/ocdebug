# Release checklist

Status: **release candidate, untested.** No item is done until it is ticked, with evidence recorded next to it.

## Rights

- [ ] Confirm ownership of the OCPM Debug concepts and of this package.
- [ ] Obtain written permission to release an adaptation.
- [ ] Choose a licence with the rights holder.
  - If MIT is approved, add a LICENSE file covering only the rights-holder-owned original portions.
  - Update `PROVENANCE.md` to match.

- [ ] Review third-party notices for the pinned Python/Debian container image before distributing an image.

## Build and test

- [ ] Pin `python:3.12-slim` by digest in the `Dockerfile`.
- [ ] Run `docker build -t oc-debug:rc .` and confirm it succeeds. Record the image ID.
- [ ] Run the Docker test command from the README and confirm it passes. Save the full output.
- [ ] Validate and render `examples/findings.json` with the Docker commands.
- [ ] Render a hostile synthetic sample in each target Markdown viewer.
  - Confirm that no HTML executes.
  - Confirm that the table stays intact.
- [ ] Confirm that the containers run without network, capabilities or root, and that the package mount stays read-only.

## Content review

- [ ] Search every file for:
  - client names
  - internal hostnames or URLs
  - credentials
  - ticket numbers
  - personal names or emails
  - host-specific paths
- [ ] Confirm the examples are still synthetic.
- [ ] Copy and paste each README command to check that it works as written.

## Skill behaviour

- [ ] Install with the copy snippet into a clean environment.
- [ ] Confirm that an existing install is left untouched.
- [ ] Dry-run an inline debug session.
  - Confirm the agent makes no false verification claims.
- [ ] Dry-run an explicit investigation.
  - Confirm the agent loads the schema, the tool and the playbook first.
  - Confirm the regression test fails before the fix and passes after it.
  - Confirm unrelated work is left untouched.

## Publish

- [ ] Agree the destination and visibility with the rights holder. Push nothing anywhere before every item above is complete.
- [ ] Remove the "untested" status from the README only after the tests have passed. Record the date and the environment.
