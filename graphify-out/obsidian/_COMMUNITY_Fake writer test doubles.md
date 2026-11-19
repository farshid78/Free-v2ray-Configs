---
type: community
cohesion: 0.20
members: 17
---

# Fake writer test doubles

**Cohesion:** 0.20 - loosely connected
**Members:** 17 nodes

## Members
- [[.__init__()_3]] - code - scripts\test_pipeline.py
- [[.close()]] - code - scripts\test_pipeline.py
- [[.wait_closed()]] - code - scripts\test_pipeline.py
- [[_FakeWriter]] - code - scripts\test_pipeline.py
- [[_sync_env()]] - code - scripts\test_pipeline.py
- [[_sync_fixture()]] - code - scripts\test_pipeline.py
- [[_sync_git()]] - code - scripts\test_pipeline.py
- [[_sync_read()]] - code - scripts\test_pipeline.py
- [[_sync_run()]] - code - scripts\test_pipeline.py
- [[_sync_write()]] - code - scripts\test_pipeline.py
- [[test_reachability_socket_counter_ignores_non_socket_descriptors()]] - code - scripts\test_pipeline.py
- [[test_zzz_gr_geo_probe_cleans_up_its_inbound_process()]] - code - scripts\test_pipeline.py
- [[test_zzz_lkg_sync_brings_a_queued_checkout_to_the_newest_publish()]] - code - scripts\test_pipeline.py
- [[test_zzz_lkg_sync_fails_open_when_the_fetch_fails()]] - code - scripts\test_pipeline.py
- [[test_zzz_lkg_sync_fails_the_job_when_the_reset_fails()]] - code - scripts\test_pipeline.py
- [[test_zzz_lkg_sync_is_a_no_op_when_the_run_was_not_queued()]] - code - scripts\test_pipeline.py
- [[test_zzz_lkg_sync_keeps_the_checkout_when_the_source_changed()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Fake_writer_test_doubles
SORT file.name ASC
```

## Connections to other communities
- 14 edges to [[_COMMUNITY_Test invariants (core suite)]]
- 2 edges to [[_COMMUNITY_Google purge workflow tests]]
- 1 edge to [[_COMMUNITY_Malformed-file report tests]]
- 1 edge to [[_COMMUNITY_Publish decision gate tests]]

## Top bridge nodes
- [[_sync_run()]] - degree 9, connects to 2 communities
- [[.close()]] - degree 6, connects to 2 communities
- [[_sync_fixture()]] - degree 8, connects to 1 community
- [[_sync_git()]] - degree 7, connects to 1 community
- [[test_zzz_lkg_sync_brings_a_queued_checkout_to_the_newest_publish()]] - degree 5, connects to 1 community