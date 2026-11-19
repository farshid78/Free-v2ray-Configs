---
type: community
cohesion: 0.67
members: 3
---

# Control-byte tests

**Cohesion:** 0.67 - moderately connected
**Members:** 3 nodes

## Members
- [[_p2_has_ctrl()]] - code - scripts\test_pipeline.py
- [[test_zzz_p2_extract_valid_lines_never_emits_a_control_byte()]] - code - scripts\test_pipeline.py
- [[test_zzz_p2_the_measured_corpus_line_is_repaired_without_losing_anything()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Control-byte_tests
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Test invariants (core suite)]]

## Top bridge nodes
- [[_p2_has_ctrl()]] - degree 3, connects to 1 community
- [[test_zzz_p2_extract_valid_lines_never_emits_a_control_byte()]] - degree 2, connects to 1 community
- [[test_zzz_p2_the_measured_corpus_line_is_repaired_without_losing_anything()]] - degree 2, connects to 1 community