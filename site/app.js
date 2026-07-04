const REPO = "Hekkipekki/Floorball-Shot-Plotter-V3";
const RELEASES_URL = `https://github.com/${REPO}/releases/latest`;
const API_URL = `https://api.github.com/repos/${REPO}/releases/latest`;

const downloadButton = document.getElementById("downloadButton");
const releaseStatus = document.getElementById("releaseStatus");
const releaseTitle = document.getElementById("releaseTitle");
const releaseNotes = document.getElementById("releaseNotes");

function isDownloadAsset(asset) {
  const name = asset.name.toLowerCase();
  return name.endsWith(".exe") || name.endsWith(".zip") || name.endsWith(".msi");
}

function formatDate(dateText) {
  if (!dateText) return "";
  return new Intl.DateTimeFormat(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(new Date(dateText));
}

function plainReleaseNotes(markdown) {
  if (!markdown) return "No release notes added yet.";
  return markdown
    .replace(/^#+\s*/gm, "")
    .replace(/\*\*/g, "")
    .trim();
}

async function loadLatestRelease() {
  try {
    const response = await fetch(API_URL, {
      headers: { Accept: "application/vnd.github+json" },
    });

    if (!response.ok) {
      throw new Error("No public release found yet.");
    }

    const release = await response.json();
    const asset = (release.assets || []).find(isDownloadAsset);
    const releaseName = release.name || release.tag_name || "Latest beta release";
    const published = formatDate(release.published_at);

    releaseTitle.textContent = releaseName;
    releaseNotes.textContent = plainReleaseNotes(release.body);

    if (asset) {
      downloadButton.href = asset.browser_download_url;
      downloadButton.textContent = `Download ${asset.name}`;
      releaseStatus.textContent = published
        ? `Latest beta: ${releaseName} · published ${published}`
        : `Latest beta: ${releaseName}`;
      return;
    }

    downloadButton.href = release.html_url || RELEASES_URL;
    releaseStatus.textContent = "Latest release found, but no .exe/.zip/.msi asset is attached yet.";
  } catch (error) {
    downloadButton.href = RELEASES_URL;
    releaseStatus.textContent = "No downloadable beta release found yet. Use View releases after a beta build is uploaded.";
    releaseTitle.textContent = "No beta release uploaded yet";
    releaseNotes.textContent = "Create a GitHub Release and attach a Windows .exe, .zip, or .msi build. This page will update automatically.";
  }
}

loadLatestRelease();
