# Graph Report - ispeak-video-builder  (2026-08-24)

## Corpus Check
- 7 files · ~20,404 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 133 nodes · 156 edges · 16 communities (8 shown, 8 thin omitted)
- Extraction: 55% EXTRACTED · 45% INFERRED · 0% AMBIGUOUS · INFERRED: 70 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `34607fb6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_render.py|render.py]]
- [[_COMMUNITY__colour_blob|_colour_blob]]
- [[_COMMUNITY_draw_object|draw_object]]
- [[_COMMUNITY_ease_out_back|ease_out_back]]
- [[_COMMUNITY_scene_background|scene_background]]
- [[_COMMUNITY__animal|_animal]]
- [[_COMMUNITY__dots|_dots]]
- [[_COMMUNITY__figure|_figure]]
- [[_COMMUNITY__nose|_nose]]
- [[_COMMUNITY__part|_part]]
- [[_COMMUNITY__place|_place]]
- [[_COMMUNITY_send.mjs|send.mjs]]
- [[_COMMUNITY_ease_out_back|ease_out_back]]
- [[_COMMUNITY_make_background|make_background]]

## God Nodes (most connected - your core abstractions)
1. `render_card()` - 11 edges
2. `background()` - 8 edges
3. `build()` - 7 edges
4. `_colour_blob()` - 5 edges
5. `brand_font()` - 5 edges
6. `draw_object()` - 4 edges
7. `scene_background()` - 4 edges
8. `theme_of()` - 4 edges
9. `Сторонние материалы` - 3 edges
10. `asset()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `render_card()` --calls--> `draw_object()`  [INFERRED]
  video/render.py → video/art.py
- `background()` --calls--> `make_background()`  [INFERRED]
  video/render.py → video/art.py
- `render_card()` --calls--> `ease_out_back()`  [INFERRED]
  video/render.py → video/art.py
- `background()` --calls--> `scene_background()`  [INFERRED]
  video/render.py → video/art.py

## Import Cycles
- None detected.

## Communities (16 total, 8 thin omitted)

### Community 1 - "render.py"
Cohesion: 0.16
Nodes (21): background(), background_photo(), brand_font(), build(), centred(), duration(), envelope(), fit() (+13 more)

### Community 2 - "_colour_blob"
Cohesion: 0.40
Nodes (5): _colour_blob(), Цвет показываем кляксой краски: у слова «red» предмета нет., _red(), _swatch(), _yellow()

### Community 3 - "draw_object"
Cohesion: 0.50
Nodes (4): asset(), draw_object(), Файл картинки для слова, если он положен. Иначе None., Предмет по английскому слову: сначала файл, потом рисунок кодом.      Ничего нет

### Community 4 - "ease_out_back"
Cohesion: 0.50
Nodes (3): Montserrat, Noto Emoji (Google), Сторонние материалы

### Community 5 - "scene_background"
Cohesion: 0.50
Nodes (4): Окно: рама и свет. Одно окно делает стену комнатой, а не заливкой., Комната по имени фона. Незнакомое имя возвращает None: тогда рисуется     обычны, scene_background(), _window()

### Community 13 - "send.mjs"
Cohesion: 0.33
Nodes (6): AGES, caption(), files, KINDS, OUT, send()

## Knowledge Gaps
- **6 isolated node(s):** `OUT`, `KINDS`, `AGES`, `files`, `Noto Emoji (Google)` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `render_card()` connect `render.py` to `draw_object`, `ease_out_back`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Why does `draw_object()` connect `draw_object` to `art.py`, `render.py`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Why does `background()` connect `render.py` to `scene_background`, `make_background`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `render_card()` (e.g. with `draw_object()` and `ease_out_back()`) actually correct?**
  _`render_card()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `background()` (e.g. with `make_background()` and `scene_background()`) actually correct?**
  _`background()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `OUT`, `KINDS`, `AGES` to the rest of the system?**
  _26 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `art.py` be split into smaller, more focused modules?**
  _Cohesion score 0.028985507246376812 - nodes in this community are weakly interconnected._