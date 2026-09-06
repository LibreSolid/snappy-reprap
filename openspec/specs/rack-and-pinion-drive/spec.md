# Rack And Pinion Drive Specification

## Purpose

The pinion under each rack, turning with the sled at the rack's pitch and standing in the rack's gaps, with the design's herringbone drift recorded.

## Requirements

### Requirement: Each pinion turns with its rack at the rack's pitch
The drive gear under each rack, with the nut and grub screw pressed into
it, SHALL turn about the motor's axis as its sled travels: one turn per
`gear_teeth * rack_tooth_size` (80 mm) of travel, counter-clockwise seen
from above as the sled goes forward along the segment's own -y, which is
the way both sleds go when their drivers are positive.

#### Scenario: A tooth of travel is a tooth of turn
- **WHEN** a sled is driven one rack tooth (10/3 mm) from rest
- **THEN** its pinion's vertices stand exactly where they stood at rest
- **WHEN** it is driven half a tooth
- **THEN** the pinion has turned exactly 7.5 degrees

### Requirement: The pinion stands in the rack's gaps
At rest and at every position of the travel the pinion SHALL stand at the
phase where it shares least metal with its racks. Because the design's
herringbone pair -- an involute extruded with a twist against a straight
rack skewed -- drifts along the tooth, that least is not nought: the
contract is that the X pinion shares under 46 mm^3 with its racks at every
sampled position, the Y pinion under 49 mm^3 (the Y sled's halves stand
half a millimetre apart where the X sled's touch, so its racks are a
quarter of a millimetre out of pitch either way), that each shares more
turned a quarter tooth, and that in a 1 mm slab three millimetres below
the chevron's apex each shares under 0.2 mm^3 at the phase and over
3 mm^3 a half tooth off.

#### Scenario: The phase holds along the travel
- **WHEN** each axis is driven to -94.5, -30, 0, 1, 21.7 and 60 mm
- **THEN** at each, the X pinion shares under 46 mm^3 with its racks and
  the Y pinion under 49 mm^3, and turned 3.75 degrees each shares more

#### Scenario: A slab of the pair is clean
- **WHEN** each pinion and its racks are cut to a 1 mm slab at -40 and 45
  mm of travel
- **THEN** the slab shares under 0.2 mm^3 at the phase and over 3 mm^3
  with the pinion turned half a tooth
