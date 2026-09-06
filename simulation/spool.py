"""The spool stand on the right tower, its axle and the spool.

``final_assembly_6`` and ``_9`` of the design: the holder snaps onto
the top of the right tower, the axle cradles in its notches, and the
spool hangs on the axle.
"""

from solid_node.math import cos
from solid_node.node import AssemblyNode

from simulation import colors
from simulation.params import (
    rail_height,
    spool_axle_diam,
    spool_axle_drop,
    spool_holder_length,
)
from simulation.part import ScadPart
from simulation.place import down, place, right, up
from simulation.scad import spool_holder
from simulation.vitamins import Spool


#: Where the axle cradles above the holder's foot.
AXLE_Z = spool_holder_length - spool_axle_diam / 2 * cos(30) + 0.25


class SpoolHolder(ScadPart):
    color = colors.YELLOW_GREEN

    def render(self):
        return spool_holder.spool_holder()


class SpoolAxle(ScadPart):
    color = colors.YELLOW_GREEN

    def render(self):
        return spool_holder.spool_axle()


class SpoolStand(AssemblyNode):
    """Holder, axle and spool, the holder's foot on the origin."""

    holder = SpoolHolder()
    axle = SpoolAxle()
    spool = Spool()

    def render(self):
        place(self.axle, up(AXLE_Z))
        place(self.spool, up(AXLE_Z), down(spool_axle_drop))
