"""Where each axis homes, how far it travels, and how long homing takes.

The firmware shipped beside the design homes all three axes to their
minimum -- ``X_HOME_DIR``, ``Y_HOME_DIR`` and ``Z_HOME_DIR`` are all
``-1`` -- and declares a travel of 198 mm for X and Y and 220 mm for Z.
Where the minimum IS, the firmware cannot say: it is wherever the
switch is, and the switch is where the printed parts put it.  So every
limit here is read off the metal, and the contracts in the root test
file hold it there.

Each home is the position at which the part that trips the switch
first touches its lever, in the design's own slide coordinates.  For X
it is the sled's rack-and-pinion hard stop -- the block on the left
joiner that also stops the sled running off the pinion -- reaching the
switch clipped beside the motor; for Y the same block on the near sled
endcap; for Z the adjustment screw threaded into the Z sled reaching
the switch at the top of each tower base.  A lever has to be pressed
a little further before the switch clicks, so a homed machine stands a
millimetre or two past each of these, which is why the firmware's 198
mm reach the far hard stop that stands 195 mm from first contact.

Each far end is where the travel physically ends.  X and Y end where
the other joiner's hard stop meets the pinion, which the design put
there for that purpose; Z ends where the top of the Z sled reaches the
top of the tower rails, which is the geometry's own ``rail_length -
rail_height/2``.  Beyond that the sliders leave the rails, and two
millimetres further the extruder motor clip meets the brace across the
towers.  The firmware's 220 mm of Z would go 13 mm past it.
"""

import math

from simulation import z_screw
from simulation.params import rail_height, rail_length


#: The design's own slide coordinate at which each axis first touches
#: its switch, measured on the built parts to a hundredth of a
#: millimetre: `test_each_axis_homes_onto_its_own_switch`.
X_HOME = -94.56
Y_HOME = -94.76
Z_HOME = -95.81

#: Where each travel physically ends: the far hard stop on the pinion
#: for X and Y, the top of the rails for Z.
X_MAX = 100.5
Y_MAX = 100.5
Z_MAX = rail_length - rail_height / 2

#: What the firmware believes the travel is, for the record.
FIRMWARE_XY_TRAVEL = 198.0
FIRMWARE_Z_TRAVEL = 220.0

#: The tick an instruction's duration is a whole number of, in seconds:
#: a simulation steps in whole ticks, and a duration that is not one
#: cannot be stepped.
TICK = 0.1


def homing_time(travel, rate):
    """How long an instruction has to cover `travel` at `rate`: the
    whole travel at the firmware's feedrate, rounded up to a tick so it
    never exceeds it."""
    return math.ceil(travel / rate / TICK) * TICK


#: How long each instruction has to cover its whole declared travel at
#: the firmware's homing feedrate for that axis.
X_HOMING_TIME = homing_time(X_MAX - X_HOME, z_screw.XY_HOMING_RATE)
Y_HOMING_TIME = homing_time(Y_MAX - Y_HOME, z_screw.XY_HOMING_RATE)
Z_HOMING_TIME = homing_time(Z_MAX - Z_HOME, z_screw.HOMING_RATE)
