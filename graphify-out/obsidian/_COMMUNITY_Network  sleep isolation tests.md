---
type: community
cohesion: 0.48
members: 7
---

# Network / sleep isolation tests

**Cohesion:** 0.48 - moderately connected
**Members:** 7 nodes

## Members
- [[_f1_no_network()]] - code - scripts\test_pipeline.py
- [[_f1_no_sleep()]] - code - scripts\test_pipeline.py
- [[_f1_restore()]] - code - scripts\test_pipeline.py
- [[test_zzz_f1_fetch_all_still_reraises_a_programming_error()]] - code - scripts\test_pipeline.py
- [[test_zzz_f1_fetch_all_survives_a_non_positive_worker_setting()]] - code - scripts\test_pipeline.py
- [[test_zzz_f1_fetch_source_survives_a_non_positive_retry_setting()]] - code - scripts\test_pipeline.py
- [[test_zzz_f1_positive_retry_settings_are_not_altered_by_the_clamp()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Network_/_sleep_isolation_tests
SORT file.name ASC
```

## Connections to other communities
- 7 edges to [[_COMMUNITY_Test invariants (core suite)]]

## Top bridge nodes
- [[_f1_restore()]] - degree 5, connects to 1 community
- [[_f1_no_network()]] - degree 4, connects to 1 community
- [[_f1_no_sleep()]] - degree 4, connects to 1 community
- [[test_zzz_f1_fetch_all_survives_a_non_positive_worker_setting()]] - degree 4, connects to 1 community
- [[test_zzz_f1_fetch_source_survives_a_non_positive_retry_setting()]] - degree 4, connects to 1 community