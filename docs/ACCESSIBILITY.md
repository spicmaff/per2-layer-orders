# Accessibility contract

- Mathematical distinctions do not rely on color alone.
- M/V use literal labels and solid/dashed styling.
- Compatible/incompatible use `✓/×` plus fill/border differences.
- Every interactive state must have a textual equivalent and deterministic static SVG fallback.
- Motion is off by default and respects reduced-motion settings.
- Required information may not exist only on hover.
- Mobile layouts reflow by panel; they do not merely shrink a dense desktop canvas.
- The `MMMMVV` directed-cycle view exposes every revealed inequality as text in addition to the SVG edge.
- Pending witness steps do not reveal future inequalities; `Previous / Next / Reset` and left/right arrow stepping remain keyboard-operable.
- Face identity remains literal (`A_i/B_i`) in map, row, layer-order and witness views; color is supplementary.
- The cycle-closing relation is identified both by text (`closes cycle`) and by non-color emphasis in the static fallback.
