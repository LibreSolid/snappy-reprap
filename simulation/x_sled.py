"""The X sled: two halves, two joiners, the chain anchor, and the whole
Y axis standing on top.

``x_axis_assembly_4`` and ``_7`` of the design; the Y axis is snapped
onto the joiners in ``x_axis_assembly_6``.
"""

from solid_node.node import AssemblyNode
from solid_node.motion.joints import Prismatic

from simulation.params import (
    groove_height,
    joiner_width,
    platform_length,
    platform_width,
    rail_offset,
)
from simulation.place import fwd, left, place, right, up, yrot, zrot
from simulation.sled_parts import ChainSledMount, XyJoiner, XySled
from simulation.y_axis import YAxis


#: The deck above the sled frame's origin: ``up(groove_height/2+rail_offset)``.
DECK = groove_height / 2 + rail_offset


class XSled(AssemblyNode):
    """The X sled on its frame's origin, carrying the Y axis.

    `travel` is the design's ``xslidepos``: how far the sled stands to
    the LEFT of the middle of its rail, along the sled's own -x -- the
    sign the joint's axis carries.
    """

    travel = Prismatic(axis=(-1, 0, 0), unit='mm')

    halves = XySled().repeat(2)
    joiners = XyJoiner().repeat(2)
    chain_mount = ChainSledMount()
    y_axis = YAxis()

    def render(self):
        for side, half in zip((1, -1), self.halves):
            place(half, up(DECK), right(side * platform_length / 2),
                  zrot(90), yrot(180))
        near, far = self.joiners
        place(near, up(DECK), left(platform_length + 0.3), zrot(-90))
        place(far, up(DECK), right(platform_length + 0.5), zrot(90))
        place(self.chain_mount, up(DECK), left(platform_length),
              fwd((platform_width - joiner_width) / 2), zrot(90))
        place(self.y_axis, up(DECK))
