---
type: community
cohesion: 0.11
members: 30
---

# xray-knife fake-shim tests

**Cohesion:** 0.11 - loosely connected
**Members:** 30 nodes

## Members
- [[.__enter__()]] - code - scripts\test_pipeline.py
- [[.__exit__()]] - code - scripts\test_pipeline.py
- [[.__init__()_4]] - code - scripts\test_pipeline.py
- [[.argv()]] - code - scripts\test_pipeline.py
- [[.input()]] - code - scripts\test_pipeline.py
- [[_FakeXk]] - code - scripts\test_pipeline.py
- [[_gr_ep()]] - code - scripts\test_pipeline.py
- [[_gr_geo()]] - code - scripts\test_pipeline.py
- [[_gr_rounds()]] - code - scripts\test_pipeline.py
- [[_gr_tree()]] - code - scripts\test_pipeline.py
- [[_l3_csv()]] - code - scripts\test_pipeline.py
- [[_l3_row()]] - code - scripts\test_pipeline.py
- [[test_realtest_deletes_a_stale_output_before_running()]] - code - scripts\test_pipeline.py
- [[test_realtest_guard_reproduces_the_measured_census_exactly()]] - code - scripts\test_pipeline.py
- [[test_realtest_marks_partial_output_but_not_mere_deduplication()]] - code - scripts\test_pipeline.py
- [[test_realtest_parses_csv_with_commas_inside_quoted_fields()]] - code - scripts\test_pipeline.py
- [[test_realtest_reports_an_unknown_status_instead_of_hiding_it()]] - code - scripts\test_pipeline.py
- [[test_realtest_stats_are_internally_consistent()]] - code - scripts\test_pipeline.py
- [[test_zzz_gr_a_blocked_or_captcha_gemini_is_never_ready()]] - code - scripts\test_pipeline.py
- [[test_zzz_gr_a_converter_crash_leaves_no_half_written_category()]] - code - scripts\test_pipeline.py
- [[test_zzz_gr_a_failed_cascade_never_tests_the_stale_verified_list()]] - code - scripts\test_pipeline.py
- [[test_zzz_gr_end_to_end_through_realtest_with_a_fake_binary()]] - code - scripts\test_pipeline.py
- [[test_zzz_gr_no_geo_phase_without_time_for_it()]] - code - scripts\test_pipeline.py
- [[test_zzz_gr_no_round_starts_without_the_time_budget()]] - code - scripts\test_pipeline.py
- [[test_zzz_gr_only_gemini_supported_countries_are_published()]] - code - scripts\test_pipeline.py
- [[test_zzz_gr_publish_writes_four_files_and_advertises_them()]] - code - scripts\test_pipeline.py
- [[test_zzz_gr_reads_verified_without_headers_or_shield_lines()]] - code - scripts\test_pipeline.py
- [[test_zzz_gr_ready_keeps_the_verified_order()]] - code - scripts\test_pipeline.py
- [[test_zzz_gr_ready_needs_every_service_in_every_round()]] - code - scripts\test_pipeline.py
- [[test_zzz_gr_stale_google_dir_is_removed_when_the_round_cannot_judge()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/xray-knife_fake-shim_tests
SORT file.name ASC
```

## Connections to other communities
- 25 edges to [[_COMMUNITY_Test invariants (core suite)]]

## Top bridge nodes
- [[_FakeXk]] - degree 9, connects to 1 community
- [[_gr_tree()]] - degree 9, connects to 1 community
- [[_gr_ep()]] - degree 8, connects to 1 community
- [[_l3_csv()]] - degree 8, connects to 1 community
- [[_l3_row()]] - degree 8, connects to 1 community