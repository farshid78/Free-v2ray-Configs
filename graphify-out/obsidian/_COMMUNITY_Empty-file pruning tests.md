---
type: community
cohesion: 0.67
members: 3
---

# Empty-file pruning tests

**Cohesion:** 0.67 - moderately connected
**Members:** 3 nodes

## Members
- [[_fresh_outdir()]] - code - scripts\test_pipeline.py
- [[test_duplicates_files_are_never_written_and_stale_ones_are_removed()]] - code - scripts\test_pipeline.py
- [[test_empty_protocol_never_publishes_a_file_and_prunes_both_members()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Empty-file_pruning_tests
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Test invariants (core suite)]]
- 1 edge to [[_COMMUNITY_Countries file tests]]

## Top bridge nodes
- [[_fresh_outdir()]] - degree 4, connects to 2 communities
- [[test_duplicates_files_are_never_written_and_stale_ones_are_removed()]] - degree 2, connects to 1 community
- [[test_empty_protocol_never_publishes_a_file_and_prunes_both_members()]] - degree 2, connects to 1 community