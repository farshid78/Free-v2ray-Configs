---
type: community
cohesion: 0.33
members: 6
---

# Freshness gate tests

**Cohesion:** 0.33 - loosely connected
**Members:** 6 nodes

## Members
- [[_f5_healthy_tree()]] - code - scripts\test_pipeline.py
- [[test_subscription_result_never_changes_the_existing_gate_verdict()]] - code - scripts\test_pipeline.py
- [[test_zzz_f5_a_run_that_proved_nothing_is_visible_not_silent()]] - code - scripts\test_pipeline.py
- [[test_zzz_f5_an_unrecognised_status_closes_the_gate()]] - code - scripts\test_pipeline.py
- [[test_zzz_f5_skipped_still_passes_because_that_is_the_documented_design()]] - code - scripts\test_pipeline.py
- [[test_zzz_f5_the_gate_is_an_allowlist_not_a_denylist()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Freshness_gate_tests
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_Test invariants (core suite)]]
- 1 edge to [[_COMMUNITY_Countries file tests]]
- 1 edge to [[_COMMUNITY_argv (F5) tests]]

## Top bridge nodes
- [[_f5_healthy_tree()]] - degree 7, connects to 2 communities
- [[test_subscription_result_never_changes_the_existing_gate_verdict()]] - degree 3, connects to 2 communities
- [[test_zzz_f5_a_run_that_proved_nothing_is_visible_not_silent()]] - degree 2, connects to 1 community
- [[test_zzz_f5_an_unrecognised_status_closes_the_gate()]] - degree 2, connects to 1 community
- [[test_zzz_f5_skipped_still_passes_because_that_is_the_documented_design()]] - degree 2, connects to 1 community