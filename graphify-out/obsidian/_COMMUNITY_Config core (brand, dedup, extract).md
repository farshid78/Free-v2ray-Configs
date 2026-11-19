---
type: community
cohesion: 0.09
members: 42
---

# Config core (brand, dedup, extract)

**Cohesion:** 0.09 - loosely connected
**Members:** 42 nodes

## Members
- [[ControlByteInOutput]] - code - scripts\core.py
- [[_flag_to_country_code()]] - code - scripts\core.py
- [[_go_query_unescape()]] - code - scripts\core.py
- [[_insecure_flag()]] - code - scripts\core.py
- [[_is_plausible_fronting_host()]] - code - scripts\core.py
- [[_is_shield()]] - code - scripts\core.py
- [[_keyword_hit()]] - code - scripts\core.py
- [[_norm_aid()]] - code - scripts\core.py
- [[_norm_identity_value()]] - code - scripts\core.py
- [[_norm_type()]] - code - scripts\core.py
- [[_normalize_packet_encoding()]] - code - scripts\core.py
- [[_pct_encode_ctrl()]] - code - scripts\core.py
- [[_repair_amp_separator()]] - code - scripts\core.py
- [[_repair_control_chars()]] - code - scripts\core.py
- [[_sni_is_endpoint()]] - code - scripts\core.py
- [[_ssr_b64_text()]] - code - scripts\core.py
- [[_ssr_parts()]] - code - scripts\core.py
- [[_strip_vless_packet_encoding()]] - code - scripts\core.py
- [[_strip_vmess_packet_encoding()]] - code - scripts\core.py
- [[_vmess_security()]] - code - scripts\core.py
- [[assert_no_control_bytes()]] - code - scripts\core.py
- [[brand_remark()]] - code - scripts\core.py
- [[core.py]] - code - scripts\core.py
- [[country_for_endpoint()]] - code - scripts\core.py
- [[decode_base64_text()]] - code - scripts\core.py
- [[dedup_key()]] - code - scripts\core.py
- [[detect_country_from_remark()]] - code - scripts\core.py
- [[encode_base64_subscription()]] - code - scripts\core.py
- [[endpoint_of()]] - code - scripts\core.py
- [[extract_valid_lines()]] - code - scripts\core.py
- [[hiddify_profile_header()]] - code - scripts\core.py
- [[is_branded()]] - code - scripts\core.py
- [[is_dummy_config()]] - code - scripts\core.py
- [[is_proxy_config()]] - code - scripts\core.py
- [[is_ray2sing_prefixed()]] - code - scripts\core.py
- [[normalize_scheme()]] - code - scripts\core.py
- [[protocol_of()]] - code - scripts\core.py
- [[remark_of()]] - code - scripts\core.py
- [[reset_country_cache()]] - code - scripts\core.py
- [[shield_unsupported_runs()]] - code - scripts\core.py
- [[stable_label()]] - code - scripts\core.py
- [[try_base64_decode()]] - code - scripts\core.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Config_core_(brand,_dedup,_extract)
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Google-Ready layer & realtest]]
- 1 edge to [[_COMMUNITY_Aggregate pipeline & sources]]
- 1 edge to [[_COMMUNITY_Brand config & renderers]]
- 1 edge to [[_COMMUNITY_Clash  sing-box converters]]
- 1 edge to [[_COMMUNITY_GeoIP country grouping]]
- 1 edge to [[_COMMUNITY_Filters + L0L1 stage]]
- 1 edge to [[_COMMUNITY_Test invariants (core suite)]]

## Top bridge nodes
- [[core.py]] - degree 48, connects to 7 communities
- [[dedup_key()]] - degree 12, connects to 1 community
- [[ControlByteInOutput]] - degree 3, connects to 1 community