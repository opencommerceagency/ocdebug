# Playbook: general

Use this playbook for a first pass, or when the failure does not clearly fit another playbook.

## Reproduce

- Record the exact steps, the input, the environment (OS, runtime and versions), the expected result and the actual result.
- Shrink the reproduction until removing anything makes the failure disappear.
- Repeat it with the same input and environment. Record the exact command or steps and how often it fails.
- Do not replay side effects, such as writes, emails or payments, without a safe fixture.
- Save a short, sanitized error excerpt as the `baseline` input.

## Classify

- Deterministic or intermittent? For intermittent failures, note the frequency and conditions.
- New or long-standing? If it used to work, switch to `regression.md`.
- Which layer? backend, frontend, dependency, configuration, data or environment. Switch playbook when one clearly applies.

## Investigate

- Read the stack from the top down to the first frame in project code. Read that code and append it as `code-surface`.
- Check the cheap explanations first: input data, configuration, environment variables, versions and caches.
- Hold one hypothesis at a time. Write down what would refute it before you look.
- When behaviour depends on a library or platform, check authoritative docs for the installed version and cite them.
- Before fixing, write the investigation checkpoint from `SKILL.md`.
- Record every source you consult, even when it turned up nothing. Use SKIP with a reason.

## Fix, guard, verify

- Make the smallest change at the root cause. Do not catch-and-ignore.
- Add a regression test at the lowest level that reproduces the bug. It must fail before the fix and pass after it.
- Re-run the original failing operation, then the guard and the neighbouring tests, in Docker. Report anything that was not run.

## Stop and ask

- Stop if the next step needs production access, credentials, real customer data or destructive actions.
