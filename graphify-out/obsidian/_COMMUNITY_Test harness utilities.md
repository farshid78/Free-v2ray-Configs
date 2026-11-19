---
type: community
cohesion: 0.21
members: 16
---

# Test harness utilities

**Cohesion:** 0.21 - loosely connected
**Members:** 16 nodes

## Members
- [[Exception]] - code
- [[_SkipTest]] - code - scripts\test_pipeline.py
- [[_bash()]] - code - scripts\test_pipeline.py
- [[_vc_fixture()]] - code - scripts\test_pipeline.py
- [[_vc_run()]] - code - scripts\test_pipeline.py
- [[_vc_sha_of()]] - code - scripts\test_pipeline.py
- [[_vc_steps()]] - code - scripts\test_pipeline.py
- [[_vc_urls()]] - code - scripts\test_pipeline.py
- [[test_zzz_vc_a_corrupt_cached_archive_is_replaced_and_marked_for_saving()]] - code - scripts\test_pipeline.py
- [[test_zzz_vc_a_failed_download_on_a_cold_cache_still_fails_closed()]] - code - scripts\test_pipeline.py
- [[test_zzz_vc_a_hung_download_is_cut_at_the_budget()]] - code - scripts\test_pipeline.py
- [[test_zzz_vc_a_tampered_download_is_rejected_and_never_reaches_the_cache()]] - code - scripts\test_pipeline.py
- [[test_zzz_vc_binary_digests_are_enforced_even_on_a_cache_hit()]] - code - scripts\test_pipeline.py
- [[test_zzz_vc_cold_cache_downloads_each_pinned_archive_once_and_keeps_both()]] - code - scripts\test_pipeline.py
- [[test_zzz_vc_downloads_use_the_measured_retry_policy()]] - code - scripts\test_pipeline.py
- [[test_zzz_vc_warm_cache_installs_with_the_network_down()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Test_harness_utilities
SORT file.name ASC
```

## Connections to other communities
- 16 edges to [[_COMMUNITY_Test invariants (core suite)]]
- 1 edge to [[_COMMUNITY_CI  workflow-derived tests]]

## Top bridge nodes
- [[_vc_steps()]] - degree 5, connects to 2 communities
- [[_vc_run()]] - degree 11, connects to 1 community
- [[_vc_fixture()]] - degree 10, connects to 1 community
- [[test_zzz_vc_a_corrupt_cached_archive_is_replaced_and_marked_for_saving()]] - degree 5, connects to 1 community
- [[test_zzz_vc_cold_cache_downloads_each_pinned_archive_once_and_keeps_both()]] - degree 5, connects to 1 community