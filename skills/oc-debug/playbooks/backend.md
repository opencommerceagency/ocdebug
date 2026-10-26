# Playbook: backend

Use this playbook for server errors (5xx), exceptions, timeouts, background jobs, queues, APIs and data problems.

## Reproduce

- Capture the request or job input as a synthetic or sanitized fixture.
- Note the endpoint, method, status code and environment.
- Use the actual request ID and time window to tie related evidence together.
  - Pass it to `collect` as `--correlation-id` only when the error and log excerpts are confirmed to share it.
  - Otherwise add records separately with `append`. See "Correlating evidence" in `SKILL.md`.

## Investigate

- `logs`: give the tool a short excerpt filtered to the correlation ID, not a whole log file.
- `apm`: if traces exist in a source you are already authorized to read, append a sanitized summary: the slow or failing span, its timing and the service order.
- Check that log and trace timestamps fall in the same window and follow the expected service order. Note clock skew.
- Checklist:
  - input validation and null handling
  - type and serialization mismatches
  - transactions and locking
  - timeouts and retries
  - concurrency and ordering
  - caching
  - configuration and environment variables
  - migrations and schema drift
  - external service responses
- Never query or modify production data to test a hypothesis. Ask the user to do it.

## Fix, guard, verify

- Fix at the boundary where the bad state first enters. Avoid defensive patches downstream.
- Write a unit or integration test with a synthetic fixture that reproduces the failing input. It must fail before the fix and pass after it.
- Re-run the original failing request or job with the safe fixture, then the service's related test suite, in Docker. Report the results.

## Pitfalls

- Stack traces, SQL and headers can contain tokens or personal data. Make sure they are sanitized before collection.
