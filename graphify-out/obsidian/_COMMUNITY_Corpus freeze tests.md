---
type: community
cohesion: 0.17
members: 16
---

# Corpus freeze tests

**Cohesion:** 0.17 - loosely connected
**Members:** 16 nodes

## Members
- [[_e4_corpus()]] - code - scripts\test_pipeline.py
- [[_e4_freeze_country()]] - code - scripts\test_pipeline.py
- [[_e4_remark_of()]] - code - scripts\test_pipeline.py
- [[_e6_sources()]] - code - scripts\test_pipeline.py
- [[test_a_node_can_never_shadow_a_group_name()]] - code - scripts\test_pipeline.py
- [[test_brand_remark_is_idempotent_over_the_adversarial_corpus()]] - code - scripts\test_pipeline.py
- [[test_branding_survives_every_adversarial_remark_in_the_text_outputs()]] - code - scripts\test_pipeline.py
- [[test_branding_survives_in_clash_and_singbox_for_the_adversarial_corpus()]] - code - scripts\test_pipeline.py
- [[test_converter_default_names_are_branded_not_bare_protocol()]] - code - scripts\test_pipeline.py
- [[test_every_output_group_name_carries_the_brand()]] - code - scripts\test_pipeline.py
- [[test_health_report_attributes_converter_drops_to_the_right_category()]] - code - scripts\test_pipeline.py
- [[test_is_branded_reads_the_remark_the_user_actually_sees()]] - code - scripts\test_pipeline.py
- [[test_no_group_reference_is_left_dangling()]] - code - scripts\test_pipeline.py
- [[test_the_publish_gate_drops_unbranded_lines_instead_of_publishing_them()]] - code - scripts\test_pipeline.py
- [[test_zz_c12_shared_adversarial_corpus_stayed_untouched()]] - code - scripts\test_pipeline.py
- [[test_zz_o4_other_schemes_are_byte_identically_untouched()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Corpus_freeze_tests
SORT file.name ASC
```

## Connections to other communities
- 16 edges to [[_COMMUNITY_Test invariants (core suite)]]
- 1 edge to [[_COMMUNITY_Converter tests (Clash, SSR)]]

## Top bridge nodes
- [[test_zz_c12_shared_adversarial_corpus_stayed_untouched()]] - degree 3, connects to 2 communities
- [[_e4_corpus()]] - degree 13, connects to 1 community
- [[_e4_freeze_country()]] - degree 8, connects to 1 community
- [[test_brand_remark_is_idempotent_over_the_adversarial_corpus()]] - degree 4, connects to 1 community
- [[test_the_publish_gate_drops_unbranded_lines_instead_of_publishing_them()]] - degree 4, connects to 1 community