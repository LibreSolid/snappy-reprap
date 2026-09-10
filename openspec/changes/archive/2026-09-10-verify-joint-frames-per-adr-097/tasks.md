# Tasks

No source edit: this is a verified no-op record (see `proposal.md`).
Repository was clean at `2e69ad5` before and after this record (only this
change's own new `openspec/changes/` directory is added).

- [x] 1. Confirm `git rev-parse --show-toplevel` names this repository and
      `git status --porcelain` is clean.
- [x] 2. Re-derive, from current source, that all 5 joint declarations
      (`Bridge.lift`, `LifterScrew.spin`, `Pinion.spin`, `YSled.travel`,
      `XSled.travel`) are inert under ADR-097 — three by a parent
      translation parallel to the joint's own axis (with `Pinion.spin`'s
      `zrot(-90)` confirmed axis-invariant), two by being Prismatic with
      no anchor for a non-parallel offset to act on. Cross-checked against
      the framework cycle's read-only `patch_snappy-reprap.py` (which
      performs zero edits for the same reason).
- [x] 3. Run the faceted suite, unedited.
      **Result:** 28/28 passed in 17.79 s.
- [x] 4. Run the exact suite, unedited.
      **Result:** 28/28 passed in 25.15 s.
- [x] 5. Capture AFTER poses on main (source untouched) and compare
      against the framework cycle's BEFORE file (captured on the
      pre-ADR-097 framework from the untouched source).
      **Result:** max deviation 0.000e+00 over 11 poses, 170 leaves.
- [x] 6. Write this proposal and these tasks recording the verified
      no-op; do not archive (the orchestrator reviews first).
