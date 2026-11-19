---
type: community
cohesion: 0.67
members: 3
---

# Filter order tests

**Cohesion:** 0.67 - moderately connected
**Members:** 3 nodes

## Members
- [[_vmess_link()]] - code - scripts\test_pipeline.py
- [[test_filters_checks_cheap_rules_before_expensive_ones()]] - code - scripts\test_pipeline.py
- [[test_filters_drops_unroutable_and_structurally_invalid_servers()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Filter_order_tests
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Test invariants (core suite)]]

## Top bridge nodes
- [[_vmess_link()]] - degree 3, connects to 1 community
- [[test_filters_checks_cheap_rules_before_expensive_ones()]] - degree 2, connects to 1 community
- [[test_filters_drops_unroutable_and_structurally_invalid_servers()]] - degree 2, connects to 1 community