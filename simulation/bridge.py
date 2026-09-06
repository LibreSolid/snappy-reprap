"""The bridge: the extruder between two arched spans, a Z sled on each
end, and the anchor of the chain that climbs the left tower.

``bridge_assembly_4`` of the design.  It is drawn about its own middle
with its Z sleds' threaded sockets at ``x = +-244``, and the machine
stands it between the towers and lifts it.
"""

from solid_node.math import cos, sin
from solid_node.node import AssemblyNode

from simulation import colors
from simulation.extruder import Extruder
from simulation.params import (
    bridge_arch_angle,
    cantilever_length,
    extruder_length,
    joiner_width,
    motor_rail_length,
    rail_length,
    rail_thick,
    z_joiner_spacing,
)
from simulation.part import ScadPart
from simulation.place import fwd, left, place, right, up, xrot, yrot, zrot
from simulation.rails import BridgeSegment
from simulation.scad import z_sled
from simulation.sled_parts import AdjustmentScrew
from simulation.chain_parts import ChainJoinerVerticalMount


#: The span from socket to socket, halved: where each Z sled stands.
REACH = (extruder_length + 2 * rail_length + 2 * cantilever_length) / 2

#: One arched segment's length along its own arch, and how high the
#: arch lifts the middle.
SEGMENT_LENGTH = rail_length / cos(bridge_arch_angle)
ARCH_OFFSET = rail_length * sin(bridge_arch_angle)

#: Where the Z sled's endstop adjustment screw threads in
#: (``bridge_assembly_3``).
SCREW_Y = z_joiner_spacing / 2 + 18
SCREW_Z = 22

#: Where the chain anchor snaps on (``bridge_assembly_2``).
ANCHOR_Y = z_joiner_spacing / 2 + 7


class ZSled(ScadPart):
    """A Z sled: threaded socket, sliders, and the joiners the bridge
    segment snaps into."""

    color = colors.MEDIUM_SLATE_BLUE

    def render(self):
        return z_sled.z_sled()


class Bridge(AssemblyNode):
    """The bridge, on its own middle, Z sled sockets on the x axis."""

    extruder = Extruder()
    segments = BridgeSegment().repeat(2)
    sleds = ZSled().repeat(2)
    screws = AdjustmentScrew().repeat(2)
    chain_anchor = ChainJoinerVerticalMount()

    # ``bridge_assembly_1`` also runs the extruder's harness down the
    # left span to the chain anchor; that path is one the design's
    # ``wiring()`` cannot sweep under OpenSCAD 2021.01 (see `wiring`),
    # so it is not here.

    def render(self):
        place(self.extruder, up(ARCH_OFFSET))
        for side, segment in zip((1, -1), self.segments):
            place(segment, up(ARCH_OFFSET), zrot(90 - 90 * side),
                  right(extruder_length / 2), yrot(bridge_arch_angle),
                  right(SEGMENT_LENGTH / 2), zrot(90))
        place(self.chain_anchor, up(ARCH_OFFSET), left(extruder_length / 2),
              yrot(-bridge_arch_angle), left(SEGMENT_LENGTH - 11),
              fwd(ANCHOR_Y), zrot(90))
        for side, sled, screw in zip((1, -1), self.sleds, self.screws):
            place(sled, zrot(90 - 90 * side), right(REACH), zrot(180))
            place(screw, zrot(90 - 90 * side), right(REACH), up(SCREW_Z),
                  fwd(SCREW_Y), xrot(180))
