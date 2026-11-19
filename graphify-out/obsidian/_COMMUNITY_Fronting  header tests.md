---
type: community
cohesion: 0.09
members: 37
---

# Fronting / header tests

**Cohesion:** 0.09 - loosely connected
**Members:** 37 nodes

## Members
- [[_h_old_fronting_generic()]] - code - scripts\test_pipeline.py
- [[_h_parts()]] - code - scripts\test_pipeline.py
- [[_h_vless()]] - code - scripts\test_pipeline.py
- [[_h_vmess()]] - code - scripts\test_pipeline.py
- [[_h_vmess_parts()]] - code - scripts\test_pipeline.py
- [[_i_old_key_generic()]] - code - scripts\test_pipeline.py
- [[_i_old_key_vmess()]] - code - scripts\test_pipeline.py
- [[_i_vless()]] - code - scripts\test_pipeline.py
- [[test_zz_h_control_old_algorithm_gave_different_result()]] - code - scripts\test_pipeline.py
- [[test_zz_h_dedup_key_is_deterministic()]] - code - scripts\test_pipeline.py
- [[test_zz_h_garbage_fronting_rejected_and_popped()]] - code - scripts\test_pipeline.py
- [[test_zz_h_host_param_unchanged_by_tls_rule()]] - code - scripts\test_pipeline.py
- [[test_zz_h_ipv6_literal_fronting_accepted()]] - code - scripts\test_pipeline.py
- [[test_zz_h_kept_host_agrees_with_endpoint_of()]] - code - scripts\test_pipeline.py
- [[test_zz_h_other_identity_params_preserved()]] - code - scripts\test_pipeline.py
- [[test_zz_h_other_schemes_follow_same_rule()]] - code - scripts\test_pipeline.py
- [[test_zz_h_reality_sni_keeps_real_host()]] - code - scripts\test_pipeline.py
- [[test_zz_h_reality_sni_two_servers_stay_distinct()]] - code - scripts\test_pipeline.py
- [[test_zz_h_remark_does_not_affect_key()]] - code - scripts\test_pipeline.py
- [[test_zz_h_security_absent_sni_keeps_real_host()]] - code - scripts\test_pipeline.py
- [[test_zz_h_security_none_sni_keeps_real_host()]] - code - scripts\test_pipeline.py
- [[test_zz_h_single_label_fronting_rejected()]] - code - scripts\test_pipeline.py
- [[test_zz_h_tls_valid_sni_key_unchanged()]] - code - scripts\test_pipeline.py
- [[test_zz_h_trailing_dot_fqdn_accepted()]] - code - scripts\test_pipeline.py
- [[test_zz_h_vmess_garbage_host_falls_back_to_add()]] - code - scripts\test_pipeline.py
- [[test_zz_h_vmess_host_kept_without_tls()]] - code - scripts\test_pipeline.py
- [[test_zz_h_vmess_invalid_host_valid_sni_shifts_to_sni()]] - code - scripts\test_pipeline.py
- [[test_zz_h_vmess_reality_sni_keeps_add()]] - code - scripts\test_pipeline.py
- [[test_zz_h_vmess_tls_valid_sni_unchanged()]] - code - scripts\test_pipeline.py
- [[test_zz_i_cdn_clean_ip_diversity_preserved()]] - code - scripts\test_pipeline.py
- [[test_zz_i_control_old_rule_merged_them_all_schemes()]] - code - scripts\test_pipeline.py
- [[test_zz_i_fronting_does_not_replace_real_host()]] - code - scripts\test_pipeline.py
- [[test_zz_i_loser_fronting_value_retained()]] - code - scripts\test_pipeline.py
- [[test_zz_i_patch_scope_no_fronting_unchanged()]] - code - scripts\test_pipeline.py
- [[test_zz_i_port_and_credential_still_distinguish()]] - code - scripts\test_pipeline.py
- [[test_zz_i_true_duplicates_still_collapse()]] - code - scripts\test_pipeline.py
- [[test_zz_i_vmess_add_retained()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Fronting_/_header_tests
SORT file.name ASC
```

## Connections to other communities
- 37 edges to [[_COMMUNITY_Test invariants (core suite)]]
- 2 edges to [[_COMMUNITY_Shadowsocks parsing tests]]

## Top bridge nodes
- [[_h_parts()]] - degree 19, connects to 2 communities
- [[_h_vless()]] - degree 16, connects to 2 communities
- [[_h_vmess()]] - degree 9, connects to 1 community
- [[_h_vmess_parts()]] - degree 8, connects to 1 community
- [[_i_old_key_generic()]] - degree 7, connects to 1 community