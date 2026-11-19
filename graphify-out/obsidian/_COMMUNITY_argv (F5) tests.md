---
type: community
cohesion: 0.40
members: 5
---

# argv (F5) tests

**Cohesion:** 0.40 - moderately connected
**Members:** 5 nodes

## Members
- [[.__enter__()_4]] - code - scripts\test_pipeline.py
- [[.__exit__()_4]] - code - scripts\test_pipeline.py
- [[.__init__()_7]] - code - scripts\test_pipeline.py
- [[_f5_argv]] - code - scripts\test_pipeline.py
- [[test_zzz_f5_the_strict_exit_code_is_what_ci_actually_gates_on()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/argv_(F5)_tests
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Test invariants (core suite)]]
- 1 edge to [[_COMMUNITY_Freshness gate tests]]

## Top bridge nodes
- [[test_zzz_f5_the_strict_exit_code_is_what_ci_actually_gates_on()]] - degree 3, connects to 2 communities
- [[_f5_argv]] - degree 5, connects to 1 community