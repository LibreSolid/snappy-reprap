## Context

Snappy is designed in OpenSCAD: forty-odd `*_parts.scad` files, each one
printed part as a module, `config.scad` with every dimension, `vitamins.scad`
and `NEMA.scad` with the bought parts, and `full_assembly.scad` with the
build order as nested assembly modules that take the three slide positions.
The layer is a second reading of that: a solid-node tree in `simulation/`
that calls those modules and says where each goes and what moves. The
machine's frame is `full_assembly.scad`'s: the X rail's motor segment at the
origin, X along the rail, Z up.

## Goals / Non-Goals

**Goals:**

- One leaf per part, calling the design's module; the layer adds nothing a
  module already draws.
- Every dimension read from `config.scad`, none restated.
- Three drivers with independent homing; every mover moving.
- Everything that is a function of machine state drawn as a function of it:
  the pinions, the rods, the chains, the wires through them, the filament.
- Every claim held by a contract that runs red before the placement that
  satisfies it.

**Non-Goals:**

- Correcting the design. Its defects are recorded and worked around only
  in the layer's own numbers.
- Whole-model interference and connectivity contracts, which the design's
  nested chain links, wires through walls and multi-body bought parts
  cannot pass.
- An E axis, a turning spool, or the four harness runs OpenSCAD cannot
  sweep.

## Decisions

**Leaves call modules; the design's transform chains are transcribed left
to right.** `place(node, up(a), zrot(b), ...)` takes the words the design
writes and appends them innermost first, so every placement can be checked
against `full_assembly.scad` line by line. Rejected: composing matrices by
hand, which is where transcription errors hide.

**Dimensions are probed, not restated.** `params.py` reads every top-level
name off `config.scad` by regular expression and asks OpenSCAD what each
evaluates to, once, at import. A value the design writes inside a module
body is restated once with the module named. Rejected: a hand-kept table,
which drifts.

**Colours are the modules' own.** Each leaf carries the hex of the
`color()` its module calls; an unpainted module carries OpenSCAD's default
face colour; a bought part drawn in several colours carries the colour of
the most of it; the design's seventeen wire colours are kept in order and a
bundle takes its first wire's. Filament, which the design never draws, is
natural PLA.

**Z's state is the rods' angle.** `z = Driver(scale=-lead/360)`: negative
because the design's own `lifter_assembly_5` turns the rods by
`-360*slidepos/pitch`, a right-handed acme thread lifting its nut clockwise
from above. The maker sees millimetres; the rods see degrees.

**The Z phase is measured, not the design's.** The rods and the sockets
are cut by the same `acme_threaded_rod` about their own centres; the design
turns the rods `-90` degrees to line them up, and under this OpenSCAD that
leaves the thread through both sockets at every height (about 1600 mm^3
shared). Sweeping the extra turn at Z nought and at five heights between
pitches, the sockets clear the rods for 174 to 213 degrees more; the layer
turns them 193.5 more, the middle of that window, and the contracts hold
the sockets clear at heights between pitches and blocked 0.7 mm along the
axis. Rejected: deriving the phase from the two centres' distance, which
gives 108 degrees by one reading and needs the polyhedron's own flank
offsets to close; the measured window is the fact.

**The pinion's phase is where the pair shares least, and the contract is
relative.** In a millimetre-thick slab at mid-tooth the pair interleaves
cleanly at the phase (0.04 mm^3) and collides a half tooth off (7 mm^3);
over the whole tooth it shares 45.6 mm^3 at best and 52.8 at worst, because
the pinion is an involute extruded with a twist and the rack a straight
rack skewed, and their flanks drift apart along the tooth. The author's
shipped STLs are the same geometry to two microns, so it is the design's.
The layer turns the pinion to the least-overlap angle, 14.25 degrees at
nought, and the contract asks that the overlap stay under 46 mm^3 at every
position of X and rise a quarter tooth either way, and that a slab at
mid-tooth be clean. The Y sled's halves stand half a millimetre apart
where the X sled's touch, so the Y racks are a quarter of a millimetre out
of pitch either way and the Y pinion, in phase with the pair, is 2.7
degrees out with each half alone: 48.3 mm^3 at the ends of its travel,
which its bound of 49 records. Rejected: a zero-
overlap contract, which no phase satisfies; and turning the pinion over,
which was tested and shares 2600 mm^3.

**Homes and ends are first contact, measured to a hundredth.** X and Y
home where the hard-stop block on the near joiner or endcap first touches
the switch lever (-94.56 and -94.76 mm); they end where the far block meets
the pinion (100.5 mm). Z homes where the adjustment screw meets the tower
switch (-95.81 mm) and ends where the Z sled's top reaches the top of the
rails (`rail_length - rail_height/2`, 111 mm); the extruder motor clip
meets the brace centre 2 mm further. The firmware's 198 and 220 mm are
recorded beside these. Rejected: the firmware's figures as the ranges,
which overrun the parts.

**A chain has the links its travel needs.** `ceil((pi*R + reach)/pitch)
+ 2` with `R` half the anchors' height difference, `reach` the farthest
the two runs differ over the travel, and the two a whole link lying
straight in each anchor at either end of the travel: 19 links for X and
19 for Z. The design's assembly text says 13 or 14 and 18; its own module
draws 15 at the end of the X travel and skips the moving run. Each link stands at its own
station on the run-bend-run curve, facing along it, turned over on the
moving run as the design turns them; the split of the chain between the two
runs is linear in the sled's position, and the clamps that decide which run
a link is on are `sqrt(x*x)` so the whole motion is one symbolic
expression the viewer can take. Rejected: placing pins on the circle as a
polygon, which needs the design's `ceil` and does not close.

**Wires through a chain are one molejo path each.** Line, half-turn arc,
line, in a frame whose +z runs out from the fixed anchor; each wire at its
hex-packed offset, with its own bend radius bound as a port because a molejo
parameter is a plain number. Colours are the design's table, one class per
colour.

**The filament goes through the brace's hole.** The brace centre is cut
with a 10 mm filleted hole on the machine's axis, which is the design saying
where the strand goes. The run leaves the top of the hub, curves until it is
coming straight down on the axis 40 mm above the brace, and drops through
the hole to the inlet at the top of the idler arm's bar. Rejected: passing
beside the brace, which was drawn first and met the brace centre at the top
of the Z travel.

**The four harness runs `wiring()` cannot sweep are left out.** Tested in
the design's own context, nudged and unnudged: `[nan, nan, nan]` fillet
points on all four. A leaf with no geometry is worse than an absent one.

## Risks / Trade-offs

- The pinion contract is relative, so a design that meshed cleanly would
  need it tightened; recorded in `pinion.py`.
- The chain's links are placed by their centres on the curve, so in the bend
  their pins stand a fraction of a millimetre inside their neighbours'; the
  design's bend fudges the same amount the other way.
- The test kernel is faceted for every OpenSCAD part; the exact kernel
  serves only the flexible leaves. Contacts are read at 0.1 mm tessellation.

## Migration Plan

None: a new package beside an untouched design.

## Open Questions

- Whether to correct the design's Z phase constant and its assembly text's
  link counts in the .scad sources: the pilot's call.
- Whether the herringbone drift is worth a real helical tooth in the design.
