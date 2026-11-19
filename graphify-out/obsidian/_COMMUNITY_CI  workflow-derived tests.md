---
type: community
cohesion: 0.07
members: 32
---

# CI / workflow-derived tests

**Cohesion:** 0.07 - loosely connected
**Members:** 32 nodes

## Members
- [[_c1b_cache_actions()]] - code - scripts\test_pipeline.py
- [[_c1b_geoip_steps()]] - code - scripts\test_pipeline.py
- [[_is_sha_pin()]] - code - scripts\test_pipeline.py
- [[_p3_download_steps()]] - code - scripts\test_pipeline.py
- [[_p3_is_sha256()]] - code - scripts\test_pipeline.py
- [[_summary_cascade_snippet()]] - code - scripts\test_pipeline.py
- [[_workflow_run_text()]] - code - scripts\test_pipeline.py
- [[_workflow_text()]] - code - scripts\test_pipeline.py
- [[_workflow_uses()]] - code - scripts\test_pipeline.py
- [[_xray_knife_install_step()]] - code - scripts\test_pipeline.py
- [[test_every_workflow_action_is_pinned_to_an_immutable_commit_sha()]] - code - scripts\test_pipeline.py
- [[test_workflow_caches_xray_knife_keyed_by_its_checksum()]] - code - scripts\test_pipeline.py
- [[test_workflow_downloads_and_caches_the_geoip_database()]] - code - scripts\test_pipeline.py
- [[test_workflow_installs_xray_knife_pinned_to_the_measured_version()]] - code - scripts\test_pipeline.py
- [[test_workflow_never_uses_maxmind_which_requires_a_licence_key()]] - code - scripts\test_pipeline.py
- [[test_workflow_pins_python_precisely_because_identity_depends_on_it()]] - code - scripts\test_pipeline.py
- [[test_workflow_publishes_the_cascade_categories_it_builds()]] - code - scripts\test_pipeline.py
- [[test_workflow_runs_the_cascade_before_it_validates_and_publishes()]] - code - scripts\test_pipeline.py
- [[test_workflow_summary_reports_the_measured_working_rate_every_run()]] - code - scripts\test_pipeline.py
- [[test_workflow_treats_cascade_output_as_output_not_as_source()]] - code - scripts\test_pipeline.py
- [[test_workflow_uses_the_xray_knife_flag_that_actually_exists()]] - code - scripts\test_pipeline.py
- [[test_workflow_verifies_both_the_xray_knife_archive_and_binary()]] - code - scripts\test_pipeline.py
- [[test_workflow_verifies_the_xray_knife_binary_even_on_a_cache_hit()]] - code - scripts\test_pipeline.py
- [[test_zzz_c1b_geoip_cache_is_saved_only_after_a_verified_download()]] - code - scripts\test_pipeline.py
- [[test_zzz_c1b_geoip_cache_uses_restore_and_save_separately()]] - code - scripts\test_pipeline.py
- [[test_zzz_c1b_geoip_step_detector_finds_the_real_steps()]] - code - scripts\test_pipeline.py
- [[test_zzz_c1b_restored_database_is_validated_by_content_not_by_its_key()]] - code - scripts\test_pipeline.py
- [[test_zzz_p3_every_binary_download_in_the_workflow_is_checksum_verified()]] - code - scripts\test_pipeline.py
- [[test_zzz_p3_installer_actually_uses_every_checksum_it_declares()]] - code - scripts\test_pipeline.py
- [[test_zzz_p3_sha256_matcher_accepts_and_rejects_correctly()]] - code - scripts\test_pipeline.py
- [[test_zzz_p3_singbox_and_mihomo_verify_archive_before_extract_and_binary_before_install()]] - code - scripts\test_pipeline.py
- [[test_zzz_p6_geo_module_has_no_second_source_of_truth_for_the_download_url()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/CI_/_workflow-derived_tests
SORT file.name ASC
```

## Connections to other communities
- 32 edges to [[_COMMUNITY_Test invariants (core suite)]]
- 1 edge to [[_COMMUNITY_Publish decision gate tests]]
- 1 edge to [[_COMMUNITY_Test harness utilities]]

## Top bridge nodes
- [[_workflow_text()]] - degree 18, connects to 3 communities
- [[_xray_knife_install_step()]] - degree 6, connects to 1 community
- [[_c1b_geoip_steps()]] - degree 5, connects to 1 community
- [[_c1b_cache_actions()]] - degree 4, connects to 1 community
- [[_workflow_run_text()]] - degree 4, connects to 1 community