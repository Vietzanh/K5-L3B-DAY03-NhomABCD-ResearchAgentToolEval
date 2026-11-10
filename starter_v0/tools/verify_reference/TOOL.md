---
name: verify_reference
track: bonus
kind: live_api
provider: Crossref
requires_env: []
inputs: [reference]
outputs: [found, match_type, items]
side_effect: false
---
# verify_reference

Checks Crossref's public scholarly metadata registry for a DOI or publication title. Use it when the user asks whether a scholarly reference has a Crossref record or wants citation metadata. A DOI is looked up directly; a title returns possible matches that should be verified against the authors and title before citing.

This confirms only whether Crossref returned a record; it does not prove that the full text is accessible, validate the work's scientific claims, or guarantee that a title-search result is the intended publication. Use `papers` for arXiv discovery and `fetch` when the user provides a URL whose content should be read.
