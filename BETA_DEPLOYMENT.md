# Beta Deployment

This project uses Netlify as a public beta download website, not as the runtime for the desktop app.

The app is still a Python/Tkinter desktop application. Testers download a Windows build from GitHub Releases and run it locally.

## How the beta website works

- Netlify publishes the `site/` folder.
- `site/app.js` asks GitHub for the latest release.
- If the release has a `.exe`, `.zip`, or `.msi` asset, the download button points directly to that file.
- If there is no downloadable asset yet, the button falls back to the latest GitHub Release page.

## Netlify setup

1. Log in to Netlify.
2. Choose **Add new site**.
3. Choose **Import an existing project**.
4. Connect GitHub.
5. Select this repository.
6. Use these settings:

```text
Base directory: leave empty
Build command: leave empty
Publish directory: site
```

The repository also includes `netlify.toml`, so Netlify should detect `site` as the publish folder automatically.

## Automated Windows beta releases

The repository includes a GitHub Actions workflow:

```text
.github/workflows/build-windows.yml
```

It builds a Windows portable zip with PyInstaller and publishes it to GitHub Releases when a version tag is pushed.

The produced file is named like:

```text
Floorball-Shot-Plotter-v0.1.0-beta.1-windows.zip
```

## Creating a new beta release

From your local repo:

```bash
git pull
git tag v0.1.0-beta.1
git push origin v0.1.0-beta.1
```

GitHub Actions will then:

1. Install Python on a Windows runner.
2. Install the app requirements.
3. Install PyInstaller.
4. Build the desktop app into a portable Windows folder.
5. Zip the folder.
6. Create or update the GitHub Release for that tag.
7. Attach the Windows zip to the release.

The Netlify beta page will automatically point the main download button to the newest release asset.

## Manual workflow run

You can also test the build without creating a release:

1. Go to **GitHub > Actions**.
2. Open **Build Windows Beta**.
3. Click **Run workflow**.
4. Download the generated artifact from the workflow run.

Manual workflow runs create a downloadable artifact, but they do not publish a GitHub Release unless the workflow runs from a tag.

## Notes for testers

Testers should download and unzip the Windows package, then run:

```text
Floorball-Shot-Plotter.exe
```

Windows SmartScreen may warn testers because the app is not code-signed yet. That is expected for early beta builds.

## Tester feedback

The beta page links to GitHub Issues. You can replace that with a Google Form, email address, or another feedback tool later.
