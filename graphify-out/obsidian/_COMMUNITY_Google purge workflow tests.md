---
type: community
cohesion: 0.25
members: 9
---

# Google purge workflow tests

**Cohesion:** 0.25 - loosely connected
**Members:** 9 nodes

## Members
- [[_gr_purge_script()]] - code - scripts\test_pipeline.py
- [[_gr_workflow()]] - code - scripts\test_pipeline.py
- [[_sync_step()]] - code - scripts\test_pipeline.py
- [[test_zzz_gr_purge_refreshes_cascade_mirrors_in_a_separate_request()]] - code - scripts\test_pipeline.py
- [[test_zzz_gr_workflow_publishes_and_classifies_google_as_output()]] - code - scripts\test_pipeline.py
- [[test_zzz_gr_workflow_runs_google_after_cascade_and_before_the_gate()]] - code - scripts\test_pipeline.py
- [[test_zzz_lkg_sync_output_paths_are_the_publish_steps_own()]] - code - scripts\test_pipeline.py
- [[test_zzz_lkg_sync_runs_after_the_gate_and_before_the_stash()]] - code - scripts\test_pipeline.py
- [[test_zzz_lkg_workflow_stashes_early_and_settles_always()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Google_purge_workflow_tests
SORT file.name ASC
```

## Connections to other communities
- 9 edges to [[_COMMUNITY_Test invariants (core suite)]]
- 2 edges to [[_COMMUNITY_Fake writer test doubles]]

## Top bridge nodes
- [[_gr_workflow()]] - degree 9, connects to 2 communities
- [[_sync_step()]] - degree 4, connects to 2 communities
- [[_gr_purge_script()]] - degree 3, connects to 1 community
- [[test_zzz_lkg_sync_output_paths_are_the_publish_steps_own()]] - degree 3, connects to 1 community
- [[test_zzz_gr_purge_refreshes_cascade_mirrors_in_a_separate_request()]] - degree 2, connects to 1 community