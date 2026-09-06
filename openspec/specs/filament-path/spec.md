# Filament Path Specification

## Purpose

The filament as one strand: the layer on the spool's hub and the free run through the brace's hole into the extruder, redrawn wherever the bridge stands.

## Requirements

### Requirement: The filament is loaded on the spool
The machine SHALL carry its filament as one flexible strand: the outermost
layer on the spool's hub, wound at the hub's radius plus half a stock, as
many whole turns at the stock's own diameter as the hub holds between the
flanges, centred on the hub.

#### Scenario: On the hub
- **WHEN** the strand is measured about the spool's axis
- **THEN** its nearest vertices stand at the hub's radius (48 mm) and its
  farthest at that plus one stock (49.75 mm), within 0.05 mm, and the layer
  lies within the hub's width

### Requirement: The run goes through the brace's hole into the extruder
The free run SHALL leave the top of the layer, turn until it is coming
straight down on the machine's axis 40 mm above the brace, drop through the
10 mm hole in the brace centre and end at the inlet: the top face of the
idler arm's bar, on the axis, at the bridge's height. It SHALL share no
volume with the brace, its endcaps, the right tower's rails, the spool
stand or the extruder's parts at any height of the bridge.

#### Scenario: Through the hole at every height
- **WHEN** the bridge stands at its home, at nought and at its top
- **THEN** the strand passes the hole's height within 4.9 mm of the axis,
  ends within 0.05 mm of the inlet's height on the axis, and interferes
  with nothing it passes

#### Scenario: Z redraws the run and leaves the spool
- **WHEN** the bridge is driven up 64 mm
- **THEN** the strand's end has risen 64 mm and every vertex on the spool
  stands where it stood
