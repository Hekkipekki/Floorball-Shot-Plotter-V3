const REPO = "Hekkipekki/Floorball-Shot-Plotter-V3";
const API_URL = `https://api.github.com/repos/${REPO}/releases/latest`;

const downloadButton = document.getElementById("downloadButton");
const releaseStatus = document.getElementById("releaseStatus");
const releaseTitle = document.getElementById("releaseTitle");
const releaseNotes = document.getElementById("releaseNotes");

function isDownloadAsset(asset) {
  const name = asset.name.toLowerCase();
  return name.endsWith(".zip") || name.endsWith(".exe") || name.endsWith(".msi");
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

function setDownloadUnavailable(message) {
  downloadButton.href = "#";
  downloadButton.textContent = "Build not ready yet";
  downloadButton.classList.add("is-disabled");
  downloadButton.setAttribute("aria-disabled", "true");
  releaseStatus.textContent = message;
}

function setDownloadAvailable(asset, releaseName, published) {
  downloadButton.href = asset.browser_download_url;
  downloadButton.textContent = "Download latest beta";
  downloadButton.classList.remove("is-disabled");
  downloadButton.removeAttribute("aria-disabled");
  downloadButton.setAttribute("download", asset.name);
  releaseStatus.textContent = published
    ? `${releaseName} · Windows download · ${published}`
    : `${releaseName} · Windows download`;
}

downloadButton.addEventListener("click", (event) => {
  if (downloadButton.classList.contains("is-disabled")) {
    event.preventDefault();
  }
});

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
      setDownloadAvailable(asset, releaseName, published);
      return;
    }

    setDownloadUnavailable("The beta page is live, but the Windows download is still being built. Please check back shortly.");
  } catch (error) {
    releaseTitle.textContent = "Windows beta build coming soon";
    releaseNotes.textContent = "The website is ready. The download button will activate automatically when the first Windows beta build is published.";
    setDownloadUnavailable("The Windows download is not ready yet. Please check back shortly.");
  }
}

loadLatestRelease();
