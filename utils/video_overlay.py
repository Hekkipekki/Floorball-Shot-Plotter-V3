"""Video overlay creation helpers."""

from __future__ import annotations


def show_video_overlay(*args, **kwargs) -> None:
    from utils.videoplayer import show_video_overlay as _show_video_overlay

    _show_video_overlay(*args, **kwargs)
