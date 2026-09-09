"""The X axis: the base rail of the machine and the sled riding it.

``x_axis_assembly_9`` of the design: the motor rail segment turned to
run along X, a plain segment on each end, the X sled sliding along the
top with the whole Y axis on it, and the wiring and cable chain that
follow the sled.  The two Z towers snap onto the ends of this rail and
belong to the machine, not to the axis.
"""

from solid_node.node import AssemblyNode

from simulation import pinion
from simulation.cable_chain import CableChain
from simulation.chain_parts import ChainJoinerMount
from simulation.homing import X_HOME, X_MAX
from simulation.motor_segment import SWITCH_X, SWITCH_Y, SWITCH_Z, MotorSegment
from simulation.params import (
    cable_chain_height,
    cable_chain_length,
    cable_chain_width,
    groove_height,
    joiner_width,
    motor_length,
    motor_rail_length,
    motor_top_z,
    platform_length,
    platform_width,
    rail_height,
    rail_length,
    rail_offset,
    rail_thick,
    rail_width,
    side_mount_spacing,
)
from simulation.place import fwd, left, place, right, translate, up, zrot
from simulation.rails import RailSegment
from simulation.wiring import Bundle
from simulation.x_sled import XSled


#: Where a plain segment's centre stands from the motor segment's.
SEGMENT = (motor_rail_length + rail_length) / 2

#: The sled frame: the rails' V, from ``x_axis_assembly_1``.
SLED = rail_height + groove_height / 2

#: The cable chain, from ``x_axis_assembly_9``: its plane stands this
#: far in front of the rail, its fixed end on the joiner mount at the
#: rail's foot and its moving end on the sled's mount at deck height.
CHAIN_Y = platform_width / 2 + cable_chain_width / 2 + 2
CHAIN_TOP = [-platform_length - 1, 0,
             rail_height + groove_height + rail_offset + cable_chain_height / 2]
CHAIN_BOTTOM = [-side_mount_spacing / 2 - cable_chain_length / 2
                + cable_chain_height / 3, 0, cable_chain_height / 2]
CHAIN_WIRES = 6


class XAxis(AssemblyNode):
    """The base rail, its sled, and everything the sled carries.

    `sled.travel` is the design's ``xslidepos``: how far the sled
    stands to the left, along -x, of the middle of its rail.
    """

    segment = MotorSegment()
    rails = RailSegment().repeat(2)
    sled = XSled()
    chain_anchor = ChainJoinerMount()
    chain = CableChain(top=CHAIN_TOP, bottom=CHAIN_BOTTOM,
                       least=X_HOME, most=X_MAX, wires=CHAIN_WIRES)

    # The rack under the sled turns the pinion; see `pinion` for the
    # sign and the measured phase.  The segment stands turned a quarter
    # turn clockwise, so its own -y is the machine's -x: a sled going
    # left goes forward along the segment, which is the travel `SIGN`
    # was measured for, and z is common to both frames.
    sled.travel.drives(segment.pinion.spin, ratio=pinion.DEGREES_PER_MM,
                       offset=pinion.PHASE)
    # The chain's split between its two runs is the sled's own position.
    sled.travel.drives(chain.offset)

    # ``x_motor_segment_assembly_1`` and ``_2``: the motor's four wires
    # and the switch's two, in the segment's own frame.
    motor_wires = Bundle(2)(path=[
        [0, 0, 0],
        [-rail_width / 2 + joiner_width + 20, 0, 0],
        [-rail_width / 2 + joiner_width + 20, -motor_rail_length / 3.5 - 4, 5],
        [0, -motor_rail_length / 3.5 - 4, 5],
        [0, -motor_rail_length / 2 - 20, 5],
    ], wires=4)
    switch_wire_a = Bundle(0)(path=[
        [-SWITCH_X, 10, SWITCH_Z - 8],
        [-SWITCH_X - 1, 18, SWITCH_Z - 8],
        [-SWITCH_X - 1, 19, 10],
        [-SWITCH_X - 1, -motor_rail_length / 3.5 - 5 + SWITCH_Y, 10],
        [1, -motor_rail_length / 3.5 - 5 + SWITCH_Y, 10],
        [1, -motor_rail_length / 2 - 20 + SWITCH_Y, 10],
    ], wires=1)
    switch_wire_b = Bundle(1)(path=[
        [-SWITCH_X, 10, SWITCH_Z + 8],
        [-SWITCH_X - 3, 18, SWITCH_Z + 8],
        [-SWITCH_X - 3, 19, 10],
        [-SWITCH_X - 3, -motor_rail_length / 3.5 - 5 + SWITCH_Y - 2, 10],
        [-1, -motor_rail_length / 3.5 - 5 + SWITCH_Y - 2, 10],
        [-1, -motor_rail_length / 2 - 20 + SWITCH_Y, 10],
    ], wires=1, wirenum=1)
    # ``x_axis_assembly_1``: the harness out the left end of the rail.
    rail_wires = Bundle(0)(path=[
        [-motor_rail_length / 2, 0, 0],
        [-rail_length, 0, 0],
        [-(rail_length + motor_rail_length / 2) - 30, 0, 0],
    ], wires=6)
    # ``x_axis_assembly_9``: from the chain's fixed end in through the
    # access hole beside it and out the left end of the rail.
    chain_wires = Bundle(0)(path=[
        [CHAIN_BOTTOM[0], -CHAIN_Y, cable_chain_height / 2],
        [-motor_rail_length / 3 + 10, -CHAIN_Y, cable_chain_height / 2],
        [-motor_rail_length / 3 + 5, -(rail_width / 2 + joiner_width / 2),
         rail_thick + 5],
        [-motor_rail_length / 3 + 5, -rail_width / 3, rail_thick + 5],
        [-rail_length - motor_rail_length / 2 - 30, -rail_width / 3,
         rail_thick + 5],
    ], wires=6)

    def render(self):
        place(self.segment, zrot(-90))
        near, far = self.rails
        place(near, right(SEGMENT), zrot(90))
        place(far, left(SEGMENT), zrot(270))
        place(self.sled, up(SLED))
        place(self.chain_anchor, fwd(rail_width / 2 + 2),
              left(side_mount_spacing / 2), zrot(90))
        place(self.chain, fwd(CHAIN_Y))
        place(self.motor_wires, zrot(-90),
              up(motor_top_z - (motor_length - 3)))
        place(self.switch_wire_a, zrot(-90), fwd(SWITCH_Y))
        place(self.switch_wire_b, zrot(-90), fwd(SWITCH_Y))
        place(self.rail_wires, up(12))
