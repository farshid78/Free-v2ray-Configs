---
type: community
cohesion: 0.22
members: 15
---

# Pipeline L3 stubs

**Cohesion:** 0.22 - loosely connected
**Members:** 15 nodes

## Members
- [[.__enter__()_1]] - code - scripts\test_pipeline.py
- [[.__exit__()_1]] - code - scripts\test_pipeline.py
- [[.__init__()_5]] - code - scripts\test_pipeline.py
- [[_StubL3]] - code - scripts\test_pipeline.py
- [[_pl_row()]] - code - scripts\test_pipeline.py
- [[test_pipeline_broken_rows_never_become_stable()]] - code - scripts\test_pipeline.py
- [[test_pipeline_fast_uses_the_median_not_a_single_run()]] - code - scripts\test_pipeline.py
- [[test_pipeline_matches_the_real_l3_result_contract()]] - code - scripts\test_pipeline.py
- [[test_pipeline_one_bad_round_cannot_be_ignored()]] - code - scripts\test_pipeline.py
- [[test_pipeline_output_survives_the_publication_gate()]] - code - scripts\test_pipeline.py
- [[test_pipeline_reports_every_layer_with_input_output_time_and_reasons()]] - code - scripts\test_pipeline.py
- [[test_pipeline_stable_requires_success_in_every_round()]] - code - scripts\test_pipeline.py
- [[test_pipeline_top_file_is_sorted_and_never_padded()]] - code - scripts\test_pipeline.py
- [[test_pipeline_verified_never_holds_a_failed_config()]] - code - scripts\test_pipeline.py
- [[test_pipeline_writes_files_with_an_honest_shortfall_notice()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Pipeline_L3_stubs
SORT file.name ASC
```

## Connections to other communities
- 12 edges to [[_COMMUNITY_Test invariants (core suite)]]
- 2 edges to [[_COMMUNITY_Countries file tests]]

## Top bridge nodes
- [[test_pipeline_output_survives_the_publication_gate()]] - degree 4, connects to 2 communities
- [[test_pipeline_writes_files_with_an_honest_shortfall_notice()]] - degree 4, connects to 2 communities
- [[_StubL3]] - degree 14, connects to 1 community
- [[_pl_row()]] - degree 11, connects to 1 community
- [[test_pipeline_broken_rows_never_become_stable()]] - degree 3, connects to 1 community