from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from core.diagnostics.diagnostics_service import (
    DiagnosticsService,
)


@dataclass
class HealthCheckItem:
    category: str
    title: str
    status: str
    value: str
    details: str = ""


@dataclass
class HealthCheckResult:
    success: bool
    overall_status: str
    summary: str
    items: list[HealthCheckItem]
    issues: list[str]
    recommendations: list[str]
    report_text: str


class ReportsService:
    """AIO Toolbox Support Health Check."""

    def __init__(self) -> None:
        self.diagnostics = DiagnosticsService()

    def run_health_check(
        self,
        database: dict | None = None,
    ) -> HealthCheckResult:
        items: list[HealthCheckItem] = []
        issues: list[str] = []
        recommendations: list[str] = []

        self._check_system_information(
            items,
            issues,
            recommendations,
        )

        self._check_memory(
            items,
            issues,
            recommendations,
        )

        self._check_disks(
            items,
            issues,
            recommendations,
        )

        self._check_graphics(
            items,
            issues,
            recommendations,
        )

        self._check_network(
            items,
            issues,
            recommendations,
        )

        self._check_processes(
            items,
            issues,
            recommendations,
        )

        self._check_services(
            items,
            issues,
            recommendations,
        )

        self._check_windows_update(
            items,
            issues,
            recommendations,
        )

        self._check_system_errors(
            items,
            issues,
            recommendations,
        )

        if database:
            items.append(
                HealthCheckItem(
                    category="DATABASE",
                    title="Database",
                    status="OK",
                    value=(
                        database.get("name")
                        or "Connected"
                    ),
                    details=(
                        f"Server: "
                        f"{database.get('server') or '-'}"
                    ),
                )
            )
        else:
            items.append(
                HealthCheckItem(
                    category="DATABASE",
                    title="Database",
                    status="INFO",
                    value="Not connected",
                    details=(
                        "No active SQL Server database "
                        "is selected."
                    ),
                )
            )

        overall_status = (
            self._calculate_overall_status(
                items
            )
        )

        summary = self._create_summary(
            overall_status,
            issues,
        )

        if not recommendations:
            recommendations.append(
                "No immediate action is required."
            )

        report_text = self._build_report(
            overall_status=overall_status,
            summary=summary,
            items=items,
            issues=issues,
            recommendations=recommendations,
            database=database,
        )

        return HealthCheckResult(
            success=True,
            overall_status=overall_status,
            summary=summary,
            items=items,
            issues=issues,
            recommendations=recommendations,
            report_text=report_text,
        )

    # ------------------------------------------------------------------
    # Checks
    # ------------------------------------------------------------------

    def _check_system_information(
        self,
        items: list[HealthCheckItem],
        issues: list[str],
        recommendations: list[str],
    ) -> None:
        try:
            result = (
                self.diagnostics
                .system_information()
            )

            output = result.output

            computer = self._extract_value(
                output,
                "Computer Name",
            )

            windows = self._extract_value(
                output,
                "OS",
            )

            cpu = self._extract_value(
                output,
                "CPU",
            )

            ram = self._extract_value(
                output,
                "RAM",
            )

            uptime = self._extract_value(
                output,
                "Uptime",
            )

            items.append(
                HealthCheckItem(
                    category="SYSTEM",
                    title="Windows / System",
                    status="OK",
                    value=(
                        f"{computer or '-'} | "
                        f"{windows or '-'}"
                    ),
                    details=(
                        f"CPU: {cpu or '-'}\n"
                        f"RAM: {ram or '-'}\n"
                        f"Uptime: {uptime or '-'}"
                    ),
                )
            )

        except Exception as exc:
            issues.append(
                "Unable to collect system information."
            )

            recommendations.append(
                "Review Windows system information manually."
            )

            items.append(
                HealthCheckItem(
                    category="SYSTEM",
                    title="Windows / System",
                    status="WARNING",
                    value="Unable to check",
                    details=str(exc),
                )
            )

    def _check_memory(
        self,
        items: list[HealthCheckItem],
        issues: list[str],
        recommendations: list[str],
    ) -> None:
        try:
            result = self.diagnostics.memory()
            output = result.output

            total = self._extract_value(
                output,
                "Total RAM",
            )

            used = self._extract_value(
                output,
                "Used RAM",
            )

            available = self._extract_value(
                output,
                "Available RAM",
            )

            usage_text = self._extract_value(
                output,
                "Usage",
            )

            usage = self._parse_percent(
                usage_text
            )

            if usage is None:
                status = "OK"

            elif usage >= 95:
                status = "CRITICAL"

                issues.append(
                    f"RAM usage is critically high "
                    f"({usage_text})."
                )

                recommendations.append(
                    "Close unnecessary applications and "
                    "investigate processes using excessive RAM."
                )

            elif usage >= 80:
                status = "WARNING"

                issues.append(
                    f"RAM usage is high ({usage_text})."
                )

                recommendations.append(
                    "Check applications using large "
                    "amounts of memory."
                )

            else:
                status = "OK"

            items.append(
                HealthCheckItem(
                    category="SYSTEM",
                    title="Memory",
                    status=status,
                    value=(
                        f"{used or '-'} used / "
                        f"{total or '-'} total"
                    ),
                    details=(
                        f"Available: {available or '-'}\n"
                        f"Usage: {usage_text or '-'}"
                    ),
                )
            )

        except Exception as exc:
            issues.append(
                "Unable to collect memory information."
            )

            items.append(
                HealthCheckItem(
                    category="SYSTEM",
                    title="Memory",
                    status="WARNING",
                    value="Unable to check",
                    details=str(exc),
                )
            )

    def _check_disks(
        self,
        items: list[HealthCheckItem],
        issues: list[str],
        recommendations: list[str],
    ) -> None:
        try:
            result = self.diagnostics.disks()
            output = result.output

            drives = self._parse_disk_output(
                output
            )

            if not drives:
                items.append(
                    HealthCheckItem(
                        category="STORAGE",
                        title="Disk Space",
                        status="INFO",
                        value="Unable to read disk data",
                        details=output,
                    )
                )
                return

            worst_status = "OK"
            drive_messages: list[str] = []

            for drive in drives:
                free_percent = (
                    drive["free_percent"]
                )

                drive_messages.append(
                    f"{drive['device']} "
                    f"{free_percent:.1f}% free"
                )

                if free_percent < 5:
                    worst_status = "CRITICAL"

                    issues.append(
                        f"{drive['device']} drive has "
                        f"critically low free space "
                        f"({free_percent:.1f}%)."
                    )

                    recommendations.append(
                        f"Free disk space on "
                        f"{drive['device']} immediately."
                    )

                elif free_percent < 10:
                    if worst_status != "CRITICAL":
                        worst_status = "WARNING"

                    issues.append(
                        f"{drive['device']} drive has "
                        f"low free space "
                        f"({free_percent:.1f}%)."
                    )

                    recommendations.append(
                        f"Free additional disk space "
                        f"on {drive['device']}."
                    )

            items.append(
                HealthCheckItem(
                    category="STORAGE",
                    title="Disk Space",
                    status=worst_status,
                    value=" | ".join(
                        drive_messages
                    ),
                    details=output,
                )
            )

        except Exception as exc:
            issues.append(
                "Unable to collect disk information."
            )

            items.append(
                HealthCheckItem(
                    category="STORAGE",
                    title="Disk Space",
                    status="WARNING",
                    value="Unable to check",
                    details=str(exc),
                )
            )

    def _check_graphics(
        self,
        items: list[HealthCheckItem],
        issues: list[str],
        recommendations: list[str],
    ) -> None:
        try:
            result = (
                self.diagnostics.graphics()
            )

            lines = (
                result.output
                .splitlines()
            )

            value = ""

            for line in lines:
                stripped = line.strip()

                if (
                    stripped
                    and not stripped.startswith("Name")
                    and not stripped.startswith("---")
                ):
                    value = stripped
                    break

            items.append(
                HealthCheckItem(
                    category="HARDWARE",
                    title="Graphics",
                    status="OK",
                    value=(
                        value
                        or "Graphics information available"
                    ),
                    details=result.output,
                )
            )

        except Exception as exc:
            issues.append(
                "Unable to collect graphics information."
            )

            items.append(
                HealthCheckItem(
                    category="HARDWARE",
                    title="Graphics",
                    status="WARNING",
                    value="Unable to check",
                    details=str(exc),
                )
            )

    def _check_network(
        self,
        items: list[HealthCheckItem],
        issues: list[str],
        recommendations: list[str],
    ) -> None:
        try:
            result = self.diagnostics.network()
            output = result.output.strip()

            if not output:
                status = "WARNING"

                issues.append(
                    "No active network configuration "
                    "was found."
                )

                recommendations.append(
                    "Check network adapters and connectivity."
                )

                value = "No active network"

            else:
                status = "OK"
                value = (
                    "Active network configuration found"
                )

            items.append(
                HealthCheckItem(
                    category="NETWORK",
                    title="Network",
                    status=status,
                    value=value,
                    details=output,
                )
            )

        except Exception as exc:
            issues.append(
                "Unable to collect network information."
            )

            recommendations.append(
                "Check network adapters and connectivity."
            )

            items.append(
                HealthCheckItem(
                    category="NETWORK",
                    title="Network",
                    status="WARNING",
                    value="Unable to check",
                    details=str(exc),
                )
            )

    def _check_processes(
        self,
        items: list[HealthCheckItem],
        issues: list[str],
        recommendations: list[str],
    ) -> None:
        try:
            result = (
                self.diagnostics.processes()
            )

            items.append(
                HealthCheckItem(
                    category="SYSTEM",
                    title="Processes",
                    status="OK",
                    value="Process information collected",
                    details=result.output,
                )
            )

        except Exception as exc:
            items.append(
                HealthCheckItem(
                    category="SYSTEM",
                    title="Processes",
                    status="INFO",
                    value="Unable to check",
                    details=str(exc),
                )
            )

    def _check_services(
        self,
        items: list[HealthCheckItem],
        issues: list[str],
        recommendations: list[str],
    ) -> None:
        try:
            result = (
                self.diagnostics.services()
            )

            output = result.output

            non_running = (
                self._extract_non_running_services(
                    output
                )
            )

            if non_running:
                count = len(non_running)

                status = "WARNING"

                issues.append(
                    f"{count} automatic Windows "
                    f"service(s) are not running."
                )

                recommendations.append(
                    "Review automatic services that "
                    "are not running and verify whether "
                    "they are required."
                )

                value = (
                    f"{count} automatic service(s) "
                    f"not running"
                )

            else:
                status = "OK"

                value = (
                    "Automatic services appear healthy"
                )

            items.append(
                HealthCheckItem(
                    category="WINDOWS",
                    title="Services",
                    status=status,
                    value=value,
                    details=output,
                )
            )

        except Exception as exc:
            issues.append(
                "Unable to collect Windows service information."
            )

            items.append(
                HealthCheckItem(
                    category="WINDOWS",
                    title="Services",
                    status="WARNING",
                    value="Unable to check",
                    details=str(exc),
                )
            )

    def _check_windows_update(
        self,
        items: list[HealthCheckItem],
        issues: list[str],
        recommendations: list[str],
    ) -> None:
        try:
            result = (
                self.diagnostics.windows_update()
            )

            output = result.output

            service_status = (
                self._extract_value(
                    output,
                    "Windows Update service",
                )
            )

            start_type = (
                self._extract_value(
                    output,
                    "Update service start",
                )
            )

            if service_status and (
                service_status.lower()
                in {
                    "running",
                    "startpending",
                }
            ):
                status = "OK"

                value = (
                    "Windows Update service running"
                )

            elif service_status:
                status = "WARNING"

                issues.append(
                    "Windows Update service is not running."
                )

                recommendations.append(
                    "Check Windows Update service "
                    "and Windows Update settings."
                )

                value = (
                    f"Service status: "
                    f"{service_status}"
                )

            else:
                status = "INFO"

                value = (
                    "Update status unavailable"
                )

            items.append(
                HealthCheckItem(
                    category="WINDOWS",
                    title="Windows Update",
                    status=status,
                    value=value,
                    details=(
                        f"{output}\n"
                        f"Start type: "
                        f"{start_type or '-'}"
                    ),
                )
            )

        except Exception as exc:
            items.append(
                HealthCheckItem(
                    category="WINDOWS",
                    title="Windows Update",
                    status="INFO",
                    value="Unable to check",
                    details=str(exc),
                )
            )

    def _check_system_errors(
        self,
        items: list[HealthCheckItem],
        issues: list[str],
        recommendations: list[str],
    ) -> None:
        try:
            result = (
                self.diagnostics.event_log_errors()
            )

            output = result.output.strip()

            if (
                not output
                or output.startswith(
                    "No System error events"
                )
            ):
                status = "OK"

                value = (
                    "No recent System errors found"
                )

            else:
                error_count = (
                    self._count_event_blocks(
                        output
                    )
                )

                if error_count >= 50:
                    status = "CRITICAL"
                else:
                    status = "WARNING"

                issues.append(
                    f"Recent System errors detected "
                    f"({error_count} event(s))."
                )

                recommendations.append(
                    "Review recent System Event Log "
                    "errors to identify recurring problems."
                )

                value = (
                    f"{error_count} recent error event(s)"
                )

            items.append(
                HealthCheckItem(
                    category="WINDOWS",
                    title="System Errors",
                    status=status,
                    value=value,
                    details=output,
                )
            )

        except Exception as exc:
            items.append(
                HealthCheckItem(
                    category="WINDOWS",
                    title="System Errors",
                    status="INFO",
                    value="Unable to check",
                    details=str(exc),
                )
            )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_value(
        output: str,
        key: str,
    ) -> str:
        for line in output.splitlines():
            stripped = line.strip()

            if stripped.lower().startswith(
                key.lower()
            ):
                if ":" in stripped:
                    return stripped.split(
                        ":",
                        1,
                    )[1].strip()

        return ""

    @staticmethod
    def _parse_percent(
        value: str,
    ) -> float | None:
        if not value:
            return None

        try:
            return float(
                value.replace(
                    "%",
                    "",
                ).strip()
            )
        except ValueError:
            return None

    @staticmethod
    def _parse_disk_output(
        output: str,
    ) -> list[dict]:
        """
        Parse Win32_LogicalDisk Format-Table output.

        The VolumeName column may contain spaces, therefore
        we do not rely on fixed column positions. Instead,
        the last three numeric values are interpreted as:

            SizeGB
            FreeGB
            FreePercent
        """

        drives: list[dict] = []

        for line in output.splitlines():
            stripped = line.strip()

            if not stripped:
                continue

            if stripped.startswith(
                "DeviceID"
            ):
                continue

            if stripped.startswith(
                "----"
            ):
                continue

            device_match = re.match(
                r"^([A-Za-z]:)",
                stripped,
            )

            if not device_match:
                continue

            device = (
                device_match
                .group(1)
                .upper()
            )

            remainder = stripped[
                device_match.end():
            ].strip()

            number_matches = re.findall(
                r"(?<![A-Za-z0-9])"
                r"(\d+(?:\.\d+)?)"
                r"(?![A-Za-z0-9])",
                remainder,
            )

            if len(number_matches) < 3:
                continue

            try:
                size_gb = float(
                    number_matches[-3]
                )

                free_gb = float(
                    number_matches[-2]
                )

                free_percent = float(
                    number_matches[-1]
                )

            except ValueError:
                continue

            if (
                size_gb <= 0
                or free_gb < 0
                or free_percent < 0
                or free_percent > 100
            ):
                continue

            drives.append(
                {
                    "device": device,
                    "size_gb": size_gb,
                    "free_gb": free_gb,
                    "free_percent": free_percent,
                }
            )

        return drives

    @staticmethod
    def _extract_non_running_services(
        output: str,
    ) -> list[str]:
        lines = output.splitlines()

        marker_found = False
        services: list[str] = []

        for line in lines:
            stripped = line.strip()

            if (
                "Non-running automatic services"
                in stripped
            ):
                marker_found = True
                continue

            if not marker_found:
                continue

            if not stripped:
                continue

            if (
                stripped.startswith("Name")
                or stripped.startswith("---")
            ):
                continue

            services.append(
                stripped
            )

        return services

    @staticmethod
    def _count_event_blocks(
        output: str,
    ) -> int:
        count = 0

        for line in output.splitlines():
            if line.strip().startswith(
                "TimeCreated"
            ):
                count += 1

        if count == 0:
            return max(
                1,
                output.count(
                    "ProviderName"
                ),
            )

        return count

    @staticmethod
    def _calculate_overall_status(
        items: list[HealthCheckItem],
    ) -> str:
        statuses = {
            item.status
            for item in items
        }

        if "CRITICAL" in statuses:
            return "CRITICAL"

        if "WARNING" in statuses:
            return "WARNING"

        if "OK" in statuses:
            return "HEALTHY"

        return "INFO"

    @staticmethod
    def _create_summary(
        overall_status: str,
        issues: list[str],
    ) -> str:
        if overall_status == "HEALTHY":
            return (
                "No problems requiring attention "
                "were detected."
            )

        if overall_status == "WARNING":
            return (
                f"{len(issues)} issue(s) require "
                "attention, but no critical condition "
                "was detected."
            )

        if overall_status == "CRITICAL":
            return (
                f"{len(issues)} issue(s) detected, "
                "including at least one critical condition."
            )

        return (
            "The health check completed with limited "
            "information."
        )

    def _build_report(
        self,
        overall_status: str,
        summary: str,
        items: list[HealthCheckItem],
        issues: list[str],
        recommendations: list[str],
        database: dict | None,
    ) -> str:
        generated = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        lines: list[str] = []

        lines.append(
            "AIO TOOLBOX - SUPPORT HEALTH CHECK"
        )
        lines.append(
            "=" * 78
        )
        lines.append(
            f"Generated       : {generated}"
        )
        lines.append(
            f"Overall Status  : {overall_status}"
        )
        lines.append(
            f"Summary         : {summary}"
        )
        lines.append("")

        lines.append(
            "SYSTEM HEALTH"
        )
        lines.append(
            "-" * 78
        )

        for item in items:
            lines.append(
                f"[{item.status:<8}] "
                f"{item.title:<22} "
                f"{item.value}"
            )

        lines.append("")

        if database:
            lines.append(
                "DATABASE"
            )
            lines.append(
                "-" * 78
            )
            lines.append(
                f"Database        : "
                f"{database.get('name') or '-'}"
            )
            lines.append(
                f"Server          : "
                f"{database.get('server') or '-'}"
            )
            lines.append("")

        lines.append(
            "ISSUES FOUND"
        )
        lines.append(
            "-" * 78
        )

        if issues:
            for index, issue in enumerate(
                issues,
                1,
            ):
                lines.append(
                    f"{index}. {issue}"
                )
        else:
            lines.append(
                "No issues detected."
            )

        lines.append("")

        lines.append(
            "RECOMMENDED ACTIONS"
        )
        lines.append(
            "-" * 78
        )

        for index, recommendation in enumerate(
            recommendations,
            1,
        ):
            lines.append(
                f"{index}. {recommendation}"
            )

        lines.append("")
        lines.append(
            "Generated by AIO Toolbox"
        )
        lines.append(
            "Sunsoft Business Software Solutions"
        )

        return "\n".join(lines)