from __future__ import annotations

from pathlib import Path


class UDLLocator:
    """
    Finds UDL files used by Sunsoft installations.

    The locator searches the standard Sunsoft installation
    directories, while the database selector also allows the
    user to browse manually for any .udl file.
    """

    SEARCH_PATHS = (
        Path(r"C:\ProgramData\Sunsoft\BackOffice"),
        Path(r"C:\ProgramData\Sunsoft"),
        Path(r"C:\Program Files (x86)\Sunsoft Ltd"),
        Path(r"C:\Program Files\Sunsoft Ltd"),
    )

    @classmethod
    def find_all(cls) -> list[Path]:
        """
        Find all available UDL files without duplicates.
        """

        found: list[Path] = []

        for root in cls.SEARCH_PATHS:
            if not root.exists():
                continue

            try:
                for udl in root.rglob("*.udl"):
                    try:
                        resolved = udl.resolve()
                    except (
                        OSError,
                        RuntimeError,
                    ):
                        continue

                    if resolved not in found:
                        found.append(resolved)

            except (
                PermissionError,
                OSError,
            ):
                continue

        found.sort(
            key=lambda item: (
                item.name.lower(),
                str(item).lower(),
            )
        )

        return found

    @classmethod
    def find_initial(cls) -> str | None:
        """
        Return Initial.udl when one is available.
        """

        for udl in cls.find_all():
            if udl.name.lower() == "initial.udl":
                return str(udl)

        return None