"""The Y sled: two sled halves, two ends, four bed clips and the glass.

The design's ``y_axis_assembly_2`` is one end of it -- an endcap with a
glass bed support snapped to each side and an adjustment screw down
through each support -- and ``y_axis_assembly_4`` and ``_6`` stand two
of those on the two halves, one turned round.  The glass drops into
the four clips last.
"""

from solid_node.node import AssemblyNode
from solid_node.motion.joints import Prismatic

from simulation.params import (
    adjust_screw_diam,
    glass_height_over_sled,
    glass_thick,
    glass_width,
    groove_height,
    joiner_width,
    platform_length,
    platform_width,
    rail_offset,
)
from simulation.place import back, fwd, left, place, right, up, xrot, yrot, zrot
from simulation.sled_parts import (
    AdjustmentScrew,
    GlassBedSupport1,
    GlassBedSupport2,
    SledEndcap,
    XySled,
)
from simulation.vitamins import Glass


#: How far the sled deck stands above the sled frame's origin, which is
#: the rails' V: ``up(groove_height/2+rail_offset)`` throughout.
DECK = groove_height / 2 + rail_offset

#: How far from the sled's centre each half and each end sits: the
#: design leaves half a millimetre between the two halves.
HALF = (platform_length + 0.5) / 2
END = platform_length + 0.5

#: Where each screw's knob stands, from ``y_axis_assembly_2``.
SCREW_X = platform_width / 2 + (glass_width / 2 - platform_width / 2
                                - adjust_screw_diam / 2 - 1)
SCREW_Z = 10 + 7
SUPPORT_Y = 20 - joiner_width / 2


class BedCorner(AssemblyNode):
    """One end of the Y sled: endcap, two clips, two screws."""

    endcap = SledEndcap()
    support_right = GlassBedSupport2()
    support_left = GlassBedSupport1()
    screws = AdjustmentScrew().repeat(2)

    def render(self):
        place(self.support_right, fwd(SUPPORT_Y), right(platform_width / 2),
              zrot(90))
        place(self.support_left, fwd(SUPPORT_Y), left(platform_width / 2),
              zrot(-90))
        for side, screw in zip((1, -1), self.screws):
            place(screw, fwd(SUPPORT_Y), right(side * SCREW_X), up(SCREW_Z),
                  xrot(180))


class YSled(AssemblyNode):
    """The whole Y sled, on the sled frame's origin, deck up.

    `travel` is the design's ``yslidepos``: how far forward the sled
    stands from the middle of its rail, along the sled's own -y -- the
    sign the joint's axis carries.
    """

    travel = Prismatic(axis=(0, -1, 0), unit='mm')

    halves = XySled().repeat(2)
    corners = BedCorner().repeat(2)
    glass = Glass()

    def render(self):
        for side, half in zip((1, -1), self.halves):
            place(half, up(DECK), back(side * HALF), zrot(180), yrot(180))
        near, far = self.corners
        place(near, fwd(END), up(DECK))
        place(far, back(END), up(DECK), zrot(180))
        place(self.glass, up(DECK + glass_height_over_sled + glass_thick / 2))
