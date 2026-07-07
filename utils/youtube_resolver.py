"""Resolve YouTube/online video URLs into URLs VLC can play."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
    "www.youtu.be",
}


class OnlineVideoError(RuntimeError):
    """Raised when an online video URL cannot be resolved for VLC."""


@dataclass(frozen=True)
class ResolvedOnlineVideo:
    original_url: str
    playback_url: str
    title: str | None = None
    duration: float | None = None


def is_http_url(value: str | None) -> bool:
    parsed = urlparse(str(value or ""))
    return parsed.scheme.lower() in {"http", "https"} and bool(parsed.netloc)


def is_youtube_url(value: str | None) -> bool:
    parsed = urlparse(str(value or ""))
    host = parsed.netloc.lower()
    return host in YOUTUBE_HOSTS or host.endswith(".youtube.com")


def resolve_online_video(url: str) -> ResolvedOnlineVideo:
    """Return a direct playback URL suitable for VLC.

    yt-dlp handles YouTube's constantly changing player URLs and also supports
    many other video providers. The resolved URL is temporary, so callers should
    keep saving the original URL and resolve again when opening the clip.
    """

    url = (url or "").strip()
    if not is_http_url(url):
        raise OnlineVideoError("Please enter a valid http(s) video URL.")

    try:
        import yt_dlp  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on installed package
        raise OnlineVideoError(
            "yt-dlp is required for YouTube playback. Install requirements again with:\n\n"
            "pip install -r requirements.txt"
        ) from exc

    options = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "format": "best[protocol^=m3u8]/best[protocol^=http]/best",
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as exc:
        raise OnlineVideoError(f"Could not resolve online video:\n{exc}") from exc

    if not isinstance(info, dict):
        raise OnlineVideoError("The online video resolver did not return video information.")

    if "entries" in info:
        entries = [entry for entry in info.get("entries") or [] if entry]
        if not entries:
            raise OnlineVideoError("No playable videos were found in that URL.")
        info = entries[0]

    playback_url = info.get("url")
    if not playback_url:
        formats = info.get("formats") or []
        playable = [fmt for fmt in formats if fmt.get("url")]
        if playable:
            playback_url = playable[-1].get("url")

    if not playback_url:
        raise OnlineVideoError("Could not find a playable stream URL for VLC.")

    return ResolvedOnlineVideo(
        original_url=url,
        playback_url=str(playback_url),
        title=info.get("title"),
        duration=info.get("duration"),
    )
