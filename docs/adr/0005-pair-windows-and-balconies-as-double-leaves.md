# Pair windows and balconies as one opening with two equal leaves

The top wall had been traced as **two separate openings per group** with a
wall pier between them:

- bedroom pair: 0.21 m pier;
- kitchen balcony pair: 0.43 m pier;
- living balcony pair: 0.57 m pier;
- studio pair: 0.29 m pier.

The glass was already parallel, but each group read as two separate
windows/doors divided by a wall. In reality these are two openable
leaves of one window/door, with a thin frame between them.

## Decision

- Replace each of the four pairs with **one combined opening** from the
  outer edge of the first leaf to the outer edge of the second.
- Put a **6 cm mullion** at the centre and two **equal glass leaves**.
- Keep the bedroom and studio as **windows** (90 cm sill, 2.2 m head);
  keep the two balconies as **full-height glass doors** (5–285 cm).
- The mullion is a wall/frame piece named with the wall line and split
  at 20 cm like the rest (`wall_sims_low/high_top_*`); the leaves are
  `wall_sims_glass_low/high_top_*`.
- The old wall piers disappear. The glass leaves are wider and equal in
  each pair, and remain parallel to the wall.
- The `sims` mode lowers the mullion and the leaves with their wall line;
  the near glass keeps its low part and the upper parts hide.

## Consequences

- The plan's original unequal leaf widths are replaced by equal leaves
  within each combined opening; the outer extents stay the same.
- The short pier walls that caused the earlier "pillar" reports are gone
  from the pairs; the remaining 6 cm mullions are frame, not wall.
- `PAIR_MULLION = 0.06` in `make_home.py`; changing it requires a model
  regeneration and a new model commit.
- The bedroom/studio are still windows, not French doors. Making them
  full-height is a separate decision.
- The custom card and its `sims` grouping/near-band logic are unchanged.

Related: `README.md`, `AGENTS.md`, `GLOSSARY.md`, ADR 0003.
