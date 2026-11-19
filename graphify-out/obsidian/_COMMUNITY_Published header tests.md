---
type: community
cohesion: 0.20
members: 10
---

# Published header tests

**Cohesion:** 0.20 - loosely connected
**Members:** 10 nodes

## Members
- [[_hd_headers()]] - code - scripts\test_pipeline.py
- [[_hd_trim_prefix()]] - code - scripts\test_pipeline.py
- [[test_zzz_hdr_aggregate_writes_headers_into_txt_b64_yaml_but_not_json()]] - code - scripts\test_pipeline.py
- [[test_zzz_hdr_archive_files_never_get_a_profile_header()]] - code - scripts\test_pipeline.py
- [[test_zzz_hdr_block_has_exactly_the_five_documented_keys()]] - code - scripts\test_pipeline.py
- [[test_zzz_hdr_existing_comment_heads_are_inert_for_hiddify()]] - code - scripts\test_pipeline.py
- [[test_zzz_hdr_protocol_files_get_headers_labelled_by_protocol()]] - code - scripts\test_pipeline.py
- [[test_zzz_hdr_survives_the_29_line_scan_window_in_every_output()]] - code - scripts\test_pipeline.py
- [[test_zzz_hdr_total_and_expire_are_zero_meaning_unlimited()]] - code - scripts\test_pipeline.py
- [[test_zzz_hdr_values_are_what_hiddify_will_actually_show()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Published_header_tests
SORT file.name ASC
```

## Connections to other communities
- 10 edges to [[_COMMUNITY_Test invariants (core suite)]]
- 3 edges to [[_COMMUNITY_Header  bucket tests]]

## Top bridge nodes
- [[_hd_headers()]] - degree 11, connects to 2 communities
- [[test_zzz_hdr_aggregate_writes_headers_into_txt_b64_yaml_but_not_json()]] - degree 3, connects to 2 communities
- [[test_zzz_hdr_protocol_files_get_headers_labelled_by_protocol()]] - degree 3, connects to 2 communities
- [[_hd_trim_prefix()]] - degree 2, connects to 1 community
- [[test_zzz_hdr_archive_files_never_get_a_profile_header()]] - degree 2, connects to 1 community