"""The snap-together rails and frames the axes are built from.

All of them are the design's own modules at their own origins; which
way each stands is the axis assembly's business.
"""

from simulation import colors
from simulation.part import ScadPart
from simulation.scad import (
    bridge_segment,
    rail_segment,
    rail_xy_motor_segment,
    rail_y_endcap,
    rail_z_endcap,
    z_base,
    z_rail,
)


class RailSegment(ScadPart):
    """A plain XY rail segment, rails along Y."""

    color = colors.RAIL

    def render(self):
        return rail_segment.rail_segment()


class MotorRailSegment(ScadPart):
    """The XY rail segment that cages a stepper, rails along Y."""

    color = colors.SPRING_GREEN

    def render(self):
        return rail_xy_motor_segment.rail_xy_motor_segment()


class RailYEndcap(ScadPart):
    color = colors.YELLOW_GREEN

    def render(self):
        return rail_y_endcap.rail_y_endcap()


class RailZEndcap(ScadPart):
    color = colors.YELLOW_GREEN

    def render(self):
        return rail_z_endcap.rail_z_endcap()


class ZRail(ScadPart):
    """One tower rail segment, drawn lying down with rails along Y."""

    color = colors.RAIL

    def render(self):
        return z_rail.z_rail()


class ZBase(ScadPart):
    """The tower base that cages the lifter motor, drawn lying down."""

    color = colors.RAIL

    def render(self):
        return z_base.z_base()


class BridgeSegment(ScadPart):
    """One arched span of the bridge, rails along Y."""

    color = colors.RAIL

    def render(self):
        return bridge_segment.bridge_segment()
