# Playbook: regression

Use this playbook when the behaviour used to work and now does not.

## Reproduce

- Establish the last-known-good and the first-known-bad: a version, release, date or environment.
- Confirm that both states really behave differently with the same input and environment. Repeat each a few times to rule out flakiness.

## Investigate

- List what changed between the two states:
  - code
  - dependency lockfiles
  - configuration
  - feature flags
  - data or schema
  - infrastructure
- Read scoped history: `git log`, `git show` and `git diff` over the good-to-bad range and the failing paths, and `git blame` on the failing lines. See "Change history" in `SKILL.md`.
- Bisect only in a task-owned isolated worktree, and only when the reproduction is reliable and safe and the range justifies it.
  - Run each step in Docker.
  - Skip untestable revisions (exit code 125). Never mark infrastructure failures bad.
  - Report an ambiguous boundary as unknown.
  - Remove only the worktree and artifacts you created.
- Never check out revisions over the user's working tree.
- Record the `change` signal by hand as a sanitized summary: what changed and roughly when. A reviewed short commit reference is fine.
  - Do not paste author names, emails, full commit messages or raw log output.
- Read the diff of the suspect change and append the affected code as `code-surface`.
- If the change came from a dependency, continue with `dependencies.md`.

## Fix, guard, verify

- Prefer correcting the regression over reverting unrelated parts of the change. Do not revert or reset anything unless the user asks.
- Write a test that pins the old, correct behaviour.
  - It must fail on the first-known-bad code and pass after the fix.
- Run the tests around the changed area. Regressions often have siblings.
