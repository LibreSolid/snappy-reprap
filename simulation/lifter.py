"""A Z lifter: the stepper and the printed screw it turns.

``lifter_assembly_5`` of the design: a coupler pressed onto the motor
shaft and locked with a grub screw, two lifter rods stacked on it, and
the whole stack turned by the sled's height.  Here the stack is turned
by the angle the machine hands down.
"""

from solid_node.node import AssemblyNode
from solid_node.motion.ports import RotationalPort

from simulation import colors
from simulation.params import (
    lifter_coupler_len,
    lifter_rod_length,
    lifter_rod_pitch,
    motor_shaft_size,
    printer_slop,
)
from simulation.part import ScadPart
from simulation.place import Z, place, right, up, yrot, zrot
from simulation.scad import lifter_coupler, lifter_rod
from simulation.vitamins import CouplerScrew, Nema17, SetScrewNut


#: How tall one rod is: ``lifter_rod()`` rounds the length up to whole
#: pitches and takes the printer's slop off.
ROD_HEIGHT = (-(-lifter_rod_length // lifter_rod_pitch) * lifter_rod_pitch
              - printer_slop)

#: Where the coupler's nut and screw sit, from ``lifter_coupler()``.
NUT_SEAT = 5
NUT_X = motor_shaft_size / 2 + 1.5
SCREW_X = NUT_X + 6 + 1.9

#: How far up the motor the coupler is pressed, from ``lifter_assembly_5``.
COUPLER_SEAT = 5


class LifterRod(ScadPart):
    """One printed acme lifter rod, tang up, socket down, unpainted."""

    color = colors.UNPAINTED

    def render(self):
        return lifter_rod.lifter_rod()


class LifterCoupler(ScadPart):
    """The printed coupler between shaft and rod, unpainted."""

    color = colors.UNPAINTED

    def render(self):
        return lifter_coupler.lifter_coupler()


class LifterScrew(AssemblyNode):
    """The coupler, its nut and grub screw, and the two rods on it.

    One assembly so it turns as one thing about the coupler's axis,
    which is the origin: the stepper turns the coupler, the coupler
    turns the rods.
    """

    coupler = LifterCoupler()
    rods = LifterRod().repeat(2)
    nut = SetScrewNut()
    screw = CouplerScrew(length=10.0, head=5.5)

    def render(self):
        lower, upper = self.rods
        place(lower, up(lifter_coupler_len), zrot(90))
        place(upper, up(lifter_coupler_len), zrot(90), up(ROD_HEIGHT))
        place(self.nut, up(NUT_SEAT), right(NUT_X), yrot(90))
        place(self.screw, up(NUT_SEAT), right(SCREW_X), yrot(90))


class Lifter(AssemblyNode):
    """The stepper with the screw on its shaft.

    `angle` is how far the screw has been turned about Z, and it comes
    from outside: a lifter has no opinion about it.  The screw turns
    and the stepper's case does not.
    """

    angle = RotationalPort(unit='deg')

    motor = Nema17()
    screw = LifterScrew()

    def render(self):
        place(self.motor, zrot(90))
        place(self.screw, up(COUPLER_SEAT))

    def simulate(self):
        self.screw.rotate(self.angle.value, Z)
