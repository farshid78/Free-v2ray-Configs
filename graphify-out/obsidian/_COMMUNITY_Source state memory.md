---
type: community
cohesion: 0.32
members: 12
---

# Source state memory

**Cohesion:** 0.32 - loosely connected
**Members:** 12 nodes

## Members
- [[_clip()]] - code - scripts\state.py
- [[_now_iso()]] - code - scripts\state.py
- [[disable_candidates()]] - code - scripts\state.py
- [[disabled_urls()]] - code - scripts\state.py
- [[empty_state()]] - code - scripts\state.py
- [[load_state()]] - code - scripts\state.py
- [[mark_disabled()]] - code - scripts\state.py
- [[record_round()]] - code - scripts\state.py
- [[save_state()]] - code - scripts\state.py
- [[source_key()]] - code - scripts\state.py
- [[state.py]] - code - scripts\state.py
- [[summary()]] - code - scripts\state.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Source_state_memory
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Aggregate pipeline & sources]]
- 1 edge to [[_COMMUNITY_Test invariants (core suite)]]

## Top bridge nodes
- [[state.py]] - degree 13, connects to 2 communities