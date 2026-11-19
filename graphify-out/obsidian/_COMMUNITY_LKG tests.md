---
type: community
cohesion: 0.27
members: 14
---

# LKG tests

**Cohesion:** 0.27 - loosely connected
**Members:** 14 nodes

## Members
- [[_lkg_aggregate()]] - code - scripts\test_pipeline.py
- [[_lkg_round()]] - code - scripts\test_pipeline.py
- [[_lkg_tree_md5()]] - code - scripts\test_pipeline.py
- [[test_zzz_lkg_a_failed_producer_never_wins_even_with_complete_looking_files()]] - code - scripts\test_pipeline.py
- [[test_zzz_lkg_cli_reports_state_and_escalates_after_a_day()]] - code - scripts\test_pipeline.py
- [[test_zzz_lkg_corrupt_index_and_health_never_block_the_file_restore()]] - code - scripts\test_pipeline.py
- [[test_zzz_lkg_failed_round_restores_previous_output_byte_for_byte()]] - code - scripts\test_pipeline.py
- [[test_zzz_lkg_first_run_failure_without_previous_output_does_not_crash()]] - code - scripts\test_pipeline.py
- [[test_zzz_lkg_fresh_round_keeps_fresh_output_and_stamps_it()]] - code - scripts\test_pipeline.py
- [[test_zzz_lkg_fresh_round_without_countries_keeps_the_previous_countries()]] - code - scripts\test_pipeline.py
- [[test_zzz_lkg_google_keeps_previous_tier_when_the_step_did_not_publish()]] - code - scripts\test_pipeline.py
- [[test_zzz_lkg_multi_round_simulation_never_loses_a_tier()]] - code - scripts\test_pipeline.py
- [[test_zzz_lkg_success_with_an_empty_list_is_not_fresh()]] - code - scripts\test_pipeline.py
- [[test_zzz_lkg_without_a_stash_the_previous_output_stays_and_is_dated()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/LKG_tests
SORT file.name ASC
```

## Connections to other communities
- 14 edges to [[_COMMUNITY_Test invariants (core suite)]]

## Top bridge nodes
- [[_lkg_round()]] - degree 11, connects to 1 community
- [[_lkg_aggregate()]] - degree 10, connects to 1 community
- [[_lkg_tree_md5()]] - degree 7, connects to 1 community
- [[test_zzz_lkg_a_failed_producer_never_wins_even_with_complete_looking_files()]] - degree 4, connects to 1 community
- [[test_zzz_lkg_failed_round_restores_previous_output_byte_for_byte()]] - degree 4, connects to 1 community