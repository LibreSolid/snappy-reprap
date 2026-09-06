## Why

The repository holds Revar Desmera's OpenSCAD design of the Snappy RepRap 3
and nothing that runs it. `full_assembly.scad` draws the whole printer for
one set of slide positions and `full_rendering()` sweeps them with `$t`, but
what it draws is a picture of a pose: the pinions stand still under racks
that slide over them, the lifter rods are turned by a constant the design
writes down, the cable chains are redrawn with a different number of links
at every position, and the wires through them and the filament the machine
eats are not drawn at all. A maker opening the design cannot slide an axis,
home it, or see whether the parts that carry each other really do.

What physically goes wrong today, read off the design's own geometry under
OpenSCAD 2021.01:

- The lifter rods' thread runs through the Z sleds' sockets at every height
  when the rods are turned as `lifter_assembly_5` turns them (`-90`
  degrees); the sockets clear the rods only for rods turned 174 to 213
  degrees further.
- The pinions do not turn, so nothing shows whether a tooth stands in a gap
  of the rack, and over the whole tooth the herringbone pair shares some
  forty-five cubic millimetres at its best phase -- the pinion's twisted
  extrusion and the rack's skew drift apart along the tooth.
- Four of the design's harness runs -- the extruder motor's, the bridge's,
  and the bridge harness down the left tower with its pigtail -- render as
  nothing: `wiring()`'s fillet yields `[nan, nan, nan]` on those paths.
- The firmware's travels (198 mm in X and Y, 220 mm in Z) overrun the
  parts: the pinion hard stop stands 195 mm from where the X switch is
  first touched, and 220 mm of Z would carry the Z sleds off their rails
  and the extruder motor clip into the brace.

## What Changes

- A solid-node package `simulation/` reads the unchanged .scad sources as a
  machine: every part a builder handles is one leaf calling the design's
  own module, coloured as the design paints it; every group snapped together
  before it goes into something bigger is an assembly; every dimension
  comes from `config.scad`, probed once at import.
- Three drivers on the root, in the design's own slide coordinates, with
  independent `HomeX`, `HomeY` and `HomeZ` instructions that run each axis
  to its own switch at the firmware's homing feedrate for that axis, and
  `Rest` back to the drawn pose.
- What the design leaves standing still under a moving part now moves with
  it: each pinion turns with its rack at the rack's pitch, the lifter rods
  turn as the bridge rises at the acme lead, the rods and couplers turning
  together and the bridge hanging at what their angle is worth.
- The cable chains are chains: a fixed number of links (nineteen each,
  where the design's text says thirteen or fourteen and eighteen), each
  placed along the one curve a chain of that length makes between its
  anchors, and the wires through them drawn as flexible leaves bound to
  the same curve.
- The filament is drawn: a layer on the spool's hub and the free run from
  it, through the hole the brace centre is cut with, straight down into the
  extruder, redrawn wherever the bridge stands.
- Every home and every end of travel is measured off the metal and held by
  a contract; the firmware's figures are recorded beside them.

Not in this change, and deliberately:

- **No edit to the .scad sources.** The Z phase constant, the herringbone
  drift, the four unrenderable harnesses and the overrunning travels are
  the design's; each is recorded where it is met and corrected only in the
  layer's own placement (the phase) or its own statements (the travels).
  Changing the design is the pilot's call.
- **No E axis.** The filament is drawn loaded and still; feeding it is a
  fourth driver and a spool that turns, which the pilot has not asked for.
- **The four harness runs `wiring()` cannot sweep** stay out rather than be
  redrawn by hand.

## Capabilities

### New Capabilities

- `design-reading`: what the layer reads from the OpenSCAD design and how --
  a leaf per module, the design's colours, `config.scad` as the one source
  of dimensions, and the design's sources as every leaf's rebuild
  dependency.
- `machine-motion`: the three drivers, what each moves, and homing --
  where each axis meets its switch and its hard stop, and how long getting
  there takes.
- `rack-and-pinion-drive`: the pinion under each rack turning with it, at
  the rack's pitch, standing in its gaps.
- `lifter-screw-drive`: the Z sleds threaded on the lifter rods, the rods
  turning with the bridge's height at the acme lead, the bridge carried by
  the thread.
- `cable-chain`: the two chains as chains of links between their anchors,
  with the wires through them as flexible strands.
- `filament-path`: the strand on the spool and its run into the extruder.

## Impact

- New: `pyproject.toml`, `simulation/` (thirty modules), `simulation/
  test_snappy_reprap.py`, `openspec/`.
- Unchanged: every `.scad`, `STLs/`, `firmware/`, `docs/`.
- No framework change is needed; the layer uses `Solid2Node`,
  `AssemblyNode`, `MolejoNode`, `Driver`, `Instruction`, the ports and the
  declared parameter kinds as the solid-node API publishes them.
