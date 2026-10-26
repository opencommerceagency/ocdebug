# Final report

Read this before you write the final report of an explicit investigation. Use the sections below in this order. Keep each one short. If a section has nothing to say, write that in one line rather than dropping it.

## 1. Impact

Who or what is affected, since when, how often and how badly. Use the counts, times and environments you observed.

## 2. Cause and uncertainty

The mechanism from the investigation checkpoint, with each part marked observed, inferred or unresolved. State your confidence in plain words. If the cause is not proven, say so, and name the alternatives you could not rule out.

## 3. Evidence

The records and excerpts behind each claim: signal, status, source, command or query, time window and versions. Note truncation, and point to preserved excerpts. A PASS record is evidence that something was captured, not proof of the cause.

## 4. Change or mitigation

What you changed, file by file. Say whether it removes the cause or only mitigates the symptom, and what evidence shows that. If the mechanism is unknown, call it a mitigation or an unverified proposed fix. List anything you deliberately left unchanged.

## 5. Verification

Every check you ran: the exact command, the environment (for example the Docker image) and the result. Include the guard's run before the fix and after it, and the re-run of the original failing operation. List the checks that were not run, and the relevant paths left untested.

## 6. Unknowns and next step

Open questions, the SKIP and FAIL signals that matter, and the single most useful next step, with who needs to take it.

## Wording

- Use plain, precise words. Name files, functions, versions and times.
- Put one claim in each sentence where you can.
- Use "verified", "fixed" or "passes" only for checks you ran and whose output you saw. Otherwise write "not run" or "expected to pass, not checked".
- Never derive a "fixed", "resolved" or "all green" verdict from signal counts or statuses. An unavailable or irrelevant SKIP does not by itself prevent reporting a verified, bounded fix. State the scope you verified, and name the relevant untested paths and unresolved failures.
- Quote error text sparingly, and only sanitized.
- Leave out filler and reassurance.
