# Provenance

## Origin

OC Debug is **adapted conceptually from OCPM Debug**, an internal debugging tool.

Concepts carried over from OCPM Debug:

- The evidence-driven workflow: reproduce, classify, investigate, fix, guard, verify.
- The rule that an explicit investigation first loads the skill, the findings schema, the collector and renderer, and the relevant playbook.
- Findings records with the fields `signal`, `status`, `proof_of_work`, `correlation_id`, `logfile` and `detail`, and the PASS/SKIP/FAIL status pairs.

## Implementation

The original is a shell/jq implementation, coupled to an unrelated spec and commit framework.

- This package reimplements only a small, generic core, as new code using the Python standard library.
- The surrounding framework is not reproduced.
- The original's internal paths and examples are not reproduced.

## Examples and data

- All examples are synthetic. Names such as `example-shop` and `demo-0001` are invented.
- The package contains no client data, client names, internal URLs, credentials, reports, ticket numbers or author identities.

## Rights and licensing

- The licensing of OCPM Debug is unknown.
- Ownership and permission must be confirmed before any release:
  - who owns the original concepts
  - who owns this package
  - whether an adaptation may be published
- This package contains no LICENSE file and grants no licence.
- Nothing here relicenses OCPM Debug or any part of it.

## Recommendation (not a grant)

Once ownership is confirmed, the rights holder may consider the MIT licence for the portions of this package that they own and that are original to it. Any part derived from OCPM Debug requires a decision by the rights holder of OCPM Debug.

## Runtime and third-party attribution review

The package uses only Python standard-library APIs and vendors no third-party library source. The Docker base image includes CPython and Debian components under their respective upstream licences. Those licences are not replaced by a future project licence. Before distributing a built image, inventory the pinned base image and preserve its applicable notices; no container attribution audit has yet run. Claude Opus 5.5 authored the initial files from a sanitized conceptual brief; coordinator review made small packaging/documentation adjustments. AI authorship does not establish rights to the source adaptation.
