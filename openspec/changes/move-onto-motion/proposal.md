# Move the machine onto solid-node's motion layer

## Why

solid-node moved ports and the declared time base out of `solid_node.node`
into `solid_node.motion.ports`, with no re-export, and added two layers this
simulation predates: `solid_node.motion.joints` (a body's one freedom, stated
next to the body) and `solid_node.motion.couplings` (one coordinate drives
another, stated as a sentence in a class body). The layer does not import
today:

    ImportError: module 'solid_node.node' has no attribute 'TranslationalPort':
    ports and the declared time base moved to 'solid_node.motion.ports'.

Fixing the imports would make it run again, but it would leave the machine
described the long way round. Every freedom this printer has is written
today as a hand-composed transform in a `simulate()` — `self.sled.translate([-position, 0, 0])`,
`self.pinion.rotate(pinion.angle(travel), Z)` — and every transmission is
written as a chain of forwarding ports: the root's `x` reaches the X sled
through `XAxis.position`, the root's `y` reaches the bed through
`XAxis.bed` and `YAxis.position`, and the root's `z` reaches each rod
through `ZTower.screw` and `Lifter.angle`. Six of the eleven port
declarations in the layer exist only to carry a number one level down the
tree, and four classes hold a `simulate()` whose whole content is that
carrying.

The machine itself is simpler than that. It has seven moving bodies and
each has exactly one freedom: two sleds slide, one bridge lifts, two
pinions turn, two lifter screws turn. Every one of those is a lower pair on
one line, and every transmission between them is affine — a rack pitch, a
screw lead, an identity. This change says the machine that way: a joint on
each body that moves, a `drives` sentence for each transmission, and no
port whose only job is forwarding.

Nothing about the pose changes. The acceptance is that every leaf's world
matrix is identical at every pose, before and after.

## What changes

### Imports (stage A, before any motion work)

`Port`, `RotationalPort`, `TranslationalPort` and `Time` come from
`solid_node.motion.ports`. Seven modules import a moved name:
`cable_chain.py`, `filament.py`, `x_axis.py`, `y_axis.py`,
`motor_segment.py`, `tower.py`, `lifter.py`. No test module imports a moved
name, so `simulation/test_snappy_reprap.py` is not touched in stage A.

### The joints: five declarations, seven realized freedoms

Each is stated in the parent's frame, as the joints spec requires. The
happy fact about this machine is that **no joint needs an `at`**: every
rotation axis here is its own parent frame's z axis through that frame's
origin, and a prismatic's anchor does not affect its placement at all. So
none of these declarations repeats a placement constant its parent already
holds, and the known "a joint cannot be anchored at a design-placed part's
own placed origin" limit does not bite.

| Class (file) | Declaration | Where the numbers come from |
|---|---|---|
| `XSled` (`x_sled.py`) | `travel = Prismatic(axis=(-1, 0, 0), unit='mm')` | `x_axis.py:134`, `self.sled.translate([-self.position.value, 0, 0])`: the design's `xslidepos` counts how far the sled stands to the LEFT, so the sled's own line is the machine's −x. The sled is placed by `up(SLED)`, a pure translation, so the axis carries into its own frame unchanged. |
| `YSled` (`y_sled.py`) | `travel = Prismatic(axis=(0, -1, 0), unit='mm')` | `y_axis.py:96`, `self.sled.translate([0, -self.position.value, 0])`: `yslidepos` counts forward, along −y. Placed by `up(SLED)`. |
| `Bridge` (`bridge.py`) | `lift = Prismatic(axis=(0, 0, 1), unit='mm')` | `snappy_reprap.py:222`, `self.bridge.translate([0, 0, lift])`. Placed by `up(BRIDGE_Z)`. |
| `Pinion` (`motor_segment.py`) | `spin = Revolute(axis=(0, 0, 1), unit='deg')` | `motor_segment.py:93`, `self.pinion.rotate(..., Z)`. The pinion is placed `up(motor_top_z + GEAR_SEAT), zrot(-90)`; the gear's bore IS the segment frame's z axis, so the default anchor names the right line. |
| `LifterScrew` (`lifter.py`) | `spin = Revolute(axis=(0, 0, 1), unit='deg')` | `lifter.py:96`, `self.screw.rotate(self.angle.value, Z)`. Placed `up(COUPLER_SEAT)`; the coupler's axis is the lifter frame's z axis. |

Two of the five are realized twice (`Pinion` in the X and the Y motor
segment; `LifterScrew` in the left and the right tower), so the machine has
seven freedoms and three drivers.

**No joint declares a `range`.** This is deliberate and is the one place
where a plausible reading of "state the machine fully" would turn two green
tests red — see **Tests**. The ranges belong to the drivers, which already
carry them and which never clamp; the joints' ranges would be checked and
refused, and the contracts deliberately drive half a millimetre past both
ends of every travel to prove where the hard stops are.

For the two revolutes the framework will carry the parent-frame anchor
`(0, 0, 0)` into the node's own frame as a pure-z vector and emit
`translate(-anchor)`, `rotate`, `translate(anchor)` instead of the single
`rotate` written by hand today. A rotation about z fixes a z vector
exactly, so the composition is bit-identical to today's single rotation;
only the operation list in the published document is two entries longer.

### The relations: ten sentences, no derived coordinates

Every sentence names the coordinate at both ends.

**On `SnappyReprap`** (the root, whose three drivers are the bound ends):

1. `x.drives(x_axis.sled.travel)` — identity. The X driver *is* the sled's
   travel: the design's `xslidepos` in millimetres, and the sled's joint
   axis carries the "to the left" sign, so no ratio is wanted. Replaces
   `connect(self.x, self.x_axis.position)` and the translate below it.
2. `y.drives(x_axis.sled.y_axis.sled.travel)` — identity. Four declared
   children down; replaces the two forwarding ports `XAxis.bed` and
   `YAxis.position` and `YAxis`'s translate.
3. `z.drives(left_tower.lifter.screw.spin, offset=z_screw.PHASE)`
4. `z.drives(right_tower.lifter.screw.spin, offset=z_screw.PHASE)` —
   ratio 1, offset `z_screw.PHASE` (= `DESIGN_PHASE + 193.5` = 103.5 deg,
   the design's own `-90` plus the measured turn that puts the rods' thread
   in the middle of the sockets' clearance, `z_screw.py`). Replaces
   `screw = self.z + z_screw.PHASE` and its two `connect`s, plus
   `ZTower.screw` → `Lifter.angle` → `rotate`.
5. `z.drives(bridge.lift, ratio=z_screw.SCALE)` — `SCALE = -LEAD/360`
   = −8/360 mm of bridge per degree of rod, the negative being the
   design's right-handed acme thread lifting its nut for a clockwise turn
   seen from above (`z_screw.py`). Replaces `lift = z_screw.lift(self.z)`
   and `self.bridge.translate([0, 0, lift])`.
   The registration `PHASE` is deliberately NOT in this ratio's offset: the
   phase lines the thread up with the sockets and lifts nothing, which is
   why the rods are driven with it and the bridge without it, exactly as
   today.
6. `bridge.lift.drives(z_chain.offset, offset=Z_CHAIN_OFFSET)` — identity
   ratio; `Z_CHAIN_OFFSET = -rail_height / 2` (`snappy_reprap.py`), where
   the chain's moving anchor stands relative to the bridge. Replaces
   `connect(lift + Z_CHAIN_OFFSET, self.z_chain.offset)`. Stated from the
   bridge rather than from `z` because that is the machine: the chain
   follows the bridge. Both ends are the root's own coordinates and the
   solver's fixpoint runs relations repeatedly until nothing changes, so
   `bridge.lift` being itself driven by (5) is not an ordering problem.
7. `bridge.lift.drives(filament.head, offset=INLET_IN_STRAND[0])` — identity
   ratio. `INLET_IN_STRAND = in_strand_frame([0, 0, INLET_Z], STRAND_ORIGIN)`,
   a new module constant that is exactly today's `head` expression with the
   `lift` term taken out: `head[0] = lift + (INLET_Z - STRAND_ORIGIN[2])`,
   and `in_strand_frame` stays the one place the strand's frame permutation
   is written. Replaces `connect(head[0], self.filament.head)`.

**On `XAxis`:**

8. `sled.travel.drives(segment.pinion.spin, ratio=pinion.DEGREES_PER_MM,
   offset=pinion.PHASE)` — the rack under the sled turns the pinion.
   `DEGREES_PER_MM = SIGN * 360 / MM_PER_TURN` is a new constant in
   `pinion.py` replacing the body of `angle()`; `MM_PER_TURN =
   gear_teeth * rack_tooth_size` (the 24-tooth herringbone pinion on its
   rack's pitch, 80 mm, which is also Marlin's 40 steps/mm), `SIGN = 1` and
   `PHASE = 14.25` deg are both measured off the metal and held there by
   the engagement contracts. The X motor segment stands `zrot(-90)`, whose
   own −y is the machine's −x, so the sled's travel is the travel `SIGN`
   was measured for, and z is common to both frames so the angle needs no
   conversion.
9. `sled.travel.drives(chain.offset)` — identity. The X cable chain's split
   between its two runs is the sled's own position. Replaces
   `connect(self.position, self.chain.offset)`.

**On `YAxis`:**

10. `sled.travel.drives(segment.pinion.spin, ratio=pinion.DEGREES_PER_MM,
    offset=pinion.PHASE)` — the same sentence with the same constants. The
    Y motor segment stands unturned and its own −y is the sled's forward,
    so the mesh reads identically. The law is stated once, in `pinion.py`;
    the sentence is stated in each axis because only an axis class holds
    both the rack (on its sled) and the pinion (on its segment).

**Derived coordinates: none.** Nothing here is a linear formula over two
coordinates. `z + PHASE` is one relation's offset, not a coordinate of the
machine.

### What shrinks or disappears

- `XAxis.position` and `XAxis.bed` — deleted. Pure forwarders.
- `YAxis.position` — deleted. Pure forwarder.
- `MotorSegment.travel` — deleted, with `MotorSegment.simulate()` and the
  module's now-unused `from simulation import pinion` and `Z` import. The
  segment becomes placement only; its pinion carries the freedom.
- `ZTower.screw` — deleted, with `ZTower.simulate()`.
- `Lifter.angle` — deleted, with `Lifter.simulate()`.
- `XAxis.simulate()` and `YAxis.simulate()` — deleted entirely.
- `SnappyReprap.simulate()` — from twelve lines to four: the four
  filament port bindings that are constants of the machine
  (`high_x`, `above_x`, `axis_y`, `axis_z`). They are not transmissions —
  nothing drives them — so they stay `connect()`s of module constants
  (`HIGH_IN_STRAND`, `ABOVE_IN_STRAND`, `INLET_IN_STRAND`), each read
  through `in_strand_frame` exactly as today.
- `pinion.angle()` — deleted, replaced by `DEGREES_PER_MM`. Nothing else
  imports it (the tests read `pinion.MM_PER_TURN` only). `z_screw.angle()`
  and `z_screw.lift()` STAY: the test suite's `drive()` helper and the
  homing contract both call them.
- The two hand-written sign inversions (`[-position, 0, 0]` and
  `[0, -position, 0]`) leave: the sign is now the joint's axis, stated once
  where the body is.

### Ports that stay, and why

Every remaining port feeds molejo geometry and is read by the node that
declares it to build a flexible shape. None is a forwarder.

- `CableChain.offset` — the chain's own state: the split of its length
  between the two runs. Read by `CableChain.simulate()` to place nineteen
  links and to bind the wires.
- `Wire.bottom`, `Wire.top_end`, `Wire.bend`, `Wire.span` (four per strand,
  eighteen strands) — molejo path parameters, bound per copy from the
  chain's own curve.
- `Filament.high_x`, `above_x`, `head`, `axis_y`, `axis_z` — molejo path
  parameters. `head` becomes the driven end of relation (7); the other four
  stay constants bound in the root's `simulate()`.

## What does not change

- The three drivers `x`, `y`, `z`, their units, ranges, `z`'s `scale`, and
  the four instructions `HomeX`, `HomeY`, `HomeZ`, `Rest`.
- Every `render()`: no placement, colour, part, or dimension moves. The
  OpenSCAD design is not touched, and `params.py` still probes it.
- The cable chains' link stations and wire paths, the filament's helix and
  spline, and every `.scad` module call.
- The test file: no assertion, tolerance or measured constant is proposed
  for change (see **Tests**).
- The project's baseline specs. `machine-motion`, `rack-and-pinion-drive`,
  `lifter-screw-drive`, `cable-chain`, `filament-path` and `design-reading`
  describe what the machine does, not how the layer wires it, and none of
  them names a port. This change is behaviour-preserving, so it proposes no
  spec delta.
- `README.md`'s account of the machine is still true; it gains one sentence
  saying the freedoms are joints and the transmissions relations.

## Known gaps

Of the three known limits of the motion layer recorded in
`solid-node/workflow/warts.md` (2026-09-09):

- **A joint cannot be anchored at a design-placed part's own placed
  origin** — does not bite. Every rotation axis in this machine is its
  parent frame's own z axis, so the default anchor is right and no joint
  repeats a placement constant. Worth reporting as the counter-example to
  the poseidon/openarm sightings.
- **A relation chain must be stated in one class body** — does not bite.
  Every chain here runs downwards from a root driver, and an ancestor's
  relation binds a descendant's coordinate before the descendant solves, so
  the two axis-local sentences (8, 9, 10) have their driver end already
  bound when they run.
- **A node's own derived coordinate is unbound inside its own
  `simulate()`** — bites once, and is designed around: the root can no
  longer read the bridge's height inside its own `simulate()`, because a
  coordinate the root's relations bind is not bound until after
  `simulate()` returns. That is why the filament's moving inlet is stated
  as relation (7) rather than as a `connect` of an expression. No
  hand-written motion survives because of it.

What stays hand-written, and why:

- **The cable chains' nineteen links.** Each link stands at its own station
  along a piecewise curve — a straight run, a half turn on the anchors'
  radius, a straight run — clamped with `min`/`max` and placed with a
  position AND a facing angle. That is not one coordinate on one line, so
  no joint states it; and the links are `.repeat()` children, which a
  relation may not fan out over. This is the third sighting of
  fender-bender's wanted `Path(...)` joint and the third of OpenCycloid's
  wanted fan-out, from a cable chain rather than a bracket or a bearing.
  The sentence the project would want is
  `sled.travel.drives(chain.links.station, law=chain_curve)`, the law
  handed each copy so it can read its index. It is dressing that follows
  the principal axes, not the machine's own transmission, so under the
  campaign's deferral rule it does not defer the project.
- **The eighteen wire strands' four molejo parameters each**, bound in a
  loop over list-held children in `CableChain.simulate()` — the Pascaline's
  list-held fan-out, second sighting. They feed molejo geometry and stay
  ports whatever happens to the fan-out primitive.

**No new framework limit was found, and deferral is not recommended.** The
principal motion of this machine — three axes, two rack-and-pinion drives,
two lifter screws and the bridge they carry — is fully statable with the
motion API as it stands.

One arithmetic caveat the reviewer should decide, because it decides the
pose evidence:

- Relations (5), (8) and (10) re-associate a product. Today the layer
  computes `-(LEAD * z / 360)` and `SIGN * 360 * travel / MM_PER_TURN + PHASE`;
  `Affine` will compute `(-LEAD/360) * z` and `(SIGN * 360 / MM_PER_TURN) * travel + PHASE`.
  Those differ by up to one ulp: measured for the Z lead, `z = 52` gives
  `-1.1555555555555557` against today's `-1.1555555555555554`, about
  3e-16 mm. `MM_PER_TURN` is probed from `config.scad` to six decimals, so
  it is 80 only to the probe's precision and the pinion ratio is not exact
  either. Every test tolerance here is 0.001 mm or looser, so nothing goes
  red; but the pose comparison will report a maximum deviation of order
  1e-13 rather than 0 on the Z-carried leaves and the two gears.
  This proposal takes `ratio=`/`offset=`, which is what the driving
  contract asks for when a law is affine, and accepts the explained
  deviation. **If the review wants max deviation 0**, the alternative is to
  keep the exact expressions behind `law=`: a two-method law object in
  `z_screw.py` whose `forward` is `lift()` and whose `inverse` is
  `angle()`, and one in `pinion.py` whose `forward` is today's `angle()`,
  each returned by a one-line callable of the two realized nodes. That is
  bit-exact and still deletes every forwarding port; it is heavier and
  against the contract's stated preference. The implementer should not
  choose: the reviewer should.

## Pre-existing state

The repository is **clean**: branch `master` at `18fd943` ("refactor(simulation):
take the chain's clamps and the Z screw's law from the framework"), no
modified, staged or untracked files. Stage 0 of the protocol is therefore a
no-op here — there is nothing to commit before the refactor begins.

## Tests

`simulation/test_snappy_reprap.py` is the whole suite: 27 contracts in one
`TestCase`, run as `solid test --faceted simulation/snappy_reprap.py`.
There is no pytest-only suite. Every contract poses the machine through
`drive()`, which calls `set_state` on the three drivers (converting a Z
height to rod degrees with `z_screw.angle`), and then measures meshes.
**No test reads a port, a joint, or `declared_ports`; no test imports a
name that moved.** That is why none is proposed for change.

What they assert, in groups:

- *At rest* — `test_the_machine_rests_where_the_design_draws_it`, and that
  each sled rides its rails clear (`..._x_sled_rides...`, `..._y_sled...`,
  `..._z_sleds_ride_the_tower_rails`).
- *What each driver moves* — three contracts naming a carried set and a
  still set and asserting the exact displacement of each. These are the
  direct test of relations (1), (2), (5) and of the tree that carries them.
- *The pinions* — one tooth of travel per tooth of rack, the phase held
  across the travel, and the slab test. The direct test of (8) and (10).
- *The lifter rods* — sockets threaded on the rods at heights between
  pitches, the design phase proved wrong, the rods carrying the bridge, a
  whole turn lifting one lead, and a quarter lead turning the rods −90°.
  The direct test of (3), (4), (5).
- *Homing and hard stops* — first contact with each switch and each end of
  travel, the instructions landing on their targets, and homing taking the
  firmware's time.
- *The chains and the filament* — link counts, seating, spacing, the wires
  inside, the layer on the hub, the run through the brace, and the
  published document.

Three to watch, none of which I propose changing:

1. **`test_each_axis_homes_onto_its_own_switch` and
   `test_each_travel_ends_on_its_hard_stop`** drive deliberately past both
   ends of every travel: `X_HOME - 0.5`, `X_MAX + 0.5`, `Y_HOME - 0.5`,
   `Y_MAX + 0.5`, `Z_HOME - 0.5`, `Z_MAX + 4.0`. A joint's declared `range`
   is checked and refused by name on a numeric binding, so declaring
   `range=(X_HOME, X_MAX)` and friends on the five joints would turn both
   of these red — and they are proving exactly the thing a range would
   assert. Hence no `range=` on any joint. If the reviewer wants the ranges
   declared, those two contracts have to change, and that is the
   orchestrator's call, not the implementer's.
2. **`test_the_flexible_parts_travel_into_the_viewer_as_shapes`** asserts
   `'z' in flexible['filament']['params']['head']` and
   `'x' in flexible['x_axis.chain.strands-0']['params']['bottom']`: the
   driver's name must still reach the molejo parameters as an unresolved
   expression, now through two chained `Affine`s (5)→(7) and through
   (1)→(9)→`CableChain.simulate()`. The couplings spec says values pass
   through a relation unresolved, so this should stay green; if it does
   not, it is the framework's behaviour that is wrong, not the contract,
   and the implementer should stop and report it.
3. **`test_the_design_phase_would_run_the_thread_through_the_sockets`** is
   the one contract that moves a jointed body by hand: it
   `save_checkpoint()`s the `LifterScrew`, rotates it by
   `DESIGN_PHASE - PHASE`, measures, and restores. The joints spec says
   joint motion and hand-written motion coexist on one node and apply in
   the order applied, and the joint's own binding now happens in the ROOT's
   simulate phase rather than in `Lifter`'s. Expected green; worth naming
   in the report either way.
