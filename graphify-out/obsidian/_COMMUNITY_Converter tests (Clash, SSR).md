---
type: community
cohesion: 0.07
members: 35
---

# Converter tests (Clash, SSR)

**Cohesion:** 0.07 - loosely connected
**Members:** 35 nodes

## Members
- [[_c11_b64()]] - code - scripts\test_pipeline.py
- [[_c11_clash()]] - code - scripts\test_pipeline.py
- [[_c11_ssr()]] - code - scripts\test_pipeline.py
- [[_o4_valid()]] - code - scripts\test_pipeline.py
- [[test_zz_c11_group_name_collision_gets_suffix()]] - code - scripts\test_pipeline.py
- [[test_zz_c11_ssr_accepts_base64url_and_missing_padding()]] - code - scripts\test_pipeline.py
- [[test_zz_c11_ssr_aead_ciphers_are_rejected_even_though_ss_allows_them()]] - code - scripts\test_pipeline.py
- [[test_zz_c11_ssr_build_is_deterministic()]] - code - scripts\test_pipeline.py
- [[test_zz_c11_ssr_case_is_normalised_like_mihomo_needs()]] - code - scripts\test_pipeline.py
- [[test_zz_c11_ssr_different_password_never_merges()]] - code - scripts\test_pipeline.py
- [[test_zz_c11_ssr_empty_decoded_password_is_rejected()]] - code - scripts\test_pipeline.py
- [[test_zz_c11_ssr_is_not_expressible_in_clash_but_stays_fully_parsed()]] - code - scripts\test_pipeline.py
- [[test_zz_c11_ssr_mixed_input_keeps_neighbours_intact()]] - code - scripts\test_pipeline.py
- [[test_zz_c11_ssr_must_never_appear_in_singbox()]] - code - scripts\test_pipeline.py
- [[test_zz_c11_ssr_name_comes_from_fragment_then_brand_fallback()]] - code - scripts\test_pipeline.py
- [[test_zz_c11_ssr_optional_params_are_omitted_not_emptied()]] - code - scripts\test_pipeline.py
- [[test_zz_c11_ssr_parses_with_and_without_query()]] - code - scripts\test_pipeline.py
- [[test_zz_c11_ssr_password_with_invalid_utf8_is_dropped_not_mangled()]] - code - scripts\test_pipeline.py
- [[test_zz_c11_ssr_port_and_password_gates()]] - code - scripts\test_pipeline.py
- [[test_zz_c11_ssr_rejects_malformed_body()]] - code - scripts\test_pipeline.py
- [[test_zz_c11_ssr_rejects_values_outside_registry()]] - code - scripts\test_pipeline.py
- [[test_zz_c11_ssr_server_gates_are_recorded_not_silent()]] - code - scripts\test_pipeline.py
- [[test_zz_o4_core_and_converters_never_diverge_on_host_and_port()]] - code - scripts\test_pipeline.py
- [[test_zz_o4_decoder_strictness_mirrors_the_converter_in_both_directions()]] - code - scripts\test_pipeline.py
- [[test_zz_o4_dedup_key_is_structural_not_the_base64_blob()]] - code - scripts\test_pipeline.py
- [[test_zz_o4_endpoint_of_returns_the_real_host_and_matches_the_converter()]] - code - scripts\test_pipeline.py
- [[test_zz_o4_every_identity_bearing_field_splits_the_key()]] - code - scripts\test_pipeline.py
- [[test_zz_o4_fragment_and_inner_remarks_and_group_never_shift_the_key()]] - code - scripts\test_pipeline.py
- [[test_zz_o4_host_and_method_case_folds_but_password_does_not()]] - code - scripts\test_pipeline.py
- [[test_zz_o4_key_is_injective_under_delimiter_bearing_values()]] - code - scripts\test_pipeline.py
- [[test_zz_o4_malformed_ssr_falls_back_without_raising_or_merging()]] - code - scripts\test_pipeline.py
- [[test_zz_o4_obfs_and_protocol_params_are_distinguished_from_each_other()]] - code - scripts\test_pipeline.py
- [[test_zz_o4_padding_and_alphabet_variants_share_exactly_one_key()]] - code - scripts\test_pipeline.py
- [[test_zz_o4_stable_label_is_deterministic_and_tracks_identity()]] - code - scripts\test_pipeline.py
- [[test_zz_o4_the_measured_duplicate_family_collapses_to_one_key()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Converter_tests_(Clash,_SSR)
SORT file.name ASC
```

## Connections to other communities
- 35 edges to [[_COMMUNITY_Test invariants (core suite)]]
- 1 edge to [[_COMMUNITY_Corpus freeze tests]]

## Top bridge nodes
- [[_c11_ssr()]] - degree 25, connects to 2 communities
- [[_o4_valid()]] - degree 14, connects to 1 community
- [[_c11_b64()]] - degree 6, connects to 1 community
- [[_c11_clash()]] - degree 6, connects to 1 community
- [[test_zz_o4_fragment_and_inner_remarks_and_group_never_shift_the_key()]] - degree 4, connects to 1 community