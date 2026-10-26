# Playbook: frontend

Use this playbook for UI errors, console errors, failed network calls, client state, rendering and browser-specific behaviour.

## Reproduce

- Record:
  - the browser and version
  - the device or viewport
  - the exact steps
  - the account type, using a synthetic account
  - feature flags
  - whether the failure survives a hard reload or a private window
- Use the console error or the failing network response as the `baseline`.

## Investigate

- `browser`: target the failing request, not the whole session. Append a sanitized summary of:
  - its network waterfall entry: method, path, status and timing phases such as queueing, waiting and download
  - the relevant request and response headers, with cookies, auth headers and tokens removed
  - the relevant console errors
  - the request ID, sanitized, so it can be matched to server logs and traces
- Separate request time from render time. A slow response can come from the network, an edge or CDN layer, or the origin server. Waterfall timings guide the investigation; they do not prove the cause. A fast response followed by slow rendering is a lead toward the client, not proof.
- Map minified frames back to source when source maps are available. Maps can be stale or mismatched with the deployed build, so a mapped frame is a lead, not a causal conclusion. Append the component or module as `code-surface`.
- Checklist:
  - API contract mismatch with the backend
  - undefined or optional data
  - race conditions and stale state
  - effects that run twice
  - hydration differences
  - caches, service workers or CDN serving old assets
  - CSS specificity and layout
- If the root cause is server-side, continue with `backend.md`.

## Fix, guard, verify

- Write a component or unit test that renders the failing state. Use an end-to-end test only when the bug needs a real browser.
- For purely visual bugs that no test can capture, describe the manual check. Report the fix as unverified until someone has performed that check.
