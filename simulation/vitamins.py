"""The parts Snappy buys, as the design draws them in ``vitamins.scad``,
``NEMA.scad`` and ``GDMUtils.scad``.

Each is bought as one thing and is one leaf here, with the colour of
the most of it: a stepper's grey body rather than its silver shaft, a
hot end's dark barrel rather than its silver block.
"""

from solid2 import cube
from solid_node.parameters import Length

from simulation import colors
from simulation.params import (
    glass_length,
    glass_thick,
    glass_width,
    motor_length,
    motor_shaft_length,
    set_screw_size,
)
from simulation.part import ScadPart
from simulation.scad import gdm, nema, spool_holder, vitamins


class Nema17(ScadPart):
    """A NEMA 17 stepper: body down -Z from the origin, shaft up +Z."""

    color = colors.MOTOR

    def render(self):
        return nema.nema17_stepper(h=motor_length,
                                   shaft_len=motor_shaft_length)


class Microswitch(ScadPart):
    """The bare limit microswitch, lever up +Z."""

    color = colors.SWITCH

    def render(self):
        return vitamins.microswitch()


class JheadHotend(ScadPart):
    """The J-head hot end, barrel down -Z, with its own two wires."""

    color = colors.SWITCH

    def render(self):
        return vitamins.jhead_hotend()


class ExtruderDriveGear(ScadPart):
    """The hobbed drive gear on the extruder motor's shaft."""

    color = colors.SILVER

    def render(self):
        return vitamins.extruder_drive_gear()


class CoolingFan(ScadPart):
    """A 40 mm fan, hub on the XY plane, body up +Z."""

    color = colors.MOTOR

    def render(self):
        return vitamins.cooling_fan()


class SetScrewNut(ScadPart):
    """The M3 nut pressed into a drive gear or a lifter coupler."""

    color = colors.SILVER

    def render(self):
        return gdm.metric_nut(size=set_screw_size, hole=True)


class SetScrew(ScadPart):
    """The M3 grub screw threaded through that nut onto the shaft flat.

    The design draws the gears' screws silver and the couplers' dim
    grey, and a shade shorter; both are declared here.
    """

    length = Length(12.0, min=0)
    head = Length(6.0, min=0)

    color = colors.SILVER

    def render(self):
        return gdm.screw(screwsize=set_screw_size, screwlen=self.length,
                         headsize=self.head, headlen=set_screw_size)


class CouplerScrew(SetScrew):
    """The lifter coupler's set screw, as the design colours it."""

    color = colors.DIM_GRAY


class Glass(ScadPart):
    """The borosilicate build plate, centred on the origin.

    ``build_platform()`` in ``full_assembly.scad`` draws it lifted 12 mm
    off the sled; the lift is placement and lives with the sled.
    """

    color = colors.GLASS

    def render(self):
        return cube(size=[glass_width, glass_length, glass_thick],
                    center=True)


class Spool(ScadPart):
    """An empty filament spool, axis along Y, as the design draws it."""

    color = colors.SPOOL

    def render(self):
        return spool_holder.spool()
