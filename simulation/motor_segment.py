"""An XY motor rail segment with its stepper, pinion and limit switch.

This is the design's ``x_motor_segment_assembly_2`` and
``y_motor_segment_assembly_2``, which are the same thing wired
differently: the rail segment that cages a stepper, the stepper with a
drive gear on its shaft, and the microswitch clipped beside the rack's
path.  The wiring differs between the two and belongs to the axes.
"""

from solid_node.node import AssemblyNode
from solid_node.motion.ports import TranslationalPort

from simulation import colors, pinion
from simulation.params import (
    drive_gear_diam,
    endstop_depth,
    endstop_length,
    endstop_thick,
    gear_base,
    motor_shaft_size,
    motor_top_z,
    motor_width,
    printer_slop,
)
from simulation.part import ScadPart
from simulation.place import Z, fwd, left, place, right, up, xrot, yrot, zrot
from simulation.rails import MotorRailSegment
from simulation.scad import drive_gear
from simulation.vitamins import Microswitch, Nema17, SetScrew, SetScrewNut


#: Where the switch stands, from ``x_motor_segment_assembly_2``: the
#: design widens the motor by the printer's slop here.
SWITCH_X = motor_width + 2 * printer_slop
SWITCH_X = SWITCH_X / 2 + 7 + endstop_thick / 2
SWITCH_Y = drive_gear_diam / 2 + 1 - endstop_depth / 2
SWITCH_Z = motor_top_z + endstop_length / 2 - 5

#: Where the pinion sits on the shaft: ``xy_motor_assembly_3`` slides
#: it 3.1 mm up from the motor face.
GEAR_SEAT = 1 + 2.1


class DriveGear(ScadPart):
    """The herringbone pinion, printed, bore down on the origin."""

    color = colors.SALMON

    def render(self):
        return drive_gear.drive_gear()


class Pinion(AssemblyNode):
    """The drive gear with the nut and grub screw that lock it on.

    One assembly rather than three placements so the nut and the screw
    go round with the gear they are pressed into: the segment turns
    this node about its own axis, which is the gear's.
    """

    gear = DriveGear()
    nut = SetScrewNut()
    screw = SetScrew()

    def render(self):
        seat = (gear_base - 1) / 2
        place(self.nut, up(seat), right(motor_shaft_size / 2 + 1.5), yrot(90))
        place(self.screw, up(seat), right(motor_shaft_size / 2 + 11.5),
              yrot(90))


class MotorSegment(AssemblyNode):
    """The segment, its stepper, the pinion and the limit switch.

    `travel` is how far the sled riding this segment has gone forward
    along the segment's own -y -- the way both sleds go when their
    driver is positive -- and it is what the pinion is turned by.
    """

    travel = TranslationalPort(unit='mm')

    segment = MotorRailSegment()
    motor = Nema17()
    pinion = Pinion()
    switch = Microswitch()

    def render(self):
        place(self.motor, up(motor_top_z), zrot(-90))
        place(self.pinion, up(motor_top_z + GEAR_SEAT), zrot(-90))
        place(self.switch, fwd(SWITCH_Y), up(SWITCH_Z), left(SWITCH_X),
              xrot(90))

    def simulate(self):
        self.pinion.rotate(pinion.angle(self.travel.value), Z)
