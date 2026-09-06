"""The printed parts the two sleds are snapped together from."""

from simulation import colors
from simulation.part import ScadPart
from simulation.scad import (
    adjustment_screw,
    cable_chain_mount,
    glass_bed_support,
    sled_endcap,
    xy_joiner,
    xy_sled,
)


class XySled(ScadPart):
    """Half a sled: sliders on top, herringbone rack underneath."""

    color = colors.MEDIUM_SLATE_BLUE

    def render(self):
        return xy_sled.xy_sled()


class XyJoiner(ScadPart):
    """The X sled's end, which the Y axis rails snap onto."""

    color = colors.SIENNA

    def render(self):
        return xy_joiner.xy_joiner()


class SledEndcap(ScadPart):
    """The Y sled's end, which the bed supports snap onto."""

    color = colors.DODGER_BLUE

    def render(self):
        return sled_endcap.sled_endcap()


class ChainSledMount(ScadPart):
    """The X sled's cable chain anchor."""

    color = colors.WHITE

    def render(self):
        return cable_chain_mount.cable_chain_x_sled_mount()


class GlassBedSupport1(ScadPart):
    color = colors.CHOCOLATE

    def render(self):
        return glass_bed_support.glass_bed_support1()


class GlassBedSupport2(ScadPart):
    color = colors.CHOCOLATE

    def render(self):
        return glass_bed_support.glass_bed_support2()


class AdjustmentScrew(ScadPart):
    """A printed acme adjustment screw, knob down on the origin.

    The design paints it nothing, so it renders in OpenSCAD's default
    face colour, which is the colour it carries here.
    """

    color = colors.UNPAINTED

    def render(self):
        return adjustment_screw.adjustment_screw()
