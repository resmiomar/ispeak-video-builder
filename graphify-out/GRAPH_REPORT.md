# Graph Report - ispeak-video-builder  (2026-08-26)

## Corpus Check
- 7 files · ~21,339 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 166 nodes · 209 edges · 17 communities (9 shown, 8 thin omitted)
- Extraction: 67% EXTRACTED · 33% INFERRED · 0% AMBIGUOUS · INFERRED: 68 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c89e9378`
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
- [[_COMMUNITY_ease_out_back|ease_out_back]]
- [[_COMMUNITY_make_background|make_background]]

## God Nodes (most connected - your core abstractions)
1. `render_card()` - 12 edges
2. `build()` - 10 edges
3. `_head()` - 6 edges
4. `paste_mascot()` - 6 edges
5. `brand_font()` - 6 edges
6. `draw_band()` - 6 edges
7. `_body()` - 5 edges
8. `mascot_layer()` - 5 edges
9. `theme_of()` - 5 edges
10. `hero_theme_has()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `build()` --calls--> `has_photo()`  [INFERRED]
  video/render.py → video/mascot.py
- `build()` --calls--> `paste_mascot()`  [INFERRED]
  video/render.py → video/mascot.py

## Import Cycles
- None detected.

## Communities (17 total, 8 thin omitted)

### Community 1 - "render.py"
Cohesion: 0.13
Nodes (28): background_photo(), blank_page(), brand_font(), build(), centred(), draw_band(), duration(), envelope() (+20 more)

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

### Community 14 - "ease_out_back"
Cohesion: 0.12
Nodes (25): _arm(), _bezier(), _body(), _ears(), _eyes(), has_photo(), _head(), mascot_layer() (+17 more)

## Knowledge Gaps
- **6 isolated node(s):** `OUT`, `KINDS`, `AGES`, `files`, `Noto Emoji (Google)` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build()` connect `render.py` to `ease_out_back`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `paste_mascot()` connect `ease_out_back` to `render.py`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `build()` (e.g. with `has_photo()` and `paste_mascot()`) actually correct?**
  _`build()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Розетки барса: кольцо с пятном внутри, размеры чуть разные.      Ровные одинаков`, `Кубическая кривая точками: Pillow не умеет кривые, только ломаные.`, `Хвост барса длиннее тела и загибается кверху.      Рисуется не одной линией, а ц` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `art.py` be split into smaller, more focused modules?**
  _Cohesion score 0.028985507246376812 - nodes in this community are weakly interconnected._
- **Should `render.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12807881773399016 - nodes in this community are weakly interconnected._
- **Should `ease_out_back` be split into smaller, more focused modules?**
  _Cohesion score 0.12307692307692308 - nodes in this community are weakly interconnected._