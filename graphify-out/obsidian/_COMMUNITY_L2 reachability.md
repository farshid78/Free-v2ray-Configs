---
type: community
cohesion: 0.24
members: 16
---

# L2 reachability

**Cohesion:** 0.24 - loosely connected
**Members:** 16 nodes

## Members
- [[FileDescriptorExhaustion]] - code - scripts\reachability.py
- [[_is_ip()]] - code - scripts\reachability.py
- [[_main()_3]] - code - scripts\reachability.py
- [[_probe()]] - code - scripts\reachability.py
- [[_probe_endpoint()]] - code - scripts\reachability.py
- [[_resolve_one()]] - code - scripts\reachability.py
- [[_run_tcp()]] - code - scripts\reachability.py
- [[_soft_nofile()]] - code - scripts\reachability.py
- [[check_endpoints()]] - code - scripts\reachability.py
- [[check_file()]] - code - scripts\reachability.py
- [[check_lines()]] - code - scripts\reachability.py
- [[fd_count()]] - code - scripts\reachability.py
- [[headroom_warning()]] - code - scripts\reachability.py
- [[reachability.py]] - code - scripts\reachability.py
- [[resolve_hosts()]] - code - scripts\reachability.py
- [[socket_fd_count()]] - code - scripts\reachability.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/L2_reachability
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Filters + L0L1 stage]]
- 1 edge to [[_COMMUNITY_Google-Ready layer & realtest]]
- 1 edge to [[_COMMUNITY_Test invariants (core suite)]]

## Top bridge nodes
- [[reachability.py]] - degree 17, connects to 2 communities
- [[FileDescriptorExhaustion]] - degree 3, connects to 1 community