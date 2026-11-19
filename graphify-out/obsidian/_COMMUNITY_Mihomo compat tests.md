---
type: community
cohesion: 0.40
members: 5
---

# Mihomo compat tests

**Cohesion:** 0.40 - moderately connected
**Members:** 5 nodes

## Members
- [[_mc_b64()]] - code - scripts\test_pipeline.py
- [[test_mihomo_fatal_lines_never_reach_the_published_text_outputs()]] - code - scripts\test_pipeline.py
- [[test_ss_at_sign_in_query_no_longer_destroys_the_endpoint()]] - code - scripts\test_pipeline.py
- [[test_ss_plugin_that_no_client_can_run_drops_the_node()]] - code - scripts\test_pipeline.py
- [[test_ss_port_followed_by_a_slash_is_parsed()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Mihomo_compat_tests
SORT file.name ASC
```

## Connections to other communities
- 5 edges to [[_COMMUNITY_Test invariants (core suite)]]

## Top bridge nodes
- [[_mc_b64()]] - degree 5, connects to 1 community
- [[test_mihomo_fatal_lines_never_reach_the_published_text_outputs()]] - degree 2, connects to 1 community
- [[test_ss_at_sign_in_query_no_longer_destroys_the_endpoint()]] - degree 2, connects to 1 community
- [[test_ss_plugin_that_no_client_can_run_drops_the_node()]] - degree 2, connects to 1 community
- [[test_ss_port_followed_by_a_slash_is_parsed()]] - degree 2, connects to 1 community