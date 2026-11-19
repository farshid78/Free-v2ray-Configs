---
type: community
cohesion: 0.22
members: 10
---

# Publish decision gate tests

**Cohesion:** 0.22 - loosely connected
**Members:** 10 nodes

## Members
- [[_f7_decision_block()]] - code - scripts\test_pipeline.py
- [[_f7_gate_step()]] - code - scripts\test_pipeline.py
- [[_f7_run_decision()]] - code - scripts\test_pipeline.py
- [[test_zzz_f7_a_future_timestamp_does_not_freeze_the_pipeline()]] - code - scripts\test_pipeline.py
- [[test_zzz_f7_a_healthy_age_is_judged_exactly_as_before()]] - code - scripts\test_pipeline.py
- [[test_zzz_f7_an_age_too_large_for_the_shell_still_opens_the_gate()]] - code - scripts\test_pipeline.py
- [[test_zzz_f7_an_unreadable_age_opens_the_gate_instead_of_skipping()]] - code - scripts\test_pipeline.py
- [[test_zzz_f7_an_unusable_threshold_also_opens_the_gate()]] - code - scripts\test_pipeline.py
- [[test_zzz_f7_the_gate_never_kills_the_job_and_says_why_out_loud()]] - code - scripts\test_pipeline.py
- [[test_zzz_f7_the_whole_gate_chain_agrees_with_a_real_index_json()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Publish_decision_gate_tests
SORT file.name ASC
```

## Connections to other communities
- 10 edges to [[_COMMUNITY_Test invariants (core suite)]]
- 1 edge to [[_COMMUNITY_CI  workflow-derived tests]]
- 1 edge to [[_COMMUNITY_Fake writer test doubles]]

## Top bridge nodes
- [[_f7_run_decision()]] - degree 9, connects to 2 communities
- [[_f7_gate_step()]] - degree 5, connects to 2 communities
- [[_f7_decision_block()]] - degree 3, connects to 1 community
- [[test_zzz_f7_the_gate_never_kills_the_job_and_says_why_out_loud()]] - degree 3, connects to 1 community
- [[test_zzz_f7_a_future_timestamp_does_not_freeze_the_pipeline()]] - degree 2, connects to 1 community