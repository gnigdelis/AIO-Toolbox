from __future__ import annotations

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer


_ICON_PATHS: dict[str, str] = {
    "home": """
        <path d="M3 10.5L12 3l9 7.5"/>
        <path d="M5 9.5V21h14V9.5"/>
        <path d="M9 21v-6h6v6"/>
    """,

    "system": """
        <rect x="3" y="4" width="18" height="13" rx="2"/>
        <path d="M8 21h8"/>
        <path d="M12 17v4"/>
        <path d="M7 8h10"/>
    """,

    "network": """
        <circle cx="12" cy="12" r="8"/>
        <circle cx="12" cy="12" r="3"/>
        <path d="M12 4v5"/>
        <path d="M12 15v5"/>
        <path d="M4 12h5"/>
        <path d="M15 12h5"/>
    """,

    "remote": """
        <rect x="3" y="4" width="14" height="10" rx="2"/>
        <path d="M7 19h6"/>
        <path d="M10 14v5"/>
        <path d="M19 8v9"/>
        <path d="M16 12h6"/>
    """,

    "maintenance": """
        <path d="M14.7 6.3a4 4 0 0 0-5.1-2.1l3 3-3.4 3.4-3-3a4 4 0 0 0 2.1 5.1l-1.8 1.8"/>
        <path d="M5.5 19.5l5.2-5.2"/>
        <path d="M14 14l5.5 5.5"/>
        <path d="M17.5 12.5l-3-3"/>
    """,

    "backup": """
        <ellipse cx="12" cy="6" rx="7" ry="3"/>
        <path d="M5 6v6c0 1.7 3.1 3 7 3s7-1.3 7-3V6"/>
        <path d="M5 12v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6"/>
    """,

    "diagnostics": """
        <path d="M4 12h3l2-5 3 10 2-5h6"/>
        <path d="M4 4h16"/>
        <path d="M4 20h16"/>
    """,

    "utilities": """
        <rect x="4" y="4" width="6" height="6" rx="1"/>
        <rect x="14" y="4" width="6" height="6" rx="1"/>
        <rect x="4" y="14" width="6" height="6" rx="1"/>
        <rect x="14" y="14" width="6" height="6" rx="1"/>
    """,

    "reports": """
        <path d="M6 3h9l4 4v14H6z"/>
        <path d="M15 3v5h5"/>
        <path d="M9 13h6"/>
        <path d="M9 17h6"/>
    """,

    "settings": """
        <circle cx="12" cy="12" r="3"/>
        <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-1.8 1.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.1h-2.5v-.1a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1-1.8-1.8.1-.1A1.7 1.7 0 0 0 8.1 15a1.7 1.7 0 0 0-1.6-1H6.4v-2.5h.1a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9l-.1-.1 1.8-1.8.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.6v-.1H15v.1a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1 1.8 1.8-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.1V14h-.1a1.7 1.7 0 0 0-1.6 1z"/>
    """,

    "search": """
        <circle cx="10.5" cy="10.5" r="6.5"/>
        <path d="M16 16l5 5"/>
    """,

    "help": """
        <circle cx="12" cy="12" r="9"/>
        <path d="M9.5 9a2.6 2.6 0 1 1 4.7 1.5c-.8 1-2.2 1.3-2.2 3"/>
        <path d="M12 17h.01"/>
    """,

    "toolbox": """
        <path d="M8 7V5.5A2.5 2.5 0 0 1 10.5 3h3A2.5 2.5 0 0 1 16 5.5V7"/>
        <rect x="3" y="7" width="18" height="13" rx="2"/>
        <path d="M3 12h18"/>
        <path d="M10 12v2h4v-2"/>
    """,

    "arrow_right": """
        <path d="M5 12h14"/>
        <path d="M13 6l6 6-6 6"/>
    """,

    "activity": """
        <circle cx="12" cy="12" r="8"/>
        <path d="M12 7v5l3 2"/>
    """,

    "computer": """
        <rect x="3" y="4" width="18" height="13" rx="2"/>
        <path d="M8 21h8"/>
        <path d="M12 17v4"/>
    """,
}


def _build_svg(
    name: str,
    color: str,
    stroke_width: float = 1.8,
) -> bytes:
    """Build an SVG document for an icon."""

    paths = _ICON_PATHS.get(name)

    if paths is None:
        raise ValueError(
            f"Unknown AIO Toolbox icon: {name}"
        )

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg"
         width="24"
         height="24"
         viewBox="0 0 24 24"
         fill="none"
         stroke="{color}"
         stroke-width="{stroke_width}"
         stroke-linecap="round"
         stroke-linejoin="round">
        {paths}
    </svg>
    """

    return svg.encode("utf-8")


def _render_pixmap(
    name: str,
    color: str,
    size: int,
) -> QPixmap:
    """Render an SVG icon onto a transparent pixmap."""

    renderer = QSvgRenderer(
        QByteArray(
            _build_svg(
                name,
                color,
            )
        )
    )

    pixmap = QPixmap(
        size,
        size,
    )

    pixmap.fill(
        Qt.GlobalColor.transparent
    )

    painter = QPainter(pixmap)

    painter.setRenderHint(
        QPainter.RenderHint.Antialiasing,
        True,
    )

    painter.setRenderHint(
        QPainter.RenderHint.SmoothPixmapTransform,
        True,
    )

    renderer.render(painter)

    painter.end()

    return pixmap


def icon(
    name: str,
    color: str = "#26344D",
    size: int = 20,
) -> QIcon:
    """Create a QIcon from an AIO Toolbox SVG icon."""

    result = QIcon()

    pixmap_1x = _render_pixmap(
        name,
        color,
        size,
    )

    pixmap_2x = _render_pixmap(
        name,
        color,
        size * 2,
    )

    result.addPixmap(
        pixmap_1x
    )

    result.addPixmap(
        pixmap_2x
    )

    return result


def pixmap(
    name: str,
    color: str = "#26344D",
    size: int = 20,
) -> QPixmap:
    """Create a transparent QPixmap from an SVG icon."""

    return _render_pixmap(
        name,
        color,
        size,
    )