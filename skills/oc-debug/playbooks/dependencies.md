# Playbook: dependencies

Use this playbook for failures after an upgrade, install or build problems, version conflicts and changes in transitive dependencies.

## Reproduce

- Reproduce in a clean, isolated environment, such as a fresh container, to rule out local state.
- Record the package manager and runtime versions, and the exact failing command.

## Investigate

- Compare the lockfiles between the good and the bad state. Identify direct and transitive version changes.
- `docs`: read the official changelog, release notes or migration guide for each changed package, for the versions actually installed.
  - Append the source and the versions it applies to.
  - Keep searches bounded. Record open questions as unresolved.
- `change`: append a sanitized summary of the version changes.
- Checklist:
  - breaking API changes and deprecations
  - peer dependency ranges
  - platform or native build requirements
  - duplicate copies of one package
  - changed defaults

## Fix, guard, verify

- Prefer adapting to the new API, or pinning one specific version with a stated reason. Avoid broad range changes.
- Do not upgrade unrelated packages, disable integrity checks or install from unofficial sources.
- Lockfile changes belong to the user. Show them and do not commit them unless asked.
- Write a test that exercises the exact API that broke. It must fail before the fix and pass after it.
