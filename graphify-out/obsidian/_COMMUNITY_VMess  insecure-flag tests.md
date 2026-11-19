---
type: community
cohesion: 0.16
members: 18
---

# VMess / insecure-flag tests

**Cohesion:** 0.16 - loosely connected
**Members:** 18 nodes

## Members
- [[_k_emit()]] - code - scripts\test_pipeline.py
- [[_k_pair()]] - code - scripts\test_pipeline.py
- [[_k_vm()]] - code - scripts\test_pipeline.py
- [[test_zz_k_insecure_absent_equals_false()]] - code - scripts\test_pipeline.py
- [[test_zz_k_insecure_has_no_weight_where_it_is_never_emitted()]] - code - scripts\test_pipeline.py
- [[test_zz_k_insecure_is_identity_for_hysteria2_and_tuic()]] - code - scripts\test_pipeline.py
- [[test_zz_k_key_and_product_never_disagree()]] - code - scripts\test_pipeline.py
- [[test_zz_k_phase_hij_endpoint_marking_intact()]] - code - scripts\test_pipeline.py
- [[test_zz_k_srv_component_is_vmess_scoped_and_present()]] - code - scripts\test_pipeline.py
- [[test_zz_k_srv_is_deterministic_and_never_empty_key()]] - code - scripts\test_pipeline.py
- [[test_zz_k_vmess_garbage_sni_does_not_split()]] - code - scripts\test_pipeline.py
- [[test_zz_k_vmess_host_dominant_sni_still_splits()]] - code - scripts\test_pipeline.py
- [[test_zz_k_vmess_scy_absent_equals_auto()]] - code - scripts\test_pipeline.py
- [[test_zz_k_vmess_scy_case_preserved_like_the_product()]] - code - scripts\test_pipeline.py
- [[test_zz_k_vmess_scy_is_identity()]] - code - scripts\test_pipeline.py
- [[test_zz_k_vmess_sni_falls_back_to_host_like_the_product()]] - code - scripts\test_pipeline.py
- [[test_zz_k_vmess_sni_reaches_output_without_tls()]] - code - scripts\test_pipeline.py
- [[test_zz_k_vmess_two_different_snis_split()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/VMess_/_insecure-flag_tests
SORT file.name ASC
```

## Connections to other communities
- 18 edges to [[_COMMUNITY_Test invariants (core suite)]]
- 1 edge to [[_COMMUNITY_Query  packet rewrite tests]]

## Top bridge nodes
- [[_k_vm()]] - degree 14, connects to 2 communities
- [[_k_pair()]] - degree 14, connects to 1 community
- [[test_zz_k_key_and_product_never_disagree()]] - degree 3, connects to 1 community
- [[test_zz_k_vmess_garbage_sni_does_not_split()]] - degree 3, connects to 1 community
- [[test_zz_k_vmess_host_dominant_sni_still_splits()]] - degree 3, connects to 1 community