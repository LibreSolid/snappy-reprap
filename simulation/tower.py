"""A Z tower: base, legs, rails, lifter and limit switch.

``z_tower_assembly_6`` of the design, and ``_7`` for the left tower,
which also carries the anchor of the chain that climbs it.  The right
tower is the same assembly turned round.  A tower is drawn in its own
frame with the YZ joiner's origin at ``left(platform_length)``, which
is how the design draws it, so the rails stand at ``x = -44`` and the
lifter under them.
"""

from solid_node.node import AssemblyNode
from solid_node.motion.ports import RotationalPort
from solid_node.parameters import Flag

from simulation import colors
from simulation.chain_parts import ChainJoinerMount
from simulation.lifter import Lifter
from simulation.params import (
    endstop_depth,
    groove_height,
    joiner_width,
    platform_length,
    rail_height,
    rail_length,
    rail_width,
    z_base_height,
    z_joiner_spacing,
)
from simulation.part import ScadPart
from simulation.place import back, fwd, left, place, right, up, yrot, zrot
from simulation.rails import ZBase, ZRail
from simulation.scad import support_leg, yz_joiner
from simulation.vitamins import Microswitch
from simulation.wiring import Bundle


#: Where the tower's parts stand, from ``z_tower_assembly_1`` to ``_7``.
BASE_TOP = rail_height + groove_height + z_base_height
RAILS_CENTRE = BASE_TOP + rail_length
RAIL_X = rail_height + groove_height / 2
LIFTER_Z = rail_height + groove_height + z_base_height / 2 + z_base_height / 2 - 16.5
SWITCH_Z = BASE_TOP - endstop_depth / 2
SWITCH_Y = z_joiner_spacing / 2 + joiner_width + 7.5
SWITCH_X = platform_length - rail_height - groove_height / 2
LEG_Y = rail_width / 2 + 14
CHAIN_MOUNT_Y = z_joiner_spacing / 2 + 7
CHAIN_MOUNT_Z = RAILS_CENTRE - 11


class YzJoiner(ScadPart):
    color = colors.JOINER

    def render(self):
        return yz_joiner.yz_joiner()


class SupportLeg(ScadPart):
    color = colors.SANDY_BROWN

    def render(self):
        return support_leg.support_leg()


class ZTower(AssemblyNode):
    """One tower.  `screw` is how far its lifter has been turned.

    `chain_mount` is whether this is the tower the bridge's cable chain
    climbs: the design snaps the anchor onto the left tower only.
    """

    chain_mount = Flag(False)

    screw = RotationalPort(unit='deg')

    joiner = YzJoiner()
    legs = SupportLeg().repeat(2)
    base = ZBase()
    rails = ZRail().repeat(2)
    lifter = Lifter()
    switch = Microswitch()
    chain_anchor = ChainJoinerMount()

    # ``z_tower_assembly_4``: the switch's two wires down the tower and
    # out the back of the base.
    switch_wire_a = Bundle(4)(path=[
        [8, 0, -10],
        [7, 0, -20],
        [5 - rail_height, 1, -z_base_height / 2],
        [5 - rail_height, -9, -z_base_height / 2 - 10],
        [5 - rail_height, -z_joiner_spacing / 2 - joiner_width / 2 - 6.5,
         -z_base_height - rail_height + 8],
        [-rail_height - 20, -z_joiner_spacing / 2 - joiner_width / 2 - 6.5,
         -z_base_height - rail_height + 8],
    ], wires=1, fillet=5, wirenum=4)
    switch_wire_b = Bundle(5)(path=[
        [-8, 0, -10],
        [-9, 0, -20],
        [5 - rail_height, -1, -z_base_height / 2],
        [5 - rail_height, -10, -z_base_height / 2 - 10],
        [5 - rail_height, -z_joiner_spacing / 2 - joiner_width / 2 - 8.5,
         -z_base_height - rail_height + 8],
        [-rail_height - 20, -z_joiner_spacing / 2 - joiner_width / 2 - 8.5,
         -z_base_height - rail_height + 8],
    ], wires=1, fillet=5, wirenum=5)

    def render(self):
        if not self.chain_mount:
            self.chain_anchor.omit()

        place(self.joiner, left(platform_length), zrot(-90))
        near, far = self.legs
        place(near, left(platform_length), right(platform_length / 3),
              back(LEG_Y))
        place(far, left(platform_length), right(platform_length / 3),
              zrot(180), back(LEG_Y))
        place(self.base, left(platform_length),
              up(rail_height + groove_height + z_base_height / 2),
              yrot(90), zrot(90))
        place(self.lifter, left(platform_length), right(RAIL_X), up(LIFTER_Z))
        lower, upper = self.rails
        place(lower, up(RAILS_CENTRE), left(platform_length),
              up(-rail_length / 2), yrot(90), zrot(90))
        place(upper, up(RAILS_CENTRE), left(platform_length),
              up(rail_length / 2), yrot(90), zrot(90))
        place(self.switch, up(SWITCH_Z), back(SWITCH_Y), left(SWITCH_X),
              zrot(90))
        for wire in (self.switch_wire_a, self.switch_wire_b):
            place(wire, up(SWITCH_Z), back(SWITCH_Y), left(SWITCH_X))
        place(self.chain_anchor, left(platform_length), fwd(CHAIN_MOUNT_Y),
              up(CHAIN_MOUNT_Z), yrot(90), zrot(90))

    def simulate(self):
        self.connect(self.screw, self.lifter.angle)
