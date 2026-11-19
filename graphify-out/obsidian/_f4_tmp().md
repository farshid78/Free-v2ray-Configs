---
source_file: "scripts\test_pipeline.py"
type: "code"
community: "Malformed-file report tests"
location: "L10336"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Malformed-file_report_tests
---

# _f4_tmp()

## Connections
- [[.close()]] - `calls` [INFERRED]
- [[test_pipeline.py]] - `contains` [EXTRACTED]
- [[test_zzz_f4_a_malformed_file_becomes_a_reportable_fail_not_a_crash()]] - `calls` [INFERRED]
- [[test_zzz_f4_healthy_documents_are_still_accepted_unchanged()]] - `calls` [INFERRED]
- [[test_zzz_f4_structural_checks_never_raise_on_a_malformed_document()]] - `calls` [INFERRED]
- [[test_zzz_f4_the_total_wrapper_is_the_last_resort_not_the_first()]] - `calls` [INFERRED]

#graphify/code #graphify/INFERRED #community/Malformed-file_report_tests