"""The design's dimensions, read from ``config.scad`` itself.

Every number Snappy is built from is declared or derived at the top of
``config.scad`` -- ``rail_offset`` from the shaft clearance and the rack,
``platform_z`` from the rail and the groove, ``z_base_height`` from the
platform height and the glass, and so on.  Restating that arithmetic
here would give this layer a second set of dimensions free to drift from
the first, so instead OpenSCAD is asked once, at import, what every
top-level name of that file evaluates to.  Echo export evaluates the
variable tree without rendering any geometry.

The names are not listed here either: they are read off ``config.scad``
by a regular expression over its assignments, so a value added to the
design is a value this module has, under the same name.  ``from
simulation.params import rail_height`` is therefore the same
``rail_height`` the .scad modules draw with.

A handful of values the design writes inside a module body, where the
probe cannot reach, are restated at the foot of this file with the
module they belong to.
"""

import ast
import os
import re
import subprocess
import tempfile

from simulation.scad import SOURCE_DIR


CONFIG = os.path.join(SOURCE_DIR, 'config.scad')

_ASSIGNMENT = re.compile(r'^\s*([A-Za-z_]\w*)\s*=', re.MULTILINE)
_ECHO = re.compile(r'^ECHO: "PARAM (\S+) = (.*)"$')
_PRECISE = re.compile(r'^ECHO: "PRECISE (\S+) = (\S+) (\S+)"$')


def names(source=CONFIG):
    """Every name assigned at the top level of `source`, in file order."""
    with open(source) as handle:
        text = handle.read()
    seen = []
    for name in _ASSIGNMENT.findall(text):
        if name not in seen:
            seen.append(name)
    return seen


def _value(text):
    """An OpenSCAD echo value as a Python one."""
    literal = re.sub(r'\btrue\b', 'True', text)
    literal = re.sub(r'\bfalse\b', 'False', literal)
    literal = re.sub(r'\bundef\b', 'None', literal)
    try:
        return ast.literal_eval(literal)
    except (SyntaxError, ValueError):
        return text


def probe(source, wanted):
    """Evaluate `wanted` in the scope of `source` and return them.

    Each scalar is echoed twice.  OpenSCAD prints a number with six
    significant digits, which for a machine 600 mm wide loses the
    fourth decimal place; so a scalar is echoed a second time split
    into its integer part and its fraction scaled by a million, and the
    two halves are recombined here.
    """
    script = ['include <%s>;' % source]
    for name in wanted:
        script.append('echo(str("PARAM %s = ", %s));' % (name, name))
        script.append(
            'if (is_num(%s)) echo(str("PRECISE %s = ", floor(%s), " ",'
            ' (%s - floor(%s))*1000000));' % ((name,) * 5))

    with tempfile.TemporaryDirectory() as workdir:
        path = os.path.join(workdir, 'probe.scad')
        echoes = os.path.join(workdir, 'probe.echo')
        with open(path, 'w') as handle:
            handle.write('\n'.join(script) + '\n')
        subprocess.run(['openscad', '-o', echoes, path],
                       check=True, capture_output=True)
        with open(echoes) as handle:
            output = handle.read()

    values = {}
    for line in output.splitlines():
        matched = _ECHO.match(line.strip())
        if matched:
            values[matched.group(1)] = _value(matched.group(2))
            continue
        matched = _PRECISE.match(line.strip())
        if matched:
            whole, fraction = matched.group(2), matched.group(3)
            values[matched.group(1)] = (
                float(whole) + float(fraction) / 1000000)

    missing = [name for name in wanted if name not in values]
    if missing:
        raise RuntimeError(
            '%s does not define %s' % (source, ', '.join(missing)))
    return values


_config = probe(CONFIG, names())
globals().update(_config)

# NEMA 17 facts the design keeps in NEMA.scad's lookup tables.
motor_width = 42.3          # nema_motor_width(17) in NEMA.scad
motor_plinth_height = 2.0   # nema_motor_plinth_height(17)
motor_plinth_diam = 22.0    # nema_motor_plinth_diam(17)

# Values the design writes inside a module body rather than at the top
# level, so the probe cannot reach them.  Each is named with the module
# it belongs to, so a reader can check it against the source.
cable_chain_pitch = ((cable_chain_length / 2 - cable_chain_height / 3)
                     + (cable_chain_length / 2 - cable_chain_pivot / 2
                        - 2.75 + 0.1))
                            # cable_chain_assembly() in
                            # cable_chain_link_parts.scad: l1 + l2, the
                            # pin-to-pin pitch of one link
xy_joiner_length = 20       # joiner_length in xy_joiner_parts.scad
sled_endcap_length = 20     # joiner_length in sled_endcap_parts.scad
spool_width = 80 + joiner_width   # spool_w in spool_holder_parts.scad
spool_hub_diam = 96         # spool() in spool_holder_parts.scad
spool_hub_length = 72       # spool(): the hub between the flanges
spool_flange_diam = 205     # spool(): the two flanges
spool_flange_thick = 5      # spool()
spool_axle_diam = 15        # spool_axle()
spool_axle_drop = 52.5 / 2 - 14   # final_assembly_9(): the spool hangs
                                  # this far below the axle's origin
jhead_length = 40           # jhead_hotend() in vitamins.scad
jhead_block_size = [18.7, 16, 9.6]   # jhead_hotend()
glass_height_over_sled = 10 + 2   # build_platform() in full_assembly.scad
