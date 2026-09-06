# Cable Chain Specification

## Purpose

The two cable chains as chains of links between their anchors, following the sled and the bridge, with the wires through them as flexible strands.

## Requirements

### Requirement: A chain has the links its travel needs and moves as a chain
Each cable chain SHALL have `ceil((pi*R + reach)/pitch) + 2` links, `R`
half the height between its anchors, `reach` the farthest the two runs
differ over the travel (the moving anchor's farthest stand beyond the
fixed one or short of it), `pitch` the link pitch (15.85 mm), and the two
a whole link lying straight in each anchor at either end of the travel:
19 for the X chain and 19 for the Z chain. Every link SHALL stand at its
own station along the run-bend-run curve a chain of that length makes
between the anchors, facing along it, turned over on the moving run. The
first link SHALL nest in the fixed anchor and the last in the moving one
at every position; no link SHALL touch the rails, the motor, the sled or
the tower it passes.

#### Scenario: The count
- **WHEN** the chains are built
- **THEN** each chain draws 19 links and no more, and at both ends of its
  travel its first and last links lie straight in their anchors

#### Scenario: Seated at both ends of the travel
- **WHEN** each axis stands at its home, at nought and at its far end
- **THEN** the first link interferes with the fixed anchor, the last with
  the moving anchor, and no link interferes with the machine

#### Scenario: A chain of links
- **WHEN** an axis is driven 33 mm
- **THEN** the first link has not moved, the last has moved with its
  anchor, and every link's centre stands between 0.9 of a pitch and one
  pitch from the next

### Requirement: The wires run through the chain as flexible strands
Each chain SHALL carry its wires -- 6 for X, 12 for Z -- as flexible
molejo leaves, one per wire in the design's wire colours, each a line, a
half turn and a line bound to the same split of the chain as the links,
at its hex-packed offset in the bundle. Every strand SHALL touch no link
and no other strand and stay within the links' envelope at every position.

#### Scenario: Inside the chain along the travel
- **WHEN** an axis stands at -30, 0 and 45 mm
- **THEN** each strand shares no volume with any link or any other strand,
  and its bounds lie within a millimetre of the links' envelope

#### Scenario: Published as shapes
- **WHEN** the model is serialized
- **THEN** the document is version 3 and carries 18 strands as flexible
  entries
