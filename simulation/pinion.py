"""What the XY drive gears do: sled travel into turns.

Snappy drives X and Y by rack and pinion.  Each motor rail segment
cages a stepper whose 24-tooth herringbone pinion meshes with the
herringbone rack on the underside of the sled riding that segment, so
when the sled travels the pinion turns, and by exactly the rack's
pitch: one tooth of travel is one tooth of turn.  The design draws the
pinion standing still under a moving rack.  Here it turns.

`MM_PER_TURN` is the rack's pitch times the pinion's teeth, 80 mm, and
it is also what Marlin's 40 steps per millimetre say: 3200 microsteps a
turn over 80 mm.

`SIGN` and `PHASE` are measured off the metal rather than reasoned
out.  The sign is which way the pinion goes round for a sled going
+y in the segment's own frame; the phase is the angle at which the
pinion's teeth stand in the rack's gaps with the sled at nought.  Both
are asked for by the engagement contracts in the root test file, so
neither can drift from the geometry unnoticed.

One thing about the mesh is worth knowing before reading those
contracts.  The design draws a herringbone pair: the pinion is an
involute gear extruded with a twist, the rack a straight rack skewed
by the same angle, and at any one height the two interleave cleanly --
a millimetre-thick slab of them at the meshing phase shares four
hundredths of a cubic millimetre, and a half tooth off shares seven.
Over the whole fifteen millimetres of tooth they do not quite: a
twisted extrusion is not a helical tooth, and the pair's chevrons do
not stand at exactly the same height, so the flanks drift a fraction
of a degree apart along the tooth and the whole pinion shares some
forty-five cubic millimetres with its rack at the best phase, fifty-
three at the worst.  That is the design's own geometry -- the author's
shipped STLs are the same to a micron -- and on the machine it is what
``printer_slop`` and a drop of oil are for.  The phase here is where
that overlap is least, and the contracts ask that it stay least as the
sled travels.
"""

from simulation.params import gear_teeth, rack_tooth_size


#: Millimetres of rack per turn of the pinion.
MM_PER_TURN = gear_teeth * rack_tooth_size

#: Which way the pinion turns, seen from above, for a sled going
#: forward, along -y in the motor segment's frame: counter-clockwise,
#: with the rack passing on the pinion's +x side.
SIGN = 1

#: The angle at which the pinion's teeth sit in the rack's gaps with
#: the sled at nought, in degrees: where the pair shares least metal
#: over one tooth pitch, found to a quarter of a degree.
PHASE = 14.25


def angle(travel):
    """The pinion's angle, in degrees, for a sled `travel` mm forward."""
    return SIGN * 360 * travel / MM_PER_TURN + PHASE
