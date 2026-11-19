---
type: community
cohesion: 0.23
members: 18
---

# Subscription validation gate

**Cohesion:** 0.23 - loosely connected
**Members:** 18 nodes

## Members
- [[_api_get()]] - code - scripts\validate.py
- [[_classify_subscription()]] - code - scripts\validate.py
- [[_clean()]] - code - scripts\validate.py
- [[_find_binary()]] - code - scripts\validate.py
- [[_mihomo_relevant_lines()]] - code - scripts\validate.py
- [[_parse_provider_errors()]] - code - scripts\validate.py
- [[_run()_1]] - code - scripts\validate.py
- [[_structural_clash()]] - code - scripts\validate.py
- [[_structural_singbox()]] - code - scripts\validate.py
- [[_subscription_files()]] - code - scripts\validate.py
- [[_supported_lines()]] - code - scripts\validate.py
- [[_total_check()]] - code - scripts\validate.py
- [[check_clash()]] - code - scripts\validate.py
- [[check_singbox()]] - code - scripts\validate.py
- [[check_subscriptions()]] - code - scripts\validate.py
- [[main()_10]] - code - scripts\validate.py
- [[validate.py]] - code - scripts\validate.py
- [[validate_outputs()]] - code - scripts\validate.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Subscription_validation_gate
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Test invariants (core suite)]]

## Top bridge nodes
- [[validate.py]] - degree 18, connects to 1 community