---
type: community
cohesion: 0.15
members: 31
---

# GeoIP country grouping

**Cohesion:** 0.15 - loosely connected
**Members:** 31 nodes

## Members
- [[_dns_timeout()]] - code - scripts\geo.py
- [[_float_env()]] - code - scripts\countries.py
- [[_get_reader()]] - code - scripts\geo.py
- [[_host_of()]] - code - scripts\countries.py
- [[_int_env()]] - code - scripts\countries.py
- [[_remove_if_exists()_1]] - code - scripts\countries.py
- [[_scan_names()]] - code - scripts\countries.py
- [[_sweep()]] - code - scripts\countries.py
- [[_targeted_names()]] - code - scripts\countries.py
- [[_warn_env()]] - code - scripts\countries.py
- [[_write_text()_1]] - code - scripts\countries.py
- [[countries.py]] - code - scripts\countries.py
- [[country_code_of()]] - code - scripts\countries.py
- [[country_for_host()]] - code - scripts\geo.py
- [[country_of_addrs()]] - code - scripts\geo.py
- [[country_of_ip()]] - code - scripts\geo.py
- [[database_available()]] - code - scripts\geo.py
- [[flag_of()]] - code - scripts\geo.py
- [[geo.py]] - code - scripts\geo.py
- [[group_by_country()]] - code - scripts\countries.py
- [[header_for()]] - code - scripts\countries.py
- [[is_ip_literal()]] - code - scripts\geo.py
- [[is_safe_slug()]] - code - scripts\countries.py
- [[log()_1]] - code - scripts\countries.py
- [[reset()]] - code - scripts\geo.py
- [[resolve_all()]] - code - scripts\geo.py
- [[resolve_names()]] - code - scripts\countries.py
- [[slug_for()]] - code - scripts\countries.py
- [[stats()]] - code - scripts\geo.py
- [[warm_up()]] - code - scripts\geo.py
- [[write_countries()]] - code - scripts\countries.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/GeoIP_country_grouping
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Test invariants (core suite)]]
- 1 edge to [[_COMMUNITY_Aggregate pipeline & sources]]
- 1 edge to [[_COMMUNITY_Config core (brand, dedup, extract)]]
- 1 edge to [[_COMMUNITY_Filters + L0L1 stage]]

## Top bridge nodes
- [[countries.py]] - degree 21, connects to 3 communities
- [[geo.py]] - degree 15, connects to 2 communities