---
type: community
cohesion: 0.08
members: 41
---

# Telegram bot handlers & DB

**Cohesion:** 0.08 - loosely connected
**Members:** 41 nodes

## Members
- [[_conn()]] - code - bot\db.py
- [[_is_admin()]] - code - bot\handlers\admin.py
- [[_route_text()]] - code - bot\main.py
- [[_trigger_aggregate()]] - code - bot\handlers\admin.py
- [[add_admin()]] - code - bot\db.py
- [[add_user()]] - code - bot\db.py
- [[adm_addadmin()]] - code - bot\handlers\admin.py
- [[adm_addsource()]] - code - bot\handlers\admin.py
- [[adm_addsource_cat()]] - code - bot\handlers\admin.py
- [[adm_broadcast()]] - code - bot\handlers\admin.py
- [[adm_removeadmin()]] - code - bot\handlers\admin.py
- [[adm_removesource()]] - code - bot\handlers\admin.py
- [[adm_removesource_do()]] - code - bot\handlers\admin.py
- [[adm_sources()]] - code - bot\handlers\admin.py
- [[adm_stats()]] - code - bot\handlers\admin.py
- [[adm_trigger()]] - code - bot\handlers\admin.py
- [[admin.py]] - code - bot\handlers\admin.py
- [[admin_menu()]] - code - bot\keyboards.py
- [[admin_panel()]] - code - bot\handlers\admin.py
- [[ask_count()]] - code - bot\handlers\user.py
- [[ask_country()]] - code - bot\handlers\user.py
- [[ask_proto()]] - code - bot\handlers\user.py
- [[back_main()]] - code - bot\handlers\user.py
- [[build_app()]] - code - bot\main.py
- [[config.py]] - code - bot\config.py
- [[db.py]] - code - bot\db.py
- [[handle_admin_text()]] - code - bot\handlers\admin.py
- [[handle_text()]] - code - bot\handlers\user.py
- [[is_admin()]] - code - bot\db.py
- [[is_owner()]] - code - bot\config.py
- [[keyboards.py]] - code - bot\keyboards.py
- [[latest20()]] - code - bot\handlers\user.py
- [[main()_4]] - code - bot\main.py
- [[main.tsx]] - code - dashboard-src\src\main.tsx
- [[main_menu()]] - code - bot\keyboards.py
- [[proto_selected()]] - code - bot\handlers\user.py
- [[protocols_menu()]] - code - bot\keyboards.py
- [[remove_admin()]] - code - bot\db.py
- [[start()]] - code - bot\handlers\user.py
- [[user.py]] - code - bot\handlers\user.py
- [[user_count()]] - code - bot\db.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Telegram_bot_handlers_&_DB
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Dashboard UI components]]
- 1 edge to [[_COMMUNITY_Dashboard client app.js]]

## Top bridge nodes
- [[user.py]] - degree 12, connects to 1 community
- [[config.py]] - degree 7, connects to 1 community
- [[main.tsx]] - degree 7, connects to 1 community