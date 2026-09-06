"""The extruder: the J-head platform and everything clipped to it.

``extruder_assembly_11`` of the design, built up from the platform in
the order a builder does it: the hot end into its slot, the motor with
its drive gear clipped on, the idler arm with its bearing hinged in,
the compression screw, the fan shroud that latches all of it, a fan on
top of that and a cooling fan in its own shroud under the platform.
"""

from solid_node.node import AssemblyNode

from simulation import colors
from simulation.params import (
    cooling_duct_height,
    cooling_fan_size,
    cooling_fan_thick,
    extruder_drive_diam,
    extruder_fan_size,
    extruder_fan_thick,
    extruder_idler_diam,
    extruder_length,
    extruder_shaft_len,
    jhead_groove_thick,
    jhead_shelf_thick,
    motor_length,
    motor_width,
    printer_slop,
    rail_height,
    rail_width,
)
from simulation.part import ScadPart
from simulation.place import (
    back, down, fwd, left, place, right, translate, up, xrot, yrot, zrot)
from simulation.scad import (
    compression_screw,
    cooling_fan_shroud,
    extruder_fan_clip,
    extruder_fan_shroud,
    extruder_idler,
    extruder_motor_clip,
    jhead_platform,
)
from simulation.vitamins import (
    CoolingFan, ExtruderDriveGear, JheadHotend, Nema17)
from simulation.wiring import Bundle


#: The height of the motor's and idler's axis over the platform:
#: ``jhead_groove_thick+jhead_shelf_thick+motor_width/2`` throughout.
AXIS_Z = jhead_groove_thick + jhead_shelf_thick + motor_width / 2

#: How far the idler arm's top bar stands above the axis, from
#: ``extruder_idler_parts.scad``: the filament goes in through the
#: hole down the middle of that bar, so its top face is the inlet.
IDLER_TOPSIDE = motor_width * 0.25 + 5
INLET = AXIS_Z + IDLER_TOPSIDE

#: Where the fan shroud stands, and what it hangs its child from
#: (``extruder_fan_shroud()``: ``left(w/8) down(h+5+wall)``).
SHROUD_X = extruder_length / 4
SHROUD_WALL = 2
SHROUD_W = extruder_fan_size + 2 * SHROUD_WALL + 2 * 2
SHROUD_H = jhead_groove_thick + 20.0 - 2    # jhead_vent_span is 20
SHROUD_HOOK = (-SHROUD_W / 8, 0, -(SHROUD_H + 5 + SHROUD_WALL))

#: The cooling shroud's tilt and where it hangs its fan
#: (``cooling_fan_shroud()``).
COOLING_TILT = 10
COOLING_DUCT = cooling_duct_height - 8
COOLING_FAN_X = ((cooling_fan_size + 2 * SHROUD_WALL) / 2 - rail_height / 4
                 + extruder_fan_size)


class JheadPlatform(ScadPart):
    color = colors.STEEL_BLUE

    def render(self):
        return jhead_platform.jhead_platform()


class ExtruderMotorClip(ScadPart):
    color = colors.TURQUOISE

    def render(self):
        return extruder_motor_clip.extruder_motor_clip()


class ExtruderIdler(ScadPart):
    color = colors.TAN

    def render(self):
        return extruder_idler.extruder_idler()


class IdlerBearing(ScadPart):
    """The 686 bearing, bought, silver races round a dark shield."""

    color = colors.SILVER

    def render(self):
        return extruder_idler.idler_bearing()


class IdlerAxle(ScadPart):
    color = colors.TAN

    def render(self):
        return extruder_idler.extruder_idler_axle()


class IdlerAxleClip(ScadPart):
    color = colors.TAN

    def render(self):
        return extruder_idler.extruder_idler_axle_clip()


class CompressionScrew(ScadPart):
    """The printed screw that loads the idler, unpainted."""

    color = colors.UNPAINTED

    def render(self):
        return compression_screw.compression_screw()


class ExtruderFanShroud(ScadPart):
    color = colors.LIGHT_PINK

    def render(self):
        return extruder_fan_shroud.extruder_fan_shroud()


class ExtruderFanClip(ScadPart):
    color = colors.VIOLET

    def render(self):
        return extruder_fan_clip.extruder_fan_clip()


class CoolingFanShroud(ScadPart):
    color = colors.LIGHT_BLUE

    def render(self):
        return cooling_fan_shroud.cooling_fan_shroud()


class Extruder(AssemblyNode):
    """The whole extruder, platform on the origin, filament down Z."""

    platform = JheadPlatform()
    hotend = JheadHotend()
    motor = Nema17()
    drive_gear = ExtruderDriveGear()
    motor_clip = ExtruderMotorClip()
    idler = ExtruderIdler()
    bearing = IdlerBearing()
    axle = IdlerAxle()
    axle_clip = IdlerAxleClip()
    compression_screw = CompressionScrew()
    fan_shroud = ExtruderFanShroud()
    fan = CoolingFan()
    fan_clip = ExtruderFanClip()
    cooling_shroud = CoolingFanShroud()
    cooling_fan = CoolingFan()

    # ``extruder_assembly_3`` also runs the motor's four wires down the
    # back of the platform; that path is one the design's ``wiring()``
    # cannot sweep under OpenSCAD 2021.01 (see `wiring`), so it is not
    # here.
    # ``extruder_assembly_9`` and ``_10``: each fan's two wires along
    # the back of the platform.
    fan_wires = Bundle(4)(path=[
        [0, extruder_fan_size / 2, 0],
        [0, extruder_fan_size / 2 + 10, 0],
        [-10, rail_width / 3 + 5, 0],
        [-30, rail_width / 3 + 5, 0],
        [-76, rail_width / 3 - 5, 0],
        [-76, 0, 0],
        [-95, 0, 0],
    ], wires=2, fillet=5, wirenum=4)
    cooling_wires = Bundle(6)(path=[
        [0, extruder_fan_size / 2, 0],
        [0, extruder_fan_size / 2 + 10, 0],
        [-40, 27.01, 25],
        [-40, 27.01, 45],
        [-45, rail_width / 3 + 5, 51],
        [-65, rail_width / 3 + 5, 51],
        [-(extruder_length / 2 + 47), rail_width / 3 - 5, 60],
        [-(extruder_length / 2 + 47), 0, 60],
        [-(extruder_length / 2 + 62), 0, 60],
    ], wires=2, fillet=5, wirenum=6)

    def render(self):
        # ``extruder_assembly_5``: the motor group, drive gear on the
        # shaft, clipped to the platform's face plate.
        motor_seat = (up(AXIS_Z), fwd(extruder_drive_diam / 2 - 0.5),
                      left(extruder_shaft_len / 2 - 0.05))
        motor_frame = (xrot(180), yrot(90), zrot(-90))
        place(self.motor, *motor_seat, *motor_frame)
        place(self.drive_gear, *motor_seat, *motor_frame, up(4))
        place(self.motor_clip, *motor_seat, left(motor_length / 2), zrot(-90))

        # ``extruder_assembly_1``, ``_2`` and ``_6``: the idler arm.
        place(self.idler, up(AXIS_Z))
        place(self.bearing, up(AXIS_Z), back(extruder_idler_diam / 2))
        place(self.axle, up(AXIS_Z), left(printer_slop),
              back(extruder_idler_diam / 2),
              left(extruder_shaft_len / 4 + 1), xrot(90), yrot(90))
        place(self.axle_clip, up(AXIS_Z), left(printer_slop),
              back(extruder_idler_diam / 2),
              right(extruder_shaft_len / 4 + 0.5), xrot(90), yrot(90))

        # ``extruder_assembly_7``: the compression screw.
        place(self.compression_screw, up(AXIS_Z), back(30 + 20.1), xrot(90))

        # ``extruder_assembly_8`` and ``_9``: the fan shroud, the fan on
        # it and the clip that holds the fan.
        place(self.fan_shroud, right(SHROUD_X), up(jhead_groove_thick + 0.05))
        fan_seat = (right(SHROUD_X),
                    up(jhead_groove_thick + jhead_shelf_thick + 0.05))
        place(self.fan, *fan_seat)
        place(self.fan_wires, *fan_seat,
              translate([-(extruder_fan_size / 2 - 5), 0,
                         extruder_fan_thick / 4]))
        place(self.fan_clip, *fan_seat,
              up(12 - extruder_fan_thick + 2 + 0.05), zrot(90))

        # ``extruder_assembly_10`` and ``_11``: the cooling shroud hung
        # from the fan shroud's hook, with its fan in it.
        cooling_seat = (right(SHROUD_X), up(jhead_groove_thick + 0.05),
                        translate(SHROUD_HOOK))
        place(self.cooling_shroud, *cooling_seat)
        cooling_fan_seat = (*cooling_seat, yrot(-COOLING_TILT),
                            down(6 + COOLING_DUCT / 2), right(COOLING_FAN_X),
                            up(cooling_fan_thick / 2 - SHROUD_WALL))
        place(self.cooling_fan, *cooling_fan_seat)
        place(self.cooling_wires, *cooling_fan_seat,
              translate([-(extruder_fan_size / 2 - 5), 0,
                         extruder_fan_thick / 4]))
