"""The Y axis: a rail on the X sled, and the bed sled riding it.

The design's ``y_axis_assembly_7``: a motor rail segment with a plain
segment snapped to each end and an endcap on each of those, and the Y
sled sliding along the top.  It stands on the X sled's deck, so it
goes wherever X goes; what moves here is the bed.
"""

from solid_node.node import AssemblyNode

from simulation import pinion
from simulation.motor_segment import SWITCH_Y, MotorSegment
from simulation.params import (
    joiner_width,
    motor_length,
    motor_rail_length,
    motor_top_z,
    rail_height,
    rail_length,
    rail_width,
    groove_height,
)
from simulation.place import back, fwd, place, up, zrot
from simulation.rails import RailSegment, RailYEndcap
from simulation.motor_segment import SWITCH_X, SWITCH_Z
from simulation.wiring import Bundle
from simulation.y_sled import YSled


#: Where a plain segment's centre stands from the motor segment's.
SEGMENT = (motor_rail_length + rail_length) / 2

#: Where an endcap's origin stands.
ENDCAP = (motor_rail_length + 2 * rail_length) / 2

#: The sled frame: the rails' V, from ``y_axis_assembly_1``.
SLED = rail_height + groove_height / 2


class YAxis(AssemblyNode):
    """Rails, motor segment, endcaps and the bed sled.

    `sled.travel` is the design's ``yslidepos``: how far forward, along
    -y, the bed sled stands from the middle of its rail.
    """

    segment = MotorSegment()
    rails = RailSegment().repeat(2)
    endcaps = RailYEndcap().repeat(2)
    sled = YSled()

    # The same sentence as XAxis's: the segment here stands unturned,
    # so its own -y is the sled's forward, and the mesh reads identically.
    sled.travel.drives(segment.pinion.spin, ratio=pinion.DEGREES_PER_MM,
                       offset=pinion.PHASE)

    # The motor's four wires and the switch's two, out the front left
    # access hole; ``y_motor_segment_assembly_1`` and ``_2``.
    motor_wires = Bundle(2)(path=[
        [0, 0, 0],
        [-rail_width / 2 + joiner_width + 5, 0, 0],
        [-rail_width / 2 + joiner_width + 5, -motor_rail_length / 3.5 - 2, 5],
        [-rail_width / 1.5, -motor_rail_length / 3.5 - 2, 5],
        [-rail_width / 1.5 - 10, -motor_rail_length / 2 - 25, 0],
        [-rail_width / 1.5 - 30, -motor_rail_length / 2 - 25, 0],
    ], wires=4)
    switch_wire_a = Bundle(0)(path=[
        [-SWITCH_X, 10, SWITCH_Z + 8],
        [-SWITCH_X, 19, SWITCH_Z + 8],
        [-SWITCH_X - 2, 19, SWITCH_Z - 8],
        [-rail_width / 2 + joiner_width + 3, 20, 4],
        [-rail_width / 2 + joiner_width + 3, -motor_rail_length / 3.5 + 9, 9],
        [-rail_width / 1.5, -motor_rail_length / 3.5 + 9, 9],
        [-rail_width / 1.5 - 8, -motor_rail_length / 2 - 14, 4.5],
        [-rail_width / 1.5 - 30, -motor_rail_length / 2 - 14, 4.5],
    ], wires=1)
    switch_wire_b = Bundle(1)(path=[
        [-SWITCH_X, 10, SWITCH_Z - 8],
        [-SWITCH_X, 19, SWITCH_Z - 8],
        [-rail_width / 2 + joiner_width + 5, 20, 4],
        [-rail_width / 2 + joiner_width + 5, -motor_rail_length / 3.5 + 7, 9],
        [-rail_width / 1.5 + 2, -motor_rail_length / 3.5 + 7, 9],
        [-rail_width / 1.5 - 7, -motor_rail_length / 2 - 16, 4.5],
        [-rail_width / 1.5 - 30, -motor_rail_length / 2 - 16, 4.5],
    ], wires=1, wirenum=1)

    def render(self):
        far, near = self.rails
        place(far, back(SEGMENT), zrot(180))
        place(near, fwd(SEGMENT))
        far, near = self.endcaps
        place(far, back(ENDCAP), zrot(180))
        place(near, fwd(ENDCAP))
        place(self.sled, up(SLED))
        place(self.motor_wires, up(motor_top_z - (motor_length - 3)))
        place(self.switch_wire_a, fwd(SWITCH_Y))
        place(self.switch_wire_b, fwd(SWITCH_Y))
