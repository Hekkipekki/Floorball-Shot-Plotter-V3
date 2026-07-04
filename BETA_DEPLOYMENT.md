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

## Updating the beta download

Create a new GitHub Release whenever there is a new beta build.

1. Go to GitHub Releases.
2. Click **Draft a new release**.
3. Create a tag such as:

```text
v0.1.0-beta.1
```

4. Add release notes.
5. Upload the Windows build asset, for example:

```text
Floorball-Shot-Plotter-v0.1.0-beta.1.zip
Floorball-Shot-Plotter-v0.1.0-beta.1.exe
Floorball-Shot-Plotter-v0.1.0-beta.1.msi
```

6. Publish the release.

The Netlify beta page will automatically point the main download button to the latest downloadable release asset.

## Packaging note

The website is ready, but a downloadable app build still needs to be created and uploaded to GitHub Releases.

Recommended first beta build format:

```text
Windows zip or exe created with PyInstaller
```

A later improvement can add automated build/release creation with GitHub Actions.

## Tester feedback

The beta page links to GitHub Issues. You can replace that with a Google Form, email address, or another feedback tool later.
