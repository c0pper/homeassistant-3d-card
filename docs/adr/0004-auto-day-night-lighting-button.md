# In-card AUTO / DAY / NIGHT lighting button

The card followed the real sun (`sun: yes`, `backgroundColor: sky`) and
the ambient torch sensor. The user wants a manual day/night switch
without giving up the automatic look.

## Decision

- Add a small **AUTO / DAY / NIGHT** pill at the bottom-left of the
  custom sims card. It cycles AUTO -> DAY -> NIGHT -> AUTO.
- **AUTO** follows `sun.sun` and `globalLightPower` as before.
- **DAY** forces a fixed sun (azimuth 180°, elevation 45°), blue sky,
  `day_globalLightPower` (0.25) and `day_exposure` (1.15).
- **NIGHT** forces the sun below the horizon, stars/moon,
  `night_globalLightPower` (0.75) and `night_exposure` (1.0).
- Appearance only: the five lamp entities keep their states.
- The mode is held in the card (`_lightingMode`), not in an HA helper.
  It is per card/browser and resets to AUTO on reload; no automations
  or cross-device sync.
- `Environment.setManual()` performs the override and restores the sun,
  sky, torch and exposure when returning to AUTO.
- The button is part of the custom `floor3d-card-sims` build only; the
  HACS card has no button.

## Consequences

- The forced modes ignore the real time, which is the point of a manual
  switch. AUTO remains available as the third state.
- Because there is no helper, the state cannot be used in automations and
  resets on reload. Adding a helper later would mean changing the card
  to read it and changing the state store; not done now.
- The card config gains `day_globalLightPower`, `night_globalLightPower`,
  `day_exposure` and `night_exposure` (all optional; the card has
  defaults).
- The custom card must be rebuilt and its jsDelivr resource updated when
  these values or the button change.

Related: ADR 0003 (sims walls), `custom-card/README.md`, `README.md`,
`AGENTS.md`, `GLOSSARY.md`.
