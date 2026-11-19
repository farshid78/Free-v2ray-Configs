---
type: community
cohesion: 0.44
members: 11
---

# Reachability tests

**Cohesion:** 0.44 - moderately connected
**Members:** 11 nodes

## Members
- [[_patch_connect()]] - code - scripts\test_pipeline.py
- [[_patch_dns()]] - code - scripts\test_pipeline.py
- [[_unpatch()]] - code - scripts\test_pipeline.py
- [[test_reachability_closes_every_socket_it_opens()]] - code - scripts\test_pipeline.py
- [[test_reachability_distinguishes_refusal_from_timeout_and_dns_failure()]] - code - scripts\test_pipeline.py
- [[test_reachability_emfile_raises_instead_of_reporting_a_wrong_rate()]] - code - scripts\test_pipeline.py
- [[test_reachability_error_keys_are_always_present_even_at_zero()]] - code - scripts\test_pipeline.py
- [[test_reachability_maps_open_endpoints_back_to_every_config_line()]] - code - scripts\test_pipeline.py
- [[test_reachability_probes_up_to_the_address_cap_not_just_the_first()]] - code - scripts\test_pipeline.py
- [[test_reachability_raises_when_a_socket_is_left_open()]] - code - scripts\test_pipeline.py
- [[test_reachability_socket_leak_is_seen_even_when_total_fds_are_flat()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Reachability_tests
SORT file.name ASC
```

## Connections to other communities
- 11 edges to [[_COMMUNITY_Test invariants (core suite)]]

## Top bridge nodes
- [[_patch_connect()]] - degree 9, connects to 1 community
- [[_patch_dns()]] - degree 9, connects to 1 community
- [[_unpatch()]] - degree 9, connects to 1 community
- [[test_reachability_closes_every_socket_it_opens()]] - degree 4, connects to 1 community
- [[test_reachability_distinguishes_refusal_from_timeout_and_dns_failure()]] - degree 4, connects to 1 community