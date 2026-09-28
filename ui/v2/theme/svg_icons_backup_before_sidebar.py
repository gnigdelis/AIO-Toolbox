from __future__ import annotations

from functools import lru_cache

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer


# Clean Windows-style outline icons used throughout AIO Toolbox.
_ICON_PATHS = {
    "home": (
        '<path d="M3 10.5 12 3l9 7.5"/>'
        '<path d="M5 9.5V21h14V9.5"/>'
        '<path d="M9.5 21v-6h5v6"/>'
    ),

    "network": (
        '<circle cx="12" cy="12" r="8.5"/>'
        '<path d="M3.5 12h17"/>'
        '<path d="M12 3.5c2.3 2.4 3.4 5.2 3.4 8.5S14.3 18.1 12 20.5"/>'
        '<path d="M12 3.5C9.7 5.9 8.6 8.7 8.6 12s1.1 6.1 3.4 8.5"/>'
    ),

    "headset": (
        '<path d="M4 13v-1a8 8 0 0 1 16 0v1"/>'
        '<path d="M4 13h3v6H5a1 1 0 0 1-1-1z"/>'
        '<path d="M20 13h-3v6h2a1 1 0 0 0 1-1z"/>'
        '<path d="M17 19c0 1.1-1.1 2-2.5 2H12"/>'
    ),

    "cart": (
        '<circle cx="9" cy="19" r="1.5"/>'
        '<circle cx="18" cy="19" r="1.5"/>'
        '<path d="M3 4h2l2.2 10.5h10.9L21 7H6"/>'
    ),

    "chart": (
        '<path d="M4 20V12M10 20V8M16 20V5M22 20H2"/>'
        '<path d="M4 9 10 6l6-3"/>'
    ),

    "calendar": (
        '<rect x="3" y="5" width="18" height="16" rx="2"/>'
        '<path d="M7 3v4M17 3v4M3 10h18"/>'
        '<path d="M7 14h3M14 14h3M7 18h3"/>'
    ),

    "database": (
        '<ellipse cx="12" cy="5.5" rx="7.5" ry="3"/>'
        '<path d="M4.5 5.5v6c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3v-6"/>'
        '<path d="M4.5 11.5v6c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3v-6"/>'
    ),

    "diagnostics": (
        '<path d="M2.5 13h4l2-5 3.5 9 2.5-6h3l2 2h2"/>'
    ),

    "grid": (
        '<rect x="4" y="4" width="6" height="6" rx="1"/>'
        '<rect x="14" y="4" width="6" height="6" rx="1"/>'
        '<rect x="4" y="14" width="6" height="6" rx="1"/>'
        '<rect x="14" y="14" width="6" height="6" rx="1"/>'
    ),

    "reports": (
        '<path d="M6 3h9l4 4v14H6z"/>'
        '<path d="M15 3v5h4"/>'
        '<path d="M9 12h6M9 16h6"/>'
    ),

    "settings": (
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="m19.4 15 .1.1-1.8 3.1-.2-.1a7.8 7.8 0 0 1-2.1 1.2V19a7.7 7.7 0 0 1-3.4 0v.3a7.8 7.8 0 0 1-2.1-1.2l-.2.1-1.8-3.1.1-.1a7.7 7.7 0 0 1-1.2-2.1H4v-3.6h.8A7.7 7.7 0 0 1 6 7.2l-.1-.1 1.8-3.1.2.1A7.8 7.8 0 0 1 10 3V2.7h4V3a7.8 7.8 0 0 1 2.1 1.2l.2-.1 1.8 3.1-.1.1a7.7 7.7 0 0 1 1.2 2.1h.8v3.6h-.8a7.7 7.7 0 0 1-1.2 2.1z"/>'
    ),

    "windows": (
        '<path d="M3 4.5 11 3.2v8.1H3z"/>'
        '<path d="M13 3l8-1v9.3h-8z"/>'
        '<path d="M3 13h8v8.1L3 19.8z"/>'
        '<path d="M13 13h8v9l-8-1z"/>'
    ),

    "user": (
        '<circle cx="12" cy="8" r="3.2"/>'
        '<path d="M5.5 20c.7-3.6 3-5.5 6.5-5.5s5.8 1.9 6.5 5.5"/>'
    ),

    "cpu": (
        '<rect x="6" y="6" width="12" height="12" rx="2"/>'
        '<path d="M9 9h6v6H9z"/>'
        '<path d="M9 2v4M15 2v4M9 18v4M15 18v4"/>'
        '<path d="M2 9h4M2 15h4M18 9h4M18 15h4"/>'
    ),

    "memory": (
        '<rect x="3" y="7" width="18" height="10" rx="2"/>'
        '<path d="M7 7v-2M11 7v-2M15 7v-2M19 7v-2"/>'
        '<path d="M7 17v2M11 17v2M15 17v2M19 17v2"/>'
        '<path d="M7 10h2v4H7zM11 10h2v4h-2zM15 10h2v4h-2z"/>'
    ),

    "drive": (
        '<rect x="3" y="5" width="18" height="14" rx="2"/>'
        '<path d="M6 15h12M8 9h8M17 16h.01"/>'
    ),

    "clock": (
        '<circle cx="12" cy="12" r="8.5"/>'
        '<path d="M12 7v5l3 2"/>'
    ),

    "search": (
        '<circle cx="10.5" cy="10.5" r="6.5"/>'
        '<path d="m16 16 5 5"/>'
    ),

    "help": (
        '<circle cx="12" cy="12" r="9"/>'
        '<path d="M9.5 9a2.6 2.6 0 1 1 4.8 1.4c-.8 1.1-2.3 1.5-2.3 3.1"/>'
        '<path d="M12 17h.01"/>'
    ),

    "toolbox": (
        '<path d="M5 8h14a2 2 0 0 1 2 2v9H3v-9a2 2 0 0 1 2-2z"/>'
        '<path d="M9 8V6a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/>'
        '<path d="M3 13h18"/>'
        '<path d="M10 13v2h4v-2"/>'
    ),

    "monitor": (
        '<rect x="3" y="4" width="18" height="13" rx="2"/>'
        '<path d="M8 21h8M12 17v4"/>'
    ),

    "maintenance": (
        '<path d="m14.5 5.5 4-2 2 2-2 4"/>'
        '<path d="m5 19 9.5-9.5"/>'
        '<path d="M4 20h4"/>'
    ),

    "activity": (
        '<circle cx="12" cy="12" r="8.5"/>'
        '<path d="M12 7v5l3 2"/>'
    ),
}


def _svg(name: str, color: str) -> str:
    path = _ICON_PATHS.get(name)

    if path is None:
        raise ValueError(
            f"Unknown AIO Toolbox icon: {name}"
        )

    return (
        '<svg '
        'xmlns="http://www.w3.org/2000/svg" '
        'width="24" '
        'height="24" '
        'viewBox="0 0 24 24" '
        'fill="none" '
        f'stroke="{color}" '
        'stroke-width="1.8" '
        'stroke-linecap="round" '
        'stroke-linejoin="round">'
        f"{path}"
        "</svg>"
    )


@lru_cache(maxsize=256)
def _render_pixmap(
    name: str,
    color: str,
    size: int,
) -> QPixmap:
    svg_data = QByteArray(
        _svg(name, color).encode("utf-8")
    )

    renderer = QSvgRenderer(svg_data)

    pixmap = QPixmap(
        size,
        size,
    )

    pixmap.fill(
        Qt.GlobalColor.transparent
    )

    painter = QPainter(pixmap)

    try:
        renderer.render(painter)
    finally:
        painter.end()

    return pixmap


def pixmap(
    name: str,
    color: str = "#26344D",
    size: int = 20,
) -> QPixmap:
    return _render_pixmap(
        name,
        color,
        size,
    )


def icon(
    name: str,
    color: str = "#26344D",
    size: int = 20,
) -> QIcon:
    return QIcon(
        _render_pixmap(
            name,
            color,
            size,
        )
    )