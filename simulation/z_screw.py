"""What the lifter screws do: turns into height, and height into turns.

The bridge does not float at a height somebody typed in.  It hangs on
two printed acme nuts, one in each Z sled, each threaded onto a
printed lifter rod that a stepper below it turns; the bridge is where
it is because the rods have been turned that far.  This module is that
sentence as arithmetic, in one place, because the machine, both towers
and the bridge all need it and none of them may reach a different
answer.

`SCALE` is the whole of it.  The Z driver's state is the rods' own
angle in degrees, and `SCALE` is what a degree of it is worth in
millimetres of bridge.  It is NEGATIVE, and the design says so:
``lifter_assembly_5`` turns the rods by ``-360*slidepos/lifter_rod_pitch``,
a right-handed acme thread that lifts its nut when turned clockwise
seen from above, and clockwise from above is a negative rotation about
Z.

`PHASE` is the other half of the same fact, and it is what makes the
socket a nut rather than a ring around a rod.  The rods and the sockets
are cut by the same ``acme_threaded_rod``, each about its own centre,
and they are different distances up the machine, so their threads only
line up if the rods are turned by the difference read as an angle.
The design writes that turn down as the ``-90`` on the same line, and
under this OpenSCAD that is half a turn out: at ``-90`` the rods'
thread runs through the sockets' at every height, and the sockets
clear the rods only for rods turned between 174 and 213 degrees
further.  `PHASE` is the middle of that window, measured off the metal
and held there by the root's contracts.  It does not change as the
machine moves, so it is a constant and not a term of the lift, and the
towers are told the driver plus this.

`HOMING_RATE` is Marlin's own Z homing feedrate for this machine, 4
mm/s (``HOMING_FEEDRATE_Z (4*60)`` in the firmware shipped beside the
design), which is 30 rpm at this lead.  Homing Z takes the time that
rate takes: this is a screw, not a rack, and the interface should show
a maker the difference.
"""

from solid_node_mechanics import screw_angle, screw_travel

from simulation.params import lifter_rod_pitch


#: How far one turn of a rod raises the bridge: an 8 mm single-start
#: acme thread, so the lead is the pitch.
LEAD = lifter_rod_pitch

#: Millimetres of bridge per degree of rod -- see the module docstring
#: for the sign.
SCALE = -LEAD / 360

#: How far the rods are turned from their own drawn phase to meet the
#: sleds' sockets: the design's ``-90`` plus the 193.5 degrees that put
#: the thread in the middle of the sockets' clearance -- see the module
#: docstring.
DESIGN_PHASE = -90.0
PHASE = DESIGN_PHASE + 193.5

#: What a Z axis homes at, in millimetres a second, and what X and Y
#: home at: Marlin's ``HOMING_FEEDRATE_XY (50*60)``.
HOMING_RATE = 4.0
XY_HOMING_RATE = 50.0


def angle(height):
    """The rods' angle, in degrees, that holds the bridge at `height`.

    The framework's own screw law, ``screw_angle``, inverted: this
    design's thread lifts the bridge when the rods turn clockwise seen
    from above, and clockwise from above is a negative rotation about
    the rods' own axis -- see the module docstring's account of `SCALE`.
    """
    return -screw_angle(height, LEAD)


def lift(turned):
    """The height, in millimetres, that rods `turned` that many degrees
    hold the bridge at.

    The framework's own screw law, ``screw_travel``, with the same
    explicit minus as `angle` -- see the module docstring.
    """
    return -screw_travel(turned, LEAD)
