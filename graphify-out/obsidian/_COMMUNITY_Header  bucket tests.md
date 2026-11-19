---
type: community
cohesion: 0.36
members: 12
---

# Header / bucket tests

**Cohesion:** 0.36 - loosely connected
**Members:** 12 nodes

## Members
- [[_hdr_buckets()]] - code - scripts\test_pipeline.py
- [[_hdr_sample_lines()]] - code - scripts\test_pipeline.py
- [[_idx_seed()]] - code - scripts\test_pipeline.py
- [[test_zzz_hdr_header_does_not_change_the_config_payload()]] - code - scripts\test_pipeline.py
- [[test_zzz_hdr_pipeline_buckets_and_top100_get_correct_labels()]] - code - scripts\test_pipeline.py
- [[test_zzz_idx_categories_block_is_left_byte_identical()]] - code - scripts\test_pipeline.py
- [[test_zzz_idx_merge_advertises_cascade_categories_and_top100()]] - code - scripts\test_pipeline.py
- [[test_zzz_idx_merge_is_failsafe_and_never_raises()]] - code - scripts\test_pipeline.py
- [[test_zzz_idx_never_advertises_a_file_that_does_not_exist()]] - code - scripts\test_pipeline.py
- [[test_zzz_idx_primary_links_are_raw_and_outnumber_mirrors_in_real_shape()]] - code - scripts\test_pipeline.py
- [[test_zzz_idx_urls_are_built_from_the_document_not_a_second_constant()]] - code - scripts\test_pipeline.py
- [[test_zzz_idx_write_is_atomic_and_leaves_no_tmp_behind()]] - code - scripts\test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Header_/_bucket_tests
SORT file.name ASC
```

## Connections to other communities
- 12 edges to [[_COMMUNITY_Test invariants (core suite)]]
- 3 edges to [[_COMMUNITY_Published header tests]]

## Top bridge nodes
- [[_hdr_sample_lines()]] - degree 12, connects to 2 communities
- [[test_zzz_hdr_pipeline_buckets_and_top100_get_correct_labels()]] - degree 4, connects to 2 communities
- [[_hdr_buckets()]] - degree 10, connects to 1 community
- [[_idx_seed()]] - degree 7, connects to 1 community
- [[test_zzz_idx_categories_block_is_left_byte_identical()]] - degree 4, connects to 1 community