---
type: community
cohesion: 0.29
members: 10
---

# Clash / sing-box naming tests

**Cohesion:** 0.29 - loosely connected
**Members:** 10 nodes

## Members
- [[_c12_clash_names()]] - code - scripts\test_pipeline.py
- [[_c12_freeze()]] - code - scripts\test_pipeline.py
- [[_c12_singbox_tags()]] - code - scripts\test_pipeline.py
- [[_c12_vmess()]] - code - scripts\test_pipeline.py
- [[test_zz_c12_enforce_brand_rebrands_the_final_name_and_never_drops()]] - code - scripts\test_pipeline.py
- [[test_zz_c12_mutant_vmess_is_branded_in_clash_and_singbox()]] - code - scripts\test_pipeline.py
- [[test_zz_c12_the_gate_and_the_output_name_disagreed_before_the_fix()]] - code - scripts\test_pipeline.py
- [[test_zz_c12_the_two_decoders_diverge_and_that_is_the_root_cause()]] - code - scripts\test_pipeline.py
- [[test_zz_c12_vmess_fragment_edge_cases_fall_back_instead_of_emptying()]] - code - scripts\test_pipeline.py
- [[test_zz_c12_vmess_name_precedence_is_fragment_then_ps_then_fallback()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Clash_/_sing-box_naming_tests
SORT file.name ASC
```

## Connections to other communities
- 10 edges to [[_COMMUNITY_Test invariants (core suite)]]

## Top bridge nodes
- [[_c12_vmess()]] - degree 7, connects to 1 community
- [[test_zz_c12_enforce_brand_rebrands_the_final_name_and_never_drops()]] - degree 5, connects to 1 community
- [[test_zz_c12_mutant_vmess_is_branded_in_clash_and_singbox()]] - degree 5, connects to 1 community
- [[_c12_freeze()]] - degree 4, connects to 1 community
- [[_c12_clash_names()]] - degree 3, connects to 1 community