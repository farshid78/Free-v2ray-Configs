---
type: community
cohesion: 0.25
members: 8
---

# Packet encoding tests

**Cohesion:** 0.25 - loosely connected
**Members:** 8 nodes

## Members
- [[_hd_vless()]] - code - scripts\test_pipeline.py
- [[test_zzz_hd_packet_encoding_go_parsequery_skips_are_left_untouched()]] - code - scripts\test_pipeline.py
- [[test_zzz_hd_packet_encoding_is_identity_preserving_and_idempotent()]] - code - scripts\test_pipeline.py
- [[test_zzz_hd_packet_encoding_key_normalisation_matches_ray2sing()]] - code - scripts\test_pipeline.py
- [[test_zzz_hd_packet_encoding_none_is_stripped_from_vless()]] - code - scripts\test_pipeline.py
- [[test_zzz_hd_packet_encoding_repeated_keys_follow_go_join_semantics()]] - code - scripts\test_pipeline.py
- [[test_zzz_hd_packet_encoding_runs_inside_the_single_ingestion_point()]] - code - scripts\test_pipeline.py
- [[test_zzz_hd_packet_encoding_supported_values_are_preserved_byte_for_byte()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Packet_encoding_tests
SORT file.name ASC
```

## Connections to other communities
- 8 edges to [[_COMMUNITY_Test invariants (core suite)]]

## Top bridge nodes
- [[_hd_vless()]] - degree 8, connects to 1 community
- [[test_zzz_hd_packet_encoding_go_parsequery_skips_are_left_untouched()]] - degree 2, connects to 1 community
- [[test_zzz_hd_packet_encoding_is_identity_preserving_and_idempotent()]] - degree 2, connects to 1 community
- [[test_zzz_hd_packet_encoding_key_normalisation_matches_ray2sing()]] - degree 2, connects to 1 community
- [[test_zzz_hd_packet_encoding_none_is_stripped_from_vless()]] - degree 2, connects to 1 community