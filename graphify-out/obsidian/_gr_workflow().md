---
source_file: "scripts\test_pipeline.py"
type: "code"
community: "Google purge workflow tests"
location: "L16378"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Google_purge_workflow_tests
---

# _gr_workflow()

## Connections
- [[_gr_purge_script()]] - `calls` [INFERRED]
- [[_sync_run()]] - `calls` [INFERRED]
- [[_sync_step()]] - `calls` [INFERRED]
- [[test_pipeline.py]] - `contains` [EXTRACTED]
- [[test_zzz_gr_workflow_publishes_and_classifies_google_as_output()]] - `calls` [INFERRED]
- [[test_zzz_gr_workflow_runs_google_after_cascade_and_before_the_gate()]] - `calls` [INFERRED]
- [[test_zzz_lkg_sync_output_paths_are_the_publish_steps_own()]] - `calls` [INFERRED]
- [[test_zzz_lkg_sync_runs_after_the_gate_and_before_the_stash()]] - `calls` [INFERRED]
- [[test_zzz_lkg_workflow_stashes_early_and_settles_always()]] - `calls` [INFERRED]

#graphify/code #graphify/INFERRED #community/Google_purge_workflow_tests