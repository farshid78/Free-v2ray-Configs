# Graph Report - .  (2026-11-19)

## Corpus Check
- Large corpus: 155 files · ~546,972 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder, or use --no-semantic to run AST-only.

## Summary
- 1218 nodes · 2509 edges · 52 communities detected
- Extraction: 50% EXTRACTED · 50% INFERRED · 0% AMBIGUOUS · INFERRED: 1251 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `_tmpdir()` - 45 edges
2. `_c11_ssr()` - 25 edges
3. `_cty_line()` - 24 edges
4. `t()` - 23 edges
5. `updateHub()` - 19 edges
6. `_h_parts()` - 19 edges
7. `_workflow_text()` - 18 edges
8. `num()` - 16 edges
9. `parse_proxy()` - 16 edges
10. `_h_vless()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `dedup_key()` --calls--> `ValueError`  [INFERRED]
  scripts\core.py →   _Bridges community 5 → community 3_
- `_fresh_outdir()` --calls--> `_tmpdir()`  [INFERRED]
  scripts\test_pipeline.py → scripts\test_pipeline.py  _Bridges community 2 → community 47_
- `test_pipeline_writes_files_with_an_honest_shortfall_notice()` --calls--> `_tmpdir()`  [INFERRED]
  scripts\test_pipeline.py → scripts\test_pipeline.py  _Bridges community 2 → community 27_
- `test_subscription_result_never_changes_the_existing_gate_verdict()` --calls--> `_tmpdir()`  [INFERRED]
  scripts\test_pipeline.py → scripts\test_pipeline.py  _Bridges community 2 → community 40_
- `_f7_gate_step()` --calls--> `_workflow_text()`  [INFERRED]
  scripts\test_pipeline.py → scripts\test_pipeline.py  _Bridges community 12 → community 35_

## Communities

### Community 0 - "Test invariants (core suite)"
Cohesion: 0.01
Nodes (6): _j_old_norm_identity_value(), _sb_proxy(), test_clash_uses_hyphenated_keys_and_singbox_uses_nested_objects(), test_zz_j_control_old_rules_really_differed(), test_zzz_vc_validator_archives_are_cached_under_a_key_that_carries_every_pin(), _vc_key_problems()

### Community 1 - "Dashboard client app.js"
Cohesion: 0.11
Nodes (64): appLink(), applyFilters(), b64decode(), clear(), configRow(), copyText(), copyWithFeedback(), countBy() (+56 more)

### Community 2 - "Countries file tests"
Cohesion: 0.06
Nodes (56): _cty_config_lines(), _cty_filename_for(), _cty_header_count(), _cty_line(), _cty_read(), _cty_scheme_line(), _f3_fake_xray_knife(), _f3_input_file() (+48 more)

### Community 3 - "Google-Ready layer & realtest"
Cohesion: 0.07
Nodes (46): classify_rounds(), _curl_fetch(), default_geo(), default_round(), _dump_json(), geo_phase(), geo_probe(), _header() (+38 more)

### Community 4 - "Clash / sing-box converters"
Cohesion: 0.1
Nodes (37): _alpn_list(), _b64_json(), _branded_fallback(), build_clash_yaml(), build_singbox_json(), _clash_dumper(), _clash_network(), _clash_transport_opts() (+29 more)

### Community 5 - "Config core (brand, dedup, extract)"
Cohesion: 0.09
Nodes (38): assert_no_control_bytes(), brand_remark(), ControlByteInOutput, country_for_endpoint(), decode_base64_text(), dedup_key(), detect_country_from_remark(), encode_base64_subscription() (+30 more)

### Community 6 - "Telegram bot handlers & DB"
Cohesion: 0.08
Nodes (21): adm_addsource(), adm_addsource_cat(), adm_broadcast(), adm_removesource(), adm_removesource_do(), adm_sources(), adm_stats(), adm_trigger() (+13 more)

### Community 7 - "Dashboard UI components"
Cohesion: 0.05
Nodes (10): bits.tsx, getJSON(), timeoutSignal(), fin(), n0(), input.tsx, sections.tsx, tabs.tsx (+2 more)

### Community 8 - "Aggregate pipeline & sources"
Cohesion: 0.12
Nodes (32): advance_memory(), build_health_report(), build_index(), CategoryResult, disabled_reasons_for(), fetch_all(), fetch_source(), log() (+24 more)

### Community 9 - "Fronting / header tests"
Cohesion: 0.09
Nodes (37): _h_old_fronting_generic(), _h_parts(), _h_vless(), _h_vmess(), _h_vmess_parts(), _i_old_key_generic(), _i_old_key_vmess(), _i_vless() (+29 more)

### Community 10 - "Converter tests (Clash, SSR)"
Cohesion: 0.07
Nodes (35): _c11_b64(), _c11_clash(), _c11_ssr(), _o4_valid(), test_zz_c11_group_name_collision_gets_suffix(), test_zz_c11_ssr_accepts_base64url_and_missing_padding(), test_zz_c11_ssr_aead_ciphers_are_rejected_even_though_ss_allows_them(), test_zz_c11_ssr_build_is_deterministic() (+27 more)

### Community 11 - "Brand config & renderers"
Cohesion: 0.13
Nodes (32): _compute(), github_env(), main(), _percent_encoded(), refresh(), render(), render_all(), render_dashboard_ts() (+24 more)

### Community 12 - "CI / workflow-derived tests"
Cohesion: 0.07
Nodes (32): _c1b_cache_actions(), _c1b_geoip_steps(), _is_sha_pin(), _p3_download_steps(), _p3_is_sha256(), _summary_cascade_snippet(), test_every_workflow_action_is_pinned_to_an_immutable_commit_sha(), test_workflow_caches_xray_knife_keyed_by_its_checksum() (+24 more)

### Community 13 - "GeoIP country grouping"
Cohesion: 0.15
Nodes (29): country_code_of(), _float_env(), group_by_country(), header_for(), _host_of(), _int_env(), is_safe_slug(), log() (+21 more)

### Community 14 - "xray-knife fake-shim tests"
Cohesion: 0.11
Nodes (25): _FakeXk, _gr_ep(), _gr_geo(), _gr_rounds(), _gr_tree(), _l3_csv(), _l3_row(), test_realtest_deletes_a_stale_output_before_running() (+17 more)

### Community 15 - "Asset generation"
Cohesion: 0.2
Nodes (26): card(), cards(), divider(), donate_qrs(), hero(), main(), pipeline(), qr_card() (+18 more)

### Community 16 - "Filters + L0/L1 stage"
Cohesion: 0.15
Nodes (24): classify(), endpoint_of_proxy(), filter_file(), filter_lines(), is_invalid_port(), is_invalid_uuid(), build_buckets(), declares_insecure() (+16 more)

### Community 17 - "Query / packet rewrite tests"
Cohesion: 0.11
Nodes (21): _j_query_of(), _j_vless(), _j_vmess(), _j_vmess_obj(), test_zz_j_alpn_and_extra_are_identity(), test_zz_j_alpn_same_value_still_collapses(), test_zz_j_amp_control_raw_line_really_is_broken(), test_zz_j_amp_entity_repaired_in_ingestion_funnel() (+13 more)

### Community 18 - "Last-known-good (lkg)"
Cohesion: 0.27
Nodes (19): _age_minutes(), _annotate(), _count_configs(), _dump(), _get(), _header_tested(), is_fresh_complete(), _load() (+11 more)

### Community 19 - "Shadowsocks parsing tests"
Cohesion: 0.11
Nodes (19): _f_ss_key_old_algorithm(), _f_ss_parts(), test_zz_f_ss_2022_userinfo_with_slash_preserved(), test_zz_f_ss_at_in_query_does_not_destroy_endpoint(), test_zz_f_ss_base64_userinfo_decoded(), test_zz_f_ss_control_patch_is_falsifiable(), test_zz_f_ss_host_agrees_with_endpoint_of(), test_zz_f_ss_ipv6_bracketed() (+11 more)

### Community 20 - "VMess / insecure-flag tests"
Cohesion: 0.16
Nodes (18): _k_emit(), _k_pair(), _k_vm(), test_zz_k_insecure_absent_equals_false(), test_zz_k_insecure_has_no_weight_where_it_is_never_emitted(), test_zz_k_insecure_is_identity_for_hysteria2_and_tuic(), test_zz_k_key_and_product_never_disagree(), test_zz_k_phase_hij_endpoint_marking_intact() (+10 more)

### Community 21 - "Subscription validation gate"
Cohesion: 0.23
Nodes (16): _api_get(), check_clash(), check_singbox(), check_subscriptions(), _classify_subscription(), _clean(), _find_binary(), main() (+8 more)

### Community 22 - "Fake writer test doubles"
Cohesion: 0.2
Nodes (14): _FakeWriter, _sync_env(), _sync_fixture(), _sync_git(), _sync_read(), _sync_run(), _sync_write(), test_reachability_socket_counter_ignores_non_socket_descriptors() (+6 more)

### Community 23 - "Corpus freeze tests"
Cohesion: 0.17
Nodes (16): _e4_corpus(), _e4_freeze_country(), _e4_remark_of(), _e6_sources(), test_a_node_can_never_shadow_a_group_name(), test_brand_remark_is_idempotent_over_the_adversarial_corpus(), test_branding_survives_every_adversarial_remark_in_the_text_outputs(), test_branding_survives_in_clash_and_singbox_for_the_adversarial_corpus() (+8 more)

### Community 24 - "Test harness utilities"
Cohesion: 0.21
Nodes (16): Exception, _bash(), _SkipTest, test_zzz_vc_a_corrupt_cached_archive_is_replaced_and_marked_for_saving(), test_zzz_vc_a_failed_download_on_a_cold_cache_still_fails_closed(), test_zzz_vc_a_hung_download_is_cut_at_the_budget(), test_zzz_vc_a_tampered_download_is_rejected_and_never_reaches_the_cache(), test_zzz_vc_binary_digests_are_enforced_even_on_a_cache_hit() (+8 more)

### Community 25 - "L2 reachability"
Cohesion: 0.24
Nodes (14): check_endpoints(), check_file(), check_lines(), fd_count(), FileDescriptorExhaustion, headroom_warning(), _is_ip(), _main() (+6 more)

### Community 26 - "One-command runner (run_all)"
Cohesion: 0.25
Nodes (13): build_plan(), check_google(), check_pipeline(), _display(), _env(), find_validator(), _last_json_object(), main() (+5 more)

### Community 27 - "Pipeline L3 stubs"
Cohesion: 0.22
Nodes (12): _pl_row(), _StubL3, test_pipeline_broken_rows_never_become_stable(), test_pipeline_fast_uses_the_median_not_a_single_run(), test_pipeline_matches_the_real_l3_result_contract(), test_pipeline_one_bad_round_cannot_be_ignored(), test_pipeline_output_survives_the_publication_gate(), test_pipeline_reports_every_layer_with_input_output_time_and_reasons() (+4 more)

### Community 28 - "LKG tests"
Cohesion: 0.27
Nodes (14): _lkg_aggregate(), _lkg_round(), _lkg_tree_md5(), test_zzz_lkg_a_failed_producer_never_wins_even_with_complete_looking_files(), test_zzz_lkg_cli_reports_state_and_escalates_after_a_day(), test_zzz_lkg_corrupt_index_and_health_never_block_the_file_restore(), test_zzz_lkg_failed_round_restores_previous_output_byte_for_byte(), test_zzz_lkg_first_run_failure_without_previous_output_does_not_crash() (+6 more)

### Community 29 - "Brand gate tests"
Cohesion: 0.26
Nodes (9): _fgate_result(), _fgate_seed(), _FgateBoom, test_zzz_f8_a_later_successful_write_clears_the_failure_flag(), test_zzz_f8_converter_failure_is_machine_readable_in_health_json(), test_zzz_f8_converter_failure_prunes_the_stale_file_instead_of_republishing(), test_zzz_f9_build_index_is_byte_identical_on_the_healthy_path(), test_zzz_f9_build_index_never_advertises_a_pruned_converter_file() (+1 more)

### Community 30 - "Header / bucket tests"
Cohesion: 0.36
Nodes (12): _hdr_buckets(), _hdr_sample_lines(), _idx_seed(), test_zzz_hdr_header_does_not_change_the_config_payload(), test_zzz_hdr_pipeline_buckets_and_top100_get_correct_labels(), test_zzz_idx_categories_block_is_left_byte_identical(), test_zzz_idx_merge_advertises_cascade_categories_and_top100(), test_zzz_idx_merge_is_failsafe_and_never_raises() (+4 more)

### Community 31 - "Source state memory"
Cohesion: 0.32
Nodes (8): _clip(), disable_candidates(), empty_state(), load_state(), mark_disabled(), _now_iso(), record_round(), source_key()

### Community 32 - "Reachability tests"
Cohesion: 0.44
Nodes (11): _patch_connect(), _patch_dns(), test_reachability_closes_every_socket_it_opens(), test_reachability_distinguishes_refusal_from_timeout_and_dns_failure(), test_reachability_emfile_raises_instead_of_reporting_a_wrong_rate(), test_reachability_error_keys_are_always_present_even_at_zero(), test_reachability_maps_open_endpoints_back_to_every_config_line(), test_reachability_probes_up_to_the_address_cap_not_just_the_first() (+3 more)

### Community 33 - "Published header tests"
Cohesion: 0.2
Nodes (10): _hd_headers(), _hd_trim_prefix(), test_zzz_hdr_aggregate_writes_headers_into_txt_b64_yaml_but_not_json(), test_zzz_hdr_archive_files_never_get_a_profile_header(), test_zzz_hdr_block_has_exactly_the_five_documented_keys(), test_zzz_hdr_existing_comment_heads_are_inert_for_hiddify(), test_zzz_hdr_protocol_files_get_headers_labelled_by_protocol(), test_zzz_hdr_survives_the_29_line_scan_window_in_every_output() (+2 more)

### Community 34 - "Clash / sing-box naming tests"
Cohesion: 0.29
Nodes (10): _c12_clash_names(), _c12_freeze(), _c12_singbox_tags(), _c12_vmess(), test_zz_c12_enforce_brand_rebrands_the_final_name_and_never_drops(), test_zz_c12_mutant_vmess_is_branded_in_clash_and_singbox(), test_zz_c12_the_gate_and_the_output_name_disagreed_before_the_fix(), test_zz_c12_the_two_decoders_diverge_and_that_is_the_root_cause() (+2 more)

### Community 35 - "Publish decision gate tests"
Cohesion: 0.22
Nodes (10): _f7_decision_block(), _f7_gate_step(), _f7_run_decision(), test_zzz_f7_a_future_timestamp_does_not_freeze_the_pipeline(), test_zzz_f7_a_healthy_age_is_judged_exactly_as_before(), test_zzz_f7_an_age_too_large_for_the_shell_still_opens_the_gate(), test_zzz_f7_an_unreadable_age_opens_the_gate_instead_of_skipping(), test_zzz_f7_an_unusable_threshold_also_opens_the_gate() (+2 more)

### Community 36 - "Google purge workflow tests"
Cohesion: 0.25
Nodes (9): _gr_purge_script(), _gr_workflow(), _sync_step(), test_zzz_gr_purge_refreshes_cascade_mirrors_in_a_separate_request(), test_zzz_gr_workflow_publishes_and_classifies_google_as_output(), test_zzz_gr_workflow_runs_google_after_cascade_and_before_the_gate(), test_zzz_lkg_sync_output_paths_are_the_publish_steps_own(), test_zzz_lkg_sync_runs_after_the_gate_and_before_the_stash() (+1 more)

### Community 37 - "Packet encoding tests"
Cohesion: 0.25
Nodes (8): _hd_vless(), test_zzz_hd_packet_encoding_go_parsequery_skips_are_left_untouched(), test_zzz_hd_packet_encoding_is_identity_preserving_and_idempotent(), test_zzz_hd_packet_encoding_key_normalisation_matches_ray2sing(), test_zzz_hd_packet_encoding_none_is_stripped_from_vless(), test_zzz_hd_packet_encoding_repeated_keys_follow_go_join_semantics(), test_zzz_hd_packet_encoding_runs_inside_the_single_ingestion_point(), test_zzz_hd_packet_encoding_supported_values_are_preserved_byte_for_byte()

### Community 38 - "Typing invariant tests"
Cohesion: 0.33
Nodes (7): _f2_admits_none(), _f2_implicit_optional_sites(), _f2_scripts_dir(), test_zzz_f2_no_production_signature_lies_about_accepting_none(), test_zzz_f2_optional_is_imported_wherever_it_is_used(), test_zzz_f2_the_invariant_covers_every_python_file_not_just_eleven(), test_zzz_f2_the_site_detector_itself_is_proven_not_assumed()

### Community 39 - "Network / sleep isolation tests"
Cohesion: 0.48
Nodes (7): _f1_no_network(), _f1_no_sleep(), _f1_restore(), test_zzz_f1_fetch_all_still_reraises_a_programming_error(), test_zzz_f1_fetch_all_survives_a_non_positive_worker_setting(), test_zzz_f1_fetch_source_survives_a_non_positive_retry_setting(), test_zzz_f1_positive_retry_settings_are_not_altered_by_the_clamp()

### Community 40 - "Freshness gate tests"
Cohesion: 0.33
Nodes (6): _f5_healthy_tree(), test_subscription_result_never_changes_the_existing_gate_verdict(), test_zzz_f5_a_run_that_proved_nothing_is_visible_not_silent(), test_zzz_f5_an_unrecognised_status_closes_the_gate(), test_zzz_f5_skipped_still_passes_because_that_is_the_documented_design(), test_zzz_f5_the_gate_is_an_allowlist_not_a_denylist()

### Community 41 - "Cross-module reference tests"
Cohesion: 0.47
Nodes (6): _p6_module_level_names(), _p6_reference_map(), _p6_repo_root(), _p6_scripts_dir(), _p6_source_files(), test_zzz_p6_no_module_level_name_in_scripts_has_zero_consumers()

### Community 42 - "Malformed-file report tests"
Cohesion: 0.4
Nodes (5): _f4_tmp(), test_zzz_f4_a_malformed_file_becomes_a_reportable_fail_not_a_crash(), test_zzz_f4_healthy_documents_are_still_accepted_unchanged(), test_zzz_f4_structural_checks_never_raise_on_a_malformed_document(), test_zzz_f4_the_total_wrapper_is_the_last_resort_not_the_first()

### Community 43 - "Mihomo compat tests"
Cohesion: 0.4
Nodes (5): _mc_b64(), test_mihomo_fatal_lines_never_reach_the_published_text_outputs(), test_ss_at_sign_in_query_no_longer_destroys_the_endpoint(), test_ss_plugin_that_no_client_can_run_drops_the_node(), test_ss_port_followed_by_a_slash_is_parsed()

### Community 44 - "argv (F5) tests"
Cohesion: 0.4
Nodes (2): _f5_argv, test_zzz_f5_the_strict_exit_code_is_what_ci_actually_gates_on()

### Community 45 - "GeoIP probe"
Cohesion: 0.7
Nodes (4): inspect_database(), main(), month_of_epoch(), probe()

### Community 46 - "VMess packet tests"
Cohesion: 0.67
Nodes (3): _hd_vmess(), _hd_vmess_obj(), test_zzz_hd_packet_encoding_vmess_uses_verbatim_json_key()

### Community 47 - "Empty-file pruning tests"
Cohesion: 0.67
Nodes (3): _fresh_outdir(), test_duplicates_files_are_never_written_and_stale_ones_are_removed(), test_empty_protocol_never_publishes_a_file_and_prunes_both_members()

### Community 48 - "Filter order tests"
Cohesion: 0.67
Nodes (3): test_filters_checks_cheap_rules_before_expensive_ones(), test_filters_drops_unroutable_and_structurally_invalid_servers(), _vmess_link()

### Community 49 - "Control-byte tests"
Cohesion: 0.67
Nodes (3): _p2_has_ctrl(), test_zzz_p2_extract_valid_lines_never_emits_a_control_byte(), test_zzz_p2_the_measured_corpus_line_is_repaired_without_losing_anything()

### Community 50 - "Vendored QR generator"
Cohesion: 0.67
Nodes (0): 

### Community 51 - "Social preview asset"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **Thin community `Social preview asset`** (2 nodes): `make_social_preview.py`, `main()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_FakeXk` connect `xray-knife fake-shim tests` to `Test invariants (core suite)`?**
  _High betweenness centrality (0.005) - this node is a cross-community bridge._
- **Why does `main.tsx` connect `Telegram bot handlers & DB` to `Dashboard client app.js`?**
  _High betweenness centrality (0.005) - this node is a cross-community bridge._
- **Why does `_StubL3` connect `Pipeline L3 stubs` to `Test invariants (core suite)`?**
  _High betweenness centrality (0.004) - this node is a cross-community bridge._
- **Are the 44 inferred relationships involving `_tmpdir()` (e.g. with `_fresh_outdir()` and `test_state_memory_never_raises_on_a_corrupt_or_missing_file()`) actually correct?**
  _`_tmpdir()` has 44 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `_c11_ssr()` (e.g. with `_c11_b64()` and `test_zz_c11_ssr_aead_ciphers_are_rejected_even_though_ss_allows_them()`) actually correct?**
  _`_c11_ssr()` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `_cty_line()` (e.g. with `test_zzz_cty_reads_the_country_from_the_remark_not_from_the_network()` and `test_zzz_cty_grouping_keeps_every_config_exactly_once()`) actually correct?**
  _`_cty_line()` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `t()` (e.g. with `copyWithFeedback()` and `renderQr()`) actually correct?**
  _`t()` has 22 INFERRED edges - model-reasoned connections that need verification._