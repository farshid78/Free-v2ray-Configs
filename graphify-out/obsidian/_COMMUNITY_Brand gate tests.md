---
type: community
cohesion: 0.26
members: 12
---

# Brand gate tests

**Cohesion:** 0.26 - loosely connected
**Members:** 12 nodes

## Members
- [[.__enter__()_2]] - code - scripts\test_pipeline.py
- [[.__exit__()_2]] - code - scripts\test_pipeline.py
- [[.__init__()_6]] - code - scripts\test_pipeline.py
- [[_FgateBoom]] - code - scripts\test_pipeline.py
- [[_fgate_result()]] - code - scripts\test_pipeline.py
- [[_fgate_seed()]] - code - scripts\test_pipeline.py
- [[test_zzz_f8_a_later_successful_write_clears_the_failure_flag()]] - code - scripts\test_pipeline.py
- [[test_zzz_f8_converter_failure_is_machine_readable_in_health_json()]] - code - scripts\test_pipeline.py
- [[test_zzz_f8_converter_failure_prunes_the_stale_file_instead_of_republishing()]] - code - scripts\test_pipeline.py
- [[test_zzz_f9_build_index_is_byte_identical_on_the_healthy_path()]] - code - scripts\test_pipeline.py
- [[test_zzz_f9_build_index_never_advertises_a_pruned_converter_file()]] - code - scripts\test_pipeline.py
- [[test_zzz_f9_out_dir_none_stays_backward_compatible()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Brand_gate_tests
SORT file.name ASC
```

## Connections to other communities
- 9 edges to [[_COMMUNITY_Test invariants (core suite)]]

## Top bridge nodes
- [[_FgateBoom]] - degree 8, connects to 1 community
- [[_fgate_result()]] - degree 7, connects to 1 community
- [[_fgate_seed()]] - degree 5, connects to 1 community
- [[test_zzz_f8_a_later_successful_write_clears_the_failure_flag()]] - degree 4, connects to 1 community
- [[test_zzz_f8_converter_failure_is_machine_readable_in_health_json()]] - degree 4, connects to 1 community