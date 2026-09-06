"""OpenSCAD's transform chains, read the way the design writes them.

The design places every part with GDMUtils' little words -- ``up(5)
zrot(-90) xrot(90) part()`` -- and reads them the way OpenSCAD applies
them: the innermost first.  solid-node applies a node's operations in
the order they are appended.  So this module offers the same words,
each returning one operation, and :func:`place`, which appends them to
a node in reverse -- so a placement here is transcribed from the design
left to right, exactly as it stands in ``full_assembly.scad``, and a
reader can check the two against each other line by line.

Every argument may be a number or a symbolic expression over the
drivers, so the same words serve `render()` and `simulate()`.
"""

X, Y, Z = [1, 0, 0], [0, 1, 0], [0, 0, 1]


def up(z):
    return ('t', [0, 0, z])


def down(z):
    return ('t', [0, 0, -z])


def right(x):
    return ('t', [x, 0, 0])


def left(x):
    return ('t', [-x, 0, 0])


def back(y):
    return ('t', [0, y, 0])


def fwd(y):
    return ('t', [0, -y, 0])


def translate(vector):
    return ('t', list(vector))


def xrot(angle):
    return ('r', angle, X)


def yrot(angle):
    return ('r', angle, Y)


def zrot(angle):
    return ('r', angle, Z)


def place(node, *operations):
    """Apply `operations` to `node` as OpenSCAD would apply that chain.

    Written in the design's order -- the outermost transform first --
    and applied innermost first, which is what the geometry sees.
    Returns the node, so a placement can end an expression.
    """
    for operation in reversed(operations):
        if operation[0] == 't':
            node.translate(operation[1])
        else:
            node.rotate(operation[1], operation[2])
    return node
