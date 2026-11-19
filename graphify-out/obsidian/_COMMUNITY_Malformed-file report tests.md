---
type: community
cohesion: 0.40
members: 5
---

# Malformed-file report tests

**Cohesion:** 0.40 - moderately connected
**Members:** 5 nodes

## Members
- [[_f4_tmp()]] - code - scripts\test_pipeline.py
- [[test_zzz_f4_a_malformed_file_becomes_a_reportable_fail_not_a_crash()]] - code - scripts\test_pipeline.py
- [[test_zzz_f4_healthy_documents_are_still_accepted_unchanged()]] - code - scripts\test_pipeline.py
- [[test_zzz_f4_structural_checks_never_raise_on_a_malformed_document()]] - code - scripts\test_pipeline.py
- [[test_zzz_f4_the_total_wrapper_is_the_last_resort_not_the_first()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Malformed-file_report_tests
SORT file.name ASC
```

## Connections to other communities
- 5 edges to [[_COMMUNITY_Test invariants (core suite)]]
- 1 edge to [[_COMMUNITY_Fake writer test doubles]]

## Top bridge nodes
- [[_f4_tmp()]] - degree 6, connects to 2 communities
- [[test_zzz_f4_a_malformed_file_becomes_a_reportable_fail_not_a_crash()]] - degree 2, connects to 1 community
- [[test_zzz_f4_healthy_documents_are_still_accepted_unchanged()]] - degree 2, connects to 1 community
- [[test_zzz_f4_structural_checks_never_raise_on_a_malformed_document()]] - degree 2, connects to 1 community
- [[test_zzz_f4_the_total_wrapper_is_the_last_resort_not_the_first()]] - degree 2, connects to 1 community