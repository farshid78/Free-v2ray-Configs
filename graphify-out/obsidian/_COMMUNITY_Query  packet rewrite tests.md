---
type: community
cohesion: 0.11
members: 21
---

# Query / packet rewrite tests

**Cohesion:** 0.11 - loosely connected
**Members:** 21 nodes

## Members
- [[_j_query_of()]] - code - scripts\test_pipeline.py
- [[_j_vless()]] - code - scripts\test_pipeline.py
- [[_j_vmess()]] - code - scripts\test_pipeline.py
- [[_j_vmess_obj()]] - code - scripts\test_pipeline.py
- [[test_zz_j_alpn_and_extra_are_identity()]] - code - scripts\test_pipeline.py
- [[test_zz_j_alpn_same_value_still_collapses()]] - code - scripts\test_pipeline.py
- [[test_zz_j_amp_control_raw_line_really_is_broken()]] - code - scripts\test_pipeline.py
- [[test_zz_j_amp_entity_repaired_in_ingestion_funnel()]] - code - scripts\test_pipeline.py
- [[test_zz_j_amp_repair_is_idempotent_and_key_stable()]] - code - scripts\test_pipeline.py
- [[test_zz_j_amp_repair_precision_non_separator_untouched()]] - code - scripts\test_pipeline.py
- [[test_zz_j_case_insensitive_params_still_folded()]] - code - scripts\test_pipeline.py
- [[test_zz_j_case_sensitive_params_preserved()]] - code - scripts\test_pipeline.py
- [[test_zz_j_norm_type_deliberately_untouched()]] - code - scripts\test_pipeline.py
- [[test_zz_j_phase_f_h_i_gains_intact()]] - code - scripts\test_pipeline.py
- [[test_zz_j_type_default_symmetric_with_absence()]] - code - scripts\test_pipeline.py
- [[test_zz_j_type_real_transport_still_splits()]] - code - scripts\test_pipeline.py
- [[test_zz_j_vmess_alter_id_normalized_like_the_product()]] - code - scripts\test_pipeline.py
- [[test_zz_j_vmess_host_and_sni_no_longer_conflated()]] - code - scripts\test_pipeline.py
- [[test_zz_j_vmess_path_root_equivalent_but_trailing_slash_not()]] - code - scripts\test_pipeline.py
- [[test_zz_j_vmess_tls_auto_equals_absent()]] - code - scripts\test_pipeline.py
- [[test_zz_j_vmess_tls_real_values_still_split()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Query_/_packet_rewrite_tests
SORT file.name ASC
```

## Connections to other communities
- 21 edges to [[_COMMUNITY_Test invariants (core suite)]]
- 1 edge to [[_COMMUNITY_VMess  insecure-flag tests]]

## Top bridge nodes
- [[_j_vmess_obj()]] - degree 4, connects to 2 communities
- [[_j_vless()]] - degree 12, connects to 1 community
- [[_j_vmess()]] - degree 9, connects to 1 community
- [[_j_query_of()]] - degree 5, connects to 1 community
- [[test_zz_j_alpn_and_extra_are_identity()]] - degree 3, connects to 1 community