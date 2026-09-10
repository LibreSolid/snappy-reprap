# Verify joint frames against ADR-097 (joint-frame-follows-declarer) — no code change

## Why

solid-node main (91c0b2a) integrated `joint-frame-follows-declarer`
(ADR-097): a class-body joint's `axis`, `at` and `carries` are now read in
the DECLARING BODY'S OWN REST FRAME, not the parent's. `at` defaults to
the body's own origin. This is stage B of the campaign tracked at
`libresolid-studio/docs/motion-general-refactor.md`; the archived
framework change
`solid-node/openspec/changes/archive/2026-09-10-joint-frame-follows-declarer/`
is the survey this record verifies against current source.

## What was checked, and why nothing changes

This project declares exactly 5 joint sites across `simulation/*.py`, no
`Orbit` or `Free` anywhere:

| Declaration | Parent placement | Relationship to axis |
|---|---|---|
| `Bridge.lift = Prismatic(axis=(0, 0, 1))` | `place(self.bridge, up(BRIDGE_Z))` | parallel translation |
| `LifterScrew.spin = Revolute(axis=(0, 0, 1))` | `place(self.screw, up(COUPLER_SEAT))` | parallel translation |
| `Pinion.spin = Revolute(axis=(0, 0, 1))` | `place(self.pinion, up(...), zrot(-90))` | parallel translation, and `zrot(-90)` leaves `(0,0,1)` invariant |
| `YSled.travel = Prismatic(axis=(0, -1, 0))` | `place(self.sled, up(SLED))` | not parallel, but Prismatic (no anchor point) |
| `XSled.travel = Prismatic(axis=(-1, 0, 0))` | `place(self.sled, up(SLED))` | not parallel, but Prismatic (no anchor point) |

None of the five declarations carries an `at=`/`carries=` argument, so
there is nothing to delete as a restatement. Three
(`Bridge.lift`, `LifterScrew.spin`, `Pinion.spin`) have a parent
translation exactly parallel to the joint's own axis — re-framing the
axis into the declaring body's own rest frame does not change the
physical line a Revolute spins about or the direction a Prismatic slides
along when the offset lies on that same line — and `Pinion.spin`'s
accompanying `zrot(-90)` was checked numerically
(`R_z(-90°)·(0,0,1) = (0,0,1)`) and found axis-invariant. The other two
(`YSled.travel`, `XSled.travel`) have a parent translation that is NOT
parallel to their axis, but both are `Prismatic`: a pure sliding freedom
has no anchor point for an offset to act on, so the joint is inert
regardless of the offset's direction.

**No source line in this project needs to change** — confirmed by the
framework cycle's read-only `patch_snappy-reprap.py`, which re-verifies
each of the five declaration lines against current source text
byte-for-byte and performs zero edits, and independently reconfirmed here
by re-reading `simulation/bridge.py`, `simulation/lifter.py`,
`simulation/motor_segment.py`, `simulation/y_sled.py` and
`simulation/x_sled.py` against the current commit.

## Evidence

- Faceted suite on main, unedited: 28/28 passed in 17.79 s.
- Exact suite on main, unedited: 28/28 passed in 25.15 s.
- Pose comparison: `capture_poses.py compare` of the pre-change BEFORE
  file (captured by the framework cycle on the pre-ADR-097 framework, from
  the untouched source) against an AFTER file captured on main (source
  untouched): **max deviation 0.000e+00 over 11 poses, 170 leaves.**

## Outcome

No code change. This record is the verified no-op: the project was
already correct under ADR-097's rule before this record was written, and
remains correct after. Not archived (the orchestrator reviews first).
