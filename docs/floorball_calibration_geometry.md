# Floorball Half-Rink Calibration Geometry

This document defines the working geometry for video calibration and GoPro-assisted plotting.

The current defensive-zone rink template represents **half of a standard 40m x 20m floorball rink**, so the plotted area is treated as:

```text
20m long x 20m wide
```

This is the defensive half only: from the end board behind the goal to the centre line.

## Coordinate system in metres

Use a real-world metre coordinate system first, independent of image pixels:

```text
x = left/right across rink width
y = distance from the end board behind the goal toward the centre line
```

```text
x = 0m   left board
x = 10m  rink centre / goal centre line
x = 20m  right board

 y = 0m   end board behind goal
 y = 3.5m goal line / goal-mouth line
 y = 20m  centre line
```

This makes the defensive half a 20m by 20m square in real rink coordinates.

## Current app/template pixel conversion

The current plot template uses the app coordinate range:

```text
plot_x = 0..1500
plot_y = 0..1000
```

The template is drawn with the centre line at the top and the end board at the bottom, so Y is visually inverted compared with the metre coordinate system.

Approximate conversion:

```python
plot_x = (x_m / 20.0) * 1500.0
plot_y = ((20.0 - y_m) / 20.0) * 1000.0
```

Reverse conversion:

```python
x_m = (plot_x / 1500.0) * 20.0
y_m = 20.0 - ((plot_y / 1000.0) * 20.0)
```

## Key half-rink references

| Landmark | Metres `(x, y)` | Approx app plot `(X, Y)` | Notes |
|---|---:|---:|---|
| Left centre-line board corner | `(0.0, 20.0)` | `(0, 0)` | Top-left of defensive half template |
| Centre-line midpoint | `(10.0, 20.0)` | `(750, 0)` | Top-centre calibration anchor |
| Right centre-line board corner | `(20.0, 20.0)` | `(1500, 0)` | Top-right of defensive half template |
| Left end-board corner | `(0.0, 0.0)` | `(0, 1000)` | Bottom-left end-board side |
| End-board midpoint behind goal | `(10.0, 0.0)` | `(750, 1000)` | Behind goal centre |
| Right end-board corner | `(20.0, 0.0)` | `(1500, 1000)` | Bottom-right end-board side |
| Goal centre on goal line | `(10.0, 3.5)` | `(750, 825)` | Main goal-mouth reference |
| Left goal post | `(9.2, 3.5)` | `(690, 825)` | Goal width 1.6m, centred |
| Right goal post | `(10.8, 3.5)` | `(810, 825)` | Goal width 1.6m, centred |
| Back centre of goal cage | `(10.0, 2.85)` | `(750, 858)` | Goal depth 0.65m behind goal line |
| Left defensive faceoff dot | `(1.5, 3.5)` | `(112, 825)` | Useful visible GoPro anchor if marked |
| Right defensive faceoff dot | `(18.5, 3.5)` | `(1388, 825)` | Useful visible GoPro anchor if marked |

## Goalkeeper / goal-zone area references

Working assumption for the visible large white goalie-area rectangle:

```text
width across rink: 5.0m
length/depth away from goal line: 4.0m
centred on x = 10m
rear edge on goal line y = 3.5m
front edge at y = 7.5m
```

| Landmark | Metres `(x, y)` | Approx app plot `(X, Y)` |
|---|---:|---:|
| Goalie-area lower-left corner | `(7.5, 3.5)` | `(562, 825)` |
| Goalie-area lower-centre | `(10.0, 3.5)` | `(750, 825)` |
| Goalie-area lower-right corner | `(12.5, 3.5)` | `(938, 825)` |
| Goalie-area upper-left corner | `(7.5, 7.5)` | `(562, 625)` |
| Goalie-area upper-centre | `(10.0, 7.5)` | `(750, 625)` |
| Goalie-area upper-right corner | `(12.5, 7.5)` | `(938, 625)` |

Working assumption for the smaller goal-crease rectangle:

```text
width across rink: 2.5m
length/depth away from goal line: 1.0m
centred on x = 10m
rear edge on goal line y = 3.5m
front edge at y = 4.5m
```

| Landmark | Metres `(x, y)` | Approx app plot `(X, Y)` |
|---|---:|---:|
| Goal-crease lower-left corner | `(8.75, 3.5)` | `(656, 825)` |
| Goal-crease lower-right corner | `(11.25, 3.5)` | `(844, 825)` |
| Goal-crease upper-left corner | `(8.75, 4.5)` | `(656, 775)` |
| Goal-crease upper-right corner | `(11.25, 4.5)` | `(844, 775)` |

## Recommended GoPro calibration sequence

For the recurring behind-goal GoPro view, ask for these points first because they are usually visible:

1. Left centre-line / far-left board reference.
2. Centre-line midpoint / far-centre board reference.
3. Right centre-line / far-right board reference.
4. Goalie-area lower-left corner.
5. Goal centre / goal-mouth centre on the goal line.
6. Goalie-area lower-right corner.
7. Goalie-area upper-centre or upper-left/upper-right corner.
8. Optional left/right defensive faceoff dots.

This should give enough reference points to compute a projective transform / homography from video pixels to real half-rink coordinates.

## Important implementation note

The current template is visually 1500 x 1000 pixels, so it is not square even though the real half-rink is 20m x 20m. Calibration math should therefore use real metre coordinates first, then convert to app plot coordinates only at the final rendering/logging step.

Do not tie the calibration transform directly to the background image aspect ratio. Store calibration in metre coordinates or normalized rink coordinates so it survives future template/image changes.
