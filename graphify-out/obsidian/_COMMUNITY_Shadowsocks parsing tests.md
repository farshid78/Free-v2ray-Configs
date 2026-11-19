---
type: community
cohesion: 0.11
members: 19
---

# Shadowsocks parsing tests

**Cohesion:** 0.11 - loosely connected
**Members:** 19 nodes

## Members
- [[_f_ss_key_old_algorithm()]] - code - scripts\test_pipeline.py
- [[_f_ss_parts()]] - code - scripts\test_pipeline.py
- [[test_zz_f_ss_2022_userinfo_with_slash_preserved()]] - code - scripts\test_pipeline.py
- [[test_zz_f_ss_at_in_query_does_not_destroy_endpoint()]] - code - scripts\test_pipeline.py
- [[test_zz_f_ss_base64_userinfo_decoded()]] - code - scripts\test_pipeline.py
- [[test_zz_f_ss_control_patch_is_falsifiable()]] - code - scripts\test_pipeline.py
- [[test_zz_f_ss_host_agrees_with_endpoint_of()]] - code - scripts\test_pipeline.py
- [[test_zz_f_ss_ipv6_bracketed()]] - code - scripts\test_pipeline.py
- [[test_zz_f_ss_last_at_is_the_delimiter()]] - code - scripts\test_pipeline.py
- [[test_zz_f_ss_no_query_semantics_unchanged()]] - code - scripts\test_pipeline.py
- [[test_zz_f_ss_note_tag_does_not_split_identity()]] - code - scripts\test_pipeline.py
- [[test_zz_f_ss_percent_encoded_userinfo()]] - code - scripts\test_pipeline.py
- [[test_zz_f_ss_plain_userinfo_kept()]] - code - scripts\test_pipeline.py
- [[test_zz_f_ss_query_presence_does_not_split_identity()]] - code - scripts\test_pipeline.py
- [[test_zz_f_ss_slash_before_query_port_clean()]] - code - scripts\test_pipeline.py
- [[test_zz_f_ss_two_at_in_query()]] - code - scripts\test_pipeline.py
- [[test_zz_f_ss_userinfo_spans_to_last_at()]] - code - scripts\test_pipeline.py
- [[test_zz_h_ss_branch_untouched()]] - code - scripts\test_pipeline.py
- [[test_zz_i_phase_h_and_f_gains_intact()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Shadowsocks_parsing_tests
SORT file.name ASC
```

## Connections to other communities
- 19 edges to [[_COMMUNITY_Test invariants (core suite)]]
- 2 edges to [[_COMMUNITY_Fronting  header tests]]

## Top bridge nodes
- [[test_zz_i_phase_h_and_f_gains_intact()]] - degree 4, connects to 2 communities
- [[_f_ss_parts()]] - degree 15, connects to 1 community
- [[_f_ss_key_old_algorithm()]] - degree 6, connects to 1 community
- [[test_zz_f_ss_control_patch_is_falsifiable()]] - degree 3, connects to 1 community
- [[test_zz_h_ss_branch_untouched()]] - degree 3, connects to 1 community