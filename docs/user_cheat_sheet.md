# Floorball Shot Plotter — User Cheat Sheet

This guide is for new beta testers who want a quick overview of what the app can do and how to use the main workflows.

## What the app is for

Floorball Shot Plotter is a desktop tool for logging **opponent shots and goals against your team** on a defensive-zone rink map.

You can use it to:

- plot opponent shots and goals
- log shot type, situation, shooter hand, passer hand, and pass origin
- review X/Y, distance, angle, and shot zone
- filter and customize the Shot Log
- link videos or video segments to logged shots
- load video clips and plot directly from video
- calibrate video angles to the rink background
- show heatmaps and danger-zone overlays
- save/load match files and export data

## Mouse controls quick reference

### Rink map / plotting view

- **Left-click on the rink** — add an opponent shot at that location.
- **Right-click on the rink** — add an opponent goal at that location.
- **Left-click during rink pass-origin selection** — mark where the opponent pass came from.

### Shot Log

- **Right-click a Shot Log row** — open the video-link menu for that logged event.
- **Link Offline Video** — attach a local video file to that event.
- **Link Online Video** — attach a video URL to that event.
- **Play / Edit Segment** — open a linked local clip and save the relevant start/stop segment.
- **Remove Video Link** — clear the video from that row.

### Video window

- **Video → Open Video Clip...** — open a video without selecting a shot first.
- **Plot: OFF / ON** — turn video plotting mode on or off.
- **Right-click in video while Plot mode is ON** — plot at that video location.
- **Right-click during video pass-origin selection** — mark the pass origin from video.
- **Left-click during calibration** — select the requested rink landmark in the video.
- **Skip Point** — skip a calibration landmark that is not visible in the video frame.

## Basic plotting

### Add a shot

1. Left-click the opponent shot location on the rink.
2. Select the game state, context, situation, shot type, shooter hand, and passer/pass origin if needed.
3. The shot appears on the rink and in the Shot Log.

### Add a goal

1. Right-click the opponent goal location on the rink.
2. Fill in the same event details.
3. The goal is logged separately from shots but still appears in the Shot Log.

### What the event dialog means

The dialog is written from your team’s defensive perspective.

Use it for **opponent events only**:

- **5v5 / Even strength** — normal opponent attacks.
- **Special teams** — opponent power play, shorthanded chances, 6v5, empty net.
- **Restart / set play against** — free hit, faceoff, penalty shot against.
- **Broken play / rebound against** — rebounds, screens, scrambles, failed clearances.

## Pass-origin logging

When an event has a passer:

1. Choose the opponent passer hand.
2. The app asks if you want to mark the pass origin manually.
3. Choose **Yes**.
4. On the rink map, left-click the pass-origin location.
5. In video Plot mode, right-click the pass-origin location in the video.

Use **No assist** when the shot is unassisted.

## Shot Log

The Shot Log is the table on the right side.

You can use it to review:

- result: shot or goal
- phase/context/situation
- shot type
- passer/shooter hand
- period
- X/Y coordinates
- pass-origin X/Y
- distance
- angle
- zone
- video links when available

### Filtering and columns

- Use the Shot Log dropdown/filter controls to focus on specific values.
- Use column visibility controls to hide/show columns.
- The Shot Log panel can be collapsed to the right.
- Drag the panel border left/right to resize it.

## Video links for logged shots

Use this when you have already logged a shot/goal and want to attach a clip afterwards.

1. Find the shot/goal in the Shot Log.
2. Right-click that Shot Log row.
3. Choose **Link Offline Video** for a local file, or **Link Online Video** for a URL.
4. A linked video row shows the video icon in the Shot Log.
5. Right-click the same row again and choose **Play / Edit Segment** to open the clip.
6. Save the start/stop segment if you only want the relevant part of the clip linked to that shot.
7. Use **Relink Offline Video**, **Relink Online Video**, or **Remove Video Link** if you need to change it later.

## Heatmaps

Use the view controls to switch between plot and heatmap views.

Available heatmap-style views include:

- standard shot heatmap
- goal heatmap
- save heatmap

Use **Heatmap Settings** from the top menu to adjust heatmap behavior.

## Shot Zone overlay

Use the top menu:

```text
Shot Zone → Show Shot Zone Overlay
```

This toggles a semi-transparent danger-zone overlay on top of the rink background.

The app looks for:

```text
assets/resources/xG/Danger Zones.png
```

If that file is missing, it falls back to older xG overlay images in the same folder.

## Video workflow

There are two video workflows:

- **Link video to an existing Shot Log row** when the event is already logged.
- **Open a standalone video and plot from it** when you want to create shots/goals directly from video.

### Open a video without logging first

Use:

```text
Video → Open Video Clip...
```

This opens a video clip directly so you can review it before plotting.

### Plot from video

1. Open a video.
2. Click **Plot: OFF** so it becomes **Plot: ON**.
3. Right-click the shot location in the video.
4. Choose **Add Shot here** or **Add Goal here**.
5. Fill in the event details.
6. If you choose manual pass origin, right-click the pass-origin location in the video.

Important: video plotting uses **right-click**. Left-click in the video is used for calibration landmark selection.

## Video calibration

Calibration maps video clicks to the rink background.

Use it when plotting directly from video, especially GoPro or fixed camera angles.

### Calibrate a video angle

1. Open a video.
2. Click **Calibrate**.
3. Left-click each requested rink landmark in the video.
4. If a landmark is outside the frame, use **Skip Point**.
5. When complete, the calibration is saved for that video file.

When reopening the same video, the app should restore the saved calibration automatically.

### Calibration landmarks

The current calibration sequence asks for these landmarks when visible:

1. Lower Left Goal Area
2. Lower Right Goal Area
3. Upper Right Goal Area
4. Upper Left Goal Area
5. Lower Left Goalie Area
6. Lower Right Goalie Area
7. Upper Left Goalie Area
8. Upper Right Goalie Area
9. Center of Goal Line
10. Upper Left Defensive Zone
11. Upper Right Defensive Zone
12. Center Faceoff Dot
13. Center of Defensive Zone
14. Left Center Defensive Zone
15. Right Center Defensive Zone
16. Lower Left Faceoff Dot
17. Lower Right Faceoff Dot
18. Behind Goal Near Board

The most reliable points are usually the goal-area and goalie-area corners, goal-line centre, visible faceoff dots, and clear defensive-zone board/line references.

## Calibration warnings

After calibration, the app checks basic geometry.

It may warn if:

- too few points were captured
- left/right points look reversed
- points that should be on the same line are too far apart
- a centre point is far from the expected midpoint

Warnings do not block saving, but they mean you should consider recalibrating.

## Save, load, and export

Use the top **File** menu:

- **Save CSV** — export the current log data.
- **Load CSV** — load previous match/event data.
- **Export Image** — export the current rink/plot view.

Use save/load when testing so you can verify that events, pass origins, and video data survive reopening.

## Useful testing checklist

Before reporting that a build is ready, test:

1. App starts normally.
2. Rink background appears.
3. Demo shots work if available.
4. Rink left-click Add Shot works.
5. Rink right-click Add Goal works.
6. Rink pass-origin left-click works.
7. Shot Log filtering works.
8. Shot Log collapse/resize works.
9. Link Offline Video from a Shot Log row works.
10. Play / Edit Segment from a linked Shot Log row works.
11. Save/load works.
12. Heatmap views work.
13. Shot Zone overlay toggles on/off.
14. Video opens and plays with VLC.
15. Video Plot mode right-click Add Shot/Add Goal works.
16. Video pass-origin right-click works.
17. Video calibration left-click landmarks work.
18. Video calibration saves and restores.
19. Downloaded release zip contains `assets`, `data`, and bundled `vlc` folders.

## Common notes

- The app is desktop-first and runs locally.
- The Netlify website is only the download/beta page.
- The download button on Netlify always points to the latest GitHub Release.
- App-only code changes require a new GitHub Release before testers get the update.
- xG model development is not the current priority; the app is currently xG-ready by collecting useful event features.
