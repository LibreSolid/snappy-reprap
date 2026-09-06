## 1. Reading the design

- [x] 1.1 `pyproject.toml` naming `simulation.snappy_reprap:SnappyReprap`; `simulation/scad.py` with one handle per source file and the source set; `params.py` probing every top-level name of `config.scad`; `colors.py`; `part.py`; `place.py`
- [x] 1.2 One leaf per printed and bought part, coloured as the design paints it, in `vitamins.py`, `rails.py`, `sled_parts.py`, `chain_parts.py`, `lifter.py`, `tower.py`, `extruder.py`, `bridge.py`, `brace.py`, `spool.py`, `electronics.py`, and `wiring.py` for the harness bundles

## 2. The machine at rest (design-reading, machine-motion)

- [x] 2.1 Assemblies transcribing `full_assembly.scad`'s chains: the motor segment, X sled with the Y axis on it, Y sled, both axes, the towers, the lifter, the bridge with its extruder, the brace, the spool stand, the root
- [x] 2.2 Red first: the sleds ride their rails, the Z sleds their towers; the machine rests at the design's nought
- [x] 2.3 Build, snapshot, look

## 3. Motion and homing (machine-motion)

- [x] 3.1 Red first: driving X carries the sled, the Y axis and the bed and nothing else; Y the bed only; Z the bridge only
- [x] 3.2 Drivers `x`, `y`, `z` on the root, Z scaled by the acme lead; instructions `HomeX`, `HomeY`, `HomeZ`, `Rest`
- [x] 3.3 Measure where each axis first touches its switch and where each travel ends; record in `homing.py` with the firmware's figures beside them; red-then-green contracts at half a millimetre either side of each
- [x] 3.4 Instructions land where they say and take the firmware's time

## 4. The pinions (rack-and-pinion-drive)

- [x] 4.1 Red first: a tooth of travel redraws the pinion as it was; half a tooth turns it half a tooth
- [x] 4.2 Measure the sign and the least-overlap phase; `pinion.py`; the pinion turned in `MotorSegment.simulate()` through its `travel` port from both axes
- [x] 4.3 The relative engagement contract at six positions, and the slab contract at mid-tooth; record the herringbone drift

## 5. The lifter screws (lifter-screw-drive)

- [x] 5.1 Red first: the sockets threaded on their rods, clear at heights between pitches
- [x] 5.2 Measure the clearance window; `z_screw.PHASE`; rods and couplers turned through the towers' `screw` ports
- [x] 5.3 Contracts: the design's phase runs the thread through the sockets; the rods carry the bridge (free within the play, blocked beyond it); a whole turn lifts one lead; a quarter lead turns a quarter turn clockwise

## 6. The chains (cable-chain)

- [x] 6.1 Red first: each chain has the links its travel needs; the end links seat in their anchors at both ends of the travel; no link touches the machine
- [x] 6.2 `cable_chain.py`: the link count, the curve, the symbolic clamps, links placed in `simulate()`
- [x] 6.3 The strands: one molejo path per wire, per colour, at its hex offset, bound to the chain's split; contracts that they touch no link and no other strand and stay inside the chain

## 7. The filament (filament-path)

- [x] 7.1 Red first: the layer lies on the hub; the run passes through the brace's hole and ends at the inlet on the axis, clear of what it passes, at both ends of the Z travel; Z redraws the run and leaves the spool
- [x] 7.2 `filament.py`: helix, spline to above the brace, straight drop; the machine binds the two constant points and the inlet

## 8. Evidence and record

- [ ] 8.1 Full faceted regression on the root; the exact run once
- [x] 8.2 `solid build`; read `viewer.json` (drivers, instructions, flexible entries); snapshots at rest and homed, inspected
- [x] 8.3 `README.md` section: how to run it, what moves, what was found in the design
- [ ] 8.4 Sync the specs and archive the change, `Purpose` lines written
