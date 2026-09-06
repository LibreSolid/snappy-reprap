"""Access to the original OpenSCAD design.

Snappy is authored in OpenSCAD, in the .scad files beside this package,
and that design is left exactly as it is.  This package is a second
reading of it: every leaf's geometry is one module of the design,
reached through solid2's ``import_scad``, which emits ``use <absolute
path>`` so the ``include``/``use`` chains inside the design keep
resolving from the source directory.

Two services live here: one handle per source file the layer draws
from, and :func:`scad_sources`, the set of .scad files the whole design
is built from, which every leaf adds to its own source set -- the
framework's import walk sees Python only, so without it a part would
report itself up to date after an edit to the module that draws it.
"""

import os

from solid2 import import_scad
from solid2.core.object_base import OpenSCADObject


SOURCE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def _handle(filename):
    return import_scad(os.path.join(SOURCE_DIR, filename))


# The bought parts, the fasteners and the wiring the design draws.
vitamins = _handle('vitamins.scad')
nema = _handle('NEMA.scad')
gdm = _handle('GDMUtils.scad')
wiring = _handle('wiring.scad')

# The printed parts, one file each, as the design keeps them.
adjustment_screw = _handle('adjustment_screw_parts.scad')
bridge_brace = _handle('bridge_brace_parts.scad')
bridge_brace_center = _handle('bridge_brace_center_parts.scad')
bridge_segment = _handle('bridge_segment_parts.scad')
cable_chain_link = _handle('cable_chain_link_parts.scad')
cable_chain_mount = _handle('cable_chain_mount_parts.scad')
compression_screw = _handle('compression_screw_parts.scad')
cooling_fan_shroud = _handle('cooling_fan_shroud_parts.scad')
drive_gear = _handle('drive_gear_parts.scad')
extruder_fan_clip = _handle('extruder_fan_clip_parts.scad')
extruder_fan_shroud = _handle('extruder_fan_shroud_parts.scad')
extruder_idler = _handle('extruder_idler_parts.scad')
extruder_motor_clip = _handle('extruder_motor_clip_parts.scad')
glass_bed_support = _handle('glass_bed_support_parts.scad')
jhead_platform = _handle('jhead_platform_parts.scad')
lifter_coupler = _handle('lifter_coupler_parts.scad')
lifter_rod = _handle('lifter_rod_parts.scad')
rail_segment = _handle('rail_segment_parts.scad')
rail_xy_motor_segment = _handle('rail_xy_motor_segment_parts.scad')
rail_y_endcap = _handle('rail_y_endcap_parts.scad')
rail_z_endcap = _handle('rail_z_endcap_parts.scad')
ramps_mount = _handle('ramps_mount_parts.scad')
sled_endcap = _handle('sled_endcap_parts.scad')
spool_holder = _handle('spool_holder_parts.scad')
support_leg = _handle('support_leg_parts.scad')
xy_joiner = _handle('xy_joiner_parts.scad')
xy_sled = _handle('xy_sled_parts.scad')
yz_joiner = _handle('yz_joiner_parts.scad')
z_base = _handle('z_base_parts.scad')
z_rail = _handle('z_rail_parts.scad')
z_sled = _handle('z_sled_parts.scad')


def call(module_name, **kwargs):
    """Call a module of the design by name, with keyword arguments only.

    For modules that take special variables such as ``$fa``, which a
    handle's attribute call cannot spell: the ``use`` header for their
    file is emitted by the imports above all the same.
    """
    return OpenSCADObject(module_name, kwargs)


def scad_sources():
    """Every OpenSCAD source the design is built from.

    The whole directory rather than a per-node closure: OpenSCAD's own
    ``include``/``use`` graph is not visible to the framework's Python
    import walk, and an unnecessary rebuild costs less than stale
    geometry served after an edit.
    """
    return {
        os.path.join(SOURCE_DIR, entry)
        for entry in os.listdir(SOURCE_DIR)
        if entry.endswith('.scad')
    }
