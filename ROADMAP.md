# Floorball Shot Plotter V3 Roadmap

This document tracks the completed refactor work and the agreed direction for future feature development.

Current priority is beta stability, smoother plotting workflow, packaging reliability, tester feedback, and video-assisted plotting. xG model development remains parked unless Daniel explicitly asks to resume it.

## Workflow

- Work directly on `main` for normal cleanup and small feature changes.
- Before larger refactors or behavior changes, create a flat backup branch, for example `backup-main-before-feature-name`.
- Prefer broad but themed batches: inspect a wider file group first, then make a safe grouped change, then pull/test once at the end.
- Keep refactor changes behavior-preserving unless a functionality change is discussed first.
- Avoid broad rewrites of sensitive working modules unless there is a bug or clear feature need.
- Do not waste Netlify credits with app-code-only changes. Netlify should only deploy for `/site` or `netlify.toml` changes.

## Current Beta Priorities

### 1. Beta release stability

Status: active.

Focus:

- Keep Windows zip builds stable through GitHub Actions.
- Confirm packaged app assets load correctly beside the executable.
- Verify bundled/local VLC playback works in packaged releases.
- Keep Netlify deploys limited to `/site` and `netlify.toml` changes.
- Keep the Netlify beta download button pulling the latest GitHub Release dynamically.

Beta smoke test checklist:

1. Rink/background appears.
2. VLC video playback works.
3. Demo shots work.
4. Save/load works.
5. Shot log collapse/resize works.
6. Shot log scrolling and column filtering work.
7. Video overlay segment controls still work.
8. Basic video-assisted plotting does not break normal shot/goal logging.

### 2. Shot log UX

Status: active.

Completed / in progress:

- Shot log can collapse fully to the right.
- Shot log can be resized by dragging its left border.
- Shot log uses a small visible flap button to hide/show the panel.
- Shot log has horizontal scrolling so all xG-ready fields can be visible.
- Shot log column filtering remains available through the Columns menu.

Next refinements:

- Keep improving the collapsible/resizable behavior based on tester feedback.
- Make sure the panel does not interfere with video overlay controls.
- Keep column filtering usable as the number of logged fields grows.

### 3. Video-assisted plotting

Status: prototype started.

Current direction:

- Stabilize the current video overlay `Plot: ON` workflow.
- Allow right-clicking video locations to create shot/goal entries through the normal dialog flow.
- Keep the current simple normalized video-to-rink mapping as a fallback.
- Make video plotting status clear in the UI.
- Keep this separate from xG model development.

Important limitation:

- The first prototype maps video screen position proportionally to rink coordinates. This is useful for workflow testing but is not accurate enough for real camera perspective.
- Accurate plotting from GoPro footage requires calibration from known rink landmarks.

### 4. GoPro calibration preset

Status: planned next major beta feature.

Goal:

- Add a guided calibration mode for recurring GoPro behind-goal recordings.
- Use visible rink markings and board/goal-area landmarks to compute a video-to-rink coordinate transform.
- Make plotting from GoPro video faster and more accurate.

Preferred GoPro calibration anchors:

- Far/upper left board or rink-frame reference point.
- Far/upper center board reference point.
- Far/upper right board or rink-frame reference point.
- Left lower goalie-area / goal-zone corner.
- Center front goal-line or goal-mouth reference point.
- Right lower goalie-area / goal-zone corner.
- Upper/center goalie-area reference point when visible.
- Optional visible faceoff dots or board-side references.

Suggested UX:

1. Open linked video segment from the shot log.
2. Choose **Calibration Mode**.
3. Select **GoPro Behind Goal preset**.
4. App draws numbered calibration dots on the rink template.
5. User clicks the matching locations in the video frame.
6. App computes and stores the calibration transform for that video/camera angle.
7. Future video right-click plotting uses calibrated rink coordinates when available.
8. App falls back to simple normalized mapping when no calibration exists.

Technical direction:

- Store calibration metadata separately from xG logic.
- Use a projective transform / homography when enough reference points are provided.
- Persist calibration per video path or match/video entry.
- Add reset/recalibrate actions.
- Make calibration status obvious in the video overlay.

Related tracking issue:

- GitHub issue #2: Video calibration for accurate shot plotting from rink reference points.

### 5. Tester feedback loop

Status: active.

Collect feedback on:

- Install/open experience.
- Rink/background loading.
- VLC/video playback.
- Demo shot generation.
- Save/load reliability.
- Shot log usability.
- Video-assisted plotting accuracy and workflow.
- Packaging/release download flow.

Prefer larger cleanup/refactor batches instead of many tiny commits.

## Completed Phases

### Phase 1 - Video runtime cleanup

Status: complete.

Completed work:

- Video runtime logic split out.
- Segment playback behavior fixed:
  - Loop ON loops between Start and Stop.
  - Loop OFF pauses cleanly at Stop.
- Video looping issues resolved.

### Phase 2 - Video overlay separation

Status: complete.

Completed work:

- Video overlay logic extracted into its own module.
- Video overlay responsibilities separated from the rest of the GUI code.

### Phase 3 - Video player cleanup

Status: complete.

Completed work:

- Video player styling extracted into `utils/video_player_style.py`.
- VLC runtime helpers extracted into `utils/video_runtime.py`.
- Overlay creation extracted into `utils/video_overlay.py`.

### Phase 4 - Split `gui/controls.py`

Status: complete.

Completed work:

- `gui/controls.py` now acts as a small orchestrator.
- Control panel sections are split into `gui/panels/controls/` modules.
- Left, center, and right panels have clearer module boundaries.

### Phase 5 - Major GUI/core/data cleanup

Status: complete / stabilized.

Completed work:

- Cleaned and split control-panel setup modules.
- Cleaned layout and panel setup helpers.
- Cleaned Shot Log view and Shot Log interaction helpers.
- Cleaned plot rendering refresh helpers.
- Cleaned app refresh helpers.
- Cleaned app startup/initial-state helpers.
- Cleaned core stats calculations.
- Cleaned demo generation helpers.
- Cleaned match-store save/load dialog helpers.
- Cleaned entry schema/helpers and serialization helpers.
- Cleaned assets/path/export/video-runtime helpers.
- Cleaned video overlay and video button style helpers.
- Cleaned plot-click, event-finalize, popup-positioning, and pass-origin helpers.

Regression fixes completed during Phase 5:

- Fixed Remove Nearest so it removes the point nearest the mouse pointer over the rink/canvas instead of falling back to the latest plotted point.
- Added `gui/point_removal.py` for pointer-based point removal.
- Routed both canvas and global Space bindings through the pointer-based removal helper.
- Restored the trash icon on the Delete This Match button.
- Fixed assisted goals so they can ask for and store pass origin points like shots.
- Added event-aware pass-origin and plot-click helpers.

Confirmed working after the major refactor:

- App startup.
- Controls panel sections.
- Heatmap settings.
- Match manager buttons.
- Period controls.
- View mode dropdown.
- Shot Log display and interactions.
- Center plot click behavior.
- Space / Remove Nearest behavior.
- Trash icon display.
- Menu and startup behavior.
- Shot and goal creation.
- Goal pass-origin flow.
- Video overlay open/close behavior.
- Save/load match behavior.
- CSV import/export.
- Demo shot generation.
- Stats and expected-goals panels.

## Current Stable Point

The app is considered stable after the major refactor. Feature development has resumed around beta UX, packaging, shot log usability, and video-assisted plotting.

Stable branch to preserve this point:

```text
stable-after-major-refactor
```

Use this stable branch as a known-good rollback point before larger future feature work.

## Sensitive Files To Avoid Unless Needed

The following files are working and should not be broadly rewritten unless there is a bug or a clear feature need:

- `gui/point_removal.py`
- `gui/events/event_dialogs.py`
- `utils/videoplayer.py`
- `core/event_logic.py`
- `core/app_match_actions.py`

Reason:

- These files control deletion, dialog flow, event creation, video playback, or match state.
- Some broad rewrites were blocked by the connector payload filter.
- The cleanup benefit is now smaller than the regression risk.

## Recommended Next Steps

### 1. Stabilize video-assisted plotting prototype

- Locally test the video overlay `Plot: ON` control.
- Confirm right-click video plotting opens the correct shot/goal dialog.
- Confirm video controls, segment save, loop, close, and shot log interactions still work.
- Fix any beta regressions before adding calibration.

### 2. Design the GoPro calibration implementation

- Build the guided **GoPro Behind Goal preset** around the visible landmarks listed above.
- Start with a clear calibration UI before optimizing math/storage.
- Store calibration data safely and separately from match event data when possible.
- Keep a fallback when calibration is missing or invalid.

### 3. Use backup branches for bigger changes

Before any bigger feature branch or behavior change, create a flat backup branch from the current working `main`, for example:

```bash
git checkout main
git pull
git branch backup-main-before-feature-name
```

Or create the backup branch remotely before starting the next larger work batch.

### 4. Consider Phase 6 only if it becomes useful

Phase 6 would evaluate whether a cleaner service layer is worthwhile.

Do not start this automatically. Only consider it if there is a clear benefit, such as:

- reducing coupling between GUI and match data,
- making save/load easier to test,
- isolating business logic from Tkinter callbacks,
- supporting a bigger new feature safely.

Possible future service candidates:

- Match service.
- Shot/event service.
- Video link service.
- Statistics/xG service.

## Future Feature: Trained / Custom xG Model

Status: planned, low priority, parked until Daniel explicitly asks for it.

Goal:

- Build a better xG model from saved Shot Plotter games instead of relying only on the current rule-based zone model in `core/xg.py`.
- Use historical saved shots and goals as training data.
- Keep the current rule-based xG model as a safe fallback.

Priority note:

- Do not start xG model scaffolding, dependency changes, UI changes, or event-creation changes unless Daniel explicitly asks to resume xG work.
- Keep this section as a future reference item only.

Important model change:

- A real xG model should predict xG for both saved shots and goals.
- Goals should not automatically be treated as `xG = 1.0` in the trained model.
- Example: a low-quality shot that becomes a goal could still have `xG = 0.04`; a dangerous saved shot could have `xG = 0.60`.

Suggested training features:

- Shot X/Y location.
- Distance to goal.
- Shot angle to goal.
- Shot type.
- Situation.
- Phase.
- Shooter stick hand.
- Passer stick hand.
- Pass origin location when available.
- Pass distance / pass angle when available.
- Period.

Suggested implementation phases:

### xG Phase A - Data preparation

- Create a new module such as `core/xg_model.py`.
- Read all saved match JSON files from the matches folder.
- Convert events into training rows.
- Target value:
  - goal = 1
  - saved shot = 0

### xG Phase B - Model training

- Start with a simple model first, such as logistic regression.
- Keep dependencies minimal and discuss before adding new packages such as scikit-learn.
- Save the trained model to disk so it can be reused.

### xG Phase C - Prediction fallback

- Add `predict_xg(...)` that uses the trained model when available.
- Fall back to the current rule-based `get_xg_value(...)` when no trained model exists.

### xG Phase D - Recalculate existing matches

- Add a safe way to recalculate xG for the current match or all loaded matches.
- Avoid overwriting historical data without confirmation.
- Consider creating backups before bulk recalculation.

### xG Phase E - UI integration

Potential UI actions:

- `Train xG Model from Saved Matches`
- `Recalculate xG for Current Match`
- `Recalculate xG for Loaded Season`
- `Show xG Model Status`

Acceptance criteria:

- Existing rule-based xG still works if no trained model exists.
- Training does not change match data unless the user explicitly recalculates xG.
- Saved matches remain loadable with older app versions where practical.
- xG recalculation can be tested on a copied/backup match first.

## Notes for Next Session

Start from the current beta feature-development state.

Suggested first next action:

1. Pull latest `main` locally.
2. Confirm the latest app still starts.
3. Test shot log collapse/resize.
4. Test linked video playback and segment controls.
5. Test the video `Plot: ON` prototype.
6. Do not start trained/custom xG model work unless Daniel explicitly asks to resume it.
