# Rafiq brand assets

The full identity guide (Arabic) is [visual-identity-ar.md](visual-identity-ar.md). The code source of truth for colours and the mascot is `src/rafiq/brand.py`.

| Asset | File |
|---|---|
| Brand board (source, palette A) | [brand-board.jpg](brand-board.jpg) |
| Mascot (welcome screen, README) | [../../assets/mascot.png](../../assets/mascot.png) |
| App icon (header, favicon) | [../../assets/icon.png](../../assets/icon.png), [icon-128](../../assets/icon-128.png) |
| SVG icon (vector, simplified) | [icon.svg](icon.svg) |
| Mascot: warm (default) | [mascot-warm.svg](mascot-warm.svg) |
| Mascot: thinking | [mascot-thinking.svg](mascot-thinking.svg) |
| Mascot: listening (safety mode) | [mascot-listening.svg](mascot-listening.svg) |
| Mascot: encouraging | [mascot-encouraging.svg](mascot-encouraging.svg) |
| Mascot: calm (paused / quiet hours) | [mascot-calm.svg](mascot-calm.svg) |

Palette A (sage): primary `#2D6255`, shell `#D5E3D6`, face `#F2DDC3`, background `#FAF8F3`, text `#263B33`, secondary text `#58685E`, accent `#E7B6A3`.

The PNGs in `assets/` are crops of the brand board. The SVG expression states are a simplified vector version of the same mascot, used for chat avatars where the expression changes; the board only shows one expression. The expressions sheet and transparent mascot referenced by the guide (`RAFEEQ_CHARACTER_EXPRESSIONS.png`, `RAFEEQ_MASCOT_GREEN.png`) are not in this repository yet. Regenerate the SVGs after changing `brand.py`:

```bash
python -c "from rafiq.brand import mascot_svg as m; [open(f'docs/brand/mascot-{s}.svg','w').write(m(s)) for s in ['warm','thinking','listening','encouraging','calm']]; open('docs/brand/icon.svg','w').write(m(tail=True))"
```
