---
type: community
cohesion: 0.67
members: 3
---

# VMess packet tests

**Cohesion:** 0.67 - moderately connected
**Members:** 3 nodes

## Members
- [[_hd_vmess()]] - code - scripts\test_pipeline.py
- [[_hd_vmess_obj()]] - code - scripts\test_pipeline.py
- [[test_zzz_hd_packet_encoding_vmess_uses_verbatim_json_key()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/VMess_packet_tests
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Test invariants (core suite)]]

## Top bridge nodes
- [[test_zzz_hd_packet_encoding_vmess_uses_verbatim_json_key()]] - degree 3, connects to 1 community
- [[_hd_vmess()]] - degree 2, connects to 1 community
- [[_hd_vmess_obj()]] - degree 2, connects to 1 community