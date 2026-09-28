from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass
class DiagnosticResult:
    success: bool
    title: str
    output: str
    details: str = ""


class DiagnosticsService:
    """Windows diagnostics used by AIO Toolbox."""

    CREATE_NO_WINDOW = getattr(
        subprocess,
        "CREATE_NO_WINDOW",
        0,
    )

    @classmethod
    def _run_powershell(
        cls,
        script: str,
        timeout: int = 30,
    ) -> str:

        process = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                script,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            creationflags=cls.CREATE_NO_WINDOW,
        )

        output = (
            process.stdout
            or process.stderr
        ).strip()

        if (
            process.returncode != 0
            and not output
        ):
            raise RuntimeError(
                "PowerShell diagnostic command failed."
            )

        return output

    # ------------------------------------------------------------------
    # System Information
    # ------------------------------------------------------------------

    def system_information(
        self,
    ) -> DiagnosticResult:

        script = r'''
$os = Get-CimInstance Win32_OperatingSystem
$cs = Get-CimInstance Win32_ComputerSystem
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$bios = Get-CimInstance Win32_BIOS | Select-Object -First 1
$uptime = (Get-Date) - $os.LastBootUpTime

@(
    "Computer Name : $env:COMPUTERNAME"
    "User          : $env:USERNAME"
    "OS            : $($os.Caption)"
    "Version       : $($os.Version)"
    "Build         : $($os.BuildNumber)"
    "Architecture  : $($os.OSArchitecture)"
    "CPU           : $($cpu.Name)"
    "CPU Cores     : $($cpu.NumberOfCores)"
    "CPU Threads   : $($cpu.NumberOfLogicalProcessors)"
    "RAM           : $([math]::Round($cs.TotalPhysicalMemory / 1GB, 2)) GB"
    "BIOS          : $($bios.Manufacturer) $($bios.SMBIOSBIOSVersion)"
    "Uptime        : $($uptime.Days)d $($uptime.Hours)h $($uptime.Minutes)m"
) -join "`n"
'''

        output = self._run_powershell(
            script
        )

        return DiagnosticResult(
            True,
            "System Information",
            output,
            "System information collected successfully.",
        )

    # ------------------------------------------------------------------
    # Memory
    # ------------------------------------------------------------------

    def memory(
        self,
    ) -> DiagnosticResult:

        script = r'''
$os = Get-CimInstance Win32_OperatingSystem

$total = [math]::Round(
    $os.TotalVisibleMemorySize / 1MB,
    2
)

$free = [math]::Round(
    $os.FreePhysicalMemory / 1MB,
    2
)

$used = [math]::Round(
    $total - $free,
    2
)

$percent = if ($total -gt 0) {
    [math]::Round(
        ($used / $total) * 100,
        1
    )
}
else {
    0
}

@(
    "Total RAM     : $total GB"
    "Used RAM      : $used GB"
    "Available RAM : $free GB"
    "Usage         : $percent%"
) -join "`n"
'''

        output = self._run_powershell(
            script
        )

        return DiagnosticResult(
            True,
            "Memory",
            output,
            "Memory status collected successfully.",
        )

    # ------------------------------------------------------------------
    # Disk Space
    # ------------------------------------------------------------------

    def disks(
        self,
    ) -> DiagnosticResult:

        script = r'''
Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" |
Select-Object DeviceID,
VolumeName,
@{
    N="SizeGB";
    E={
        [math]::Round(
            $_.Size / 1GB,
            2
        )
    }
},
@{
    N="FreeGB";
    E={
        [math]::Round(
            $_.FreeSpace / 1GB,
            2
        )
    }
},
@{
    N="FreePercent";
    E={
        if ($_.Size) {
            [math]::Round(
                ($_.FreeSpace / $_.Size) * 100,
                1
            )
        }
        else {
            0
        }
    }
} |
Format-Table -AutoSize |
Out-String -Width 180
'''

        output = self._run_powershell(
            script
        )

        return DiagnosticResult(
            True,
            "Disk Space",
            output,
            "Logical disk information collected successfully.",
        )

    # ------------------------------------------------------------------
    # Graphics
    # ------------------------------------------------------------------

    def graphics(
        self,
    ) -> DiagnosticResult:

        script = r'''
Get-CimInstance Win32_VideoController |
Select-Object Name,
@{
    N="DriverVersion";
    E={
        $_.DriverVersion
    }
},
@{
    N="Resolution";
    E={
        if ($_.CurrentHorizontalResolution) {
            "$($_.CurrentHorizontalResolution)x$($_.CurrentVerticalResolution)"
        }
        else {
            "-"
        }
    }
},
@{
    N="AdapterRAM";
    E={
        if ($_.AdapterRAM) {
            [math]::Round(
                $_.AdapterRAM / 1GB,
                2
            )
        }
        else {
            "-"
        }
    }
} |
Format-Table -AutoSize |
Out-String -Width 180
'''

        output = self._run_powershell(
            script
        )

        return DiagnosticResult(
            True,
            "Graphics",
            output,
            "GPU information collected successfully.",
        )

    # ------------------------------------------------------------------
    # Network
    # ------------------------------------------------------------------

    def network(
        self,
    ) -> DiagnosticResult:

        script = r'''
Get-NetIPConfiguration |
Where-Object {
    $_.NetAdapter.Status -eq "Up"
} |
ForEach-Object {

    "Interface : $($_.InterfaceAlias)"

    "IPv4      : $(
        (
            $_.IPv4Address |
            Select-Object -First 1
        ).IPv4Address
    )"

    "Gateway   : $(
        (
            $_.IPv4DefaultGateway |
            Select-Object -First 1
        ).NextHop
    )"

    "DNS       : $(
        (
            $_.DNSServer.ServerAddresses
        ) -join ", "
    )"

    ""
}
'''

        output = self._run_powershell(
            script
        )

        return DiagnosticResult(
            True,
            "Network Status",
            output,
            "Active network configuration collected successfully.",
        )

    # ------------------------------------------------------------------
    # Processes
    # ------------------------------------------------------------------

    def processes(
        self,
    ) -> DiagnosticResult:

        script = r'''
Get-Process |
Sort-Object CPU -Descending |
Select-Object -First 20 ProcessName,
Id,
@{
    N="CPUSeconds";
    E={
        if ($_.CPU) {
            [math]::Round(
                $_.CPU,
                1
            )
        }
        else {
            0
        }
    }
},
@{
    N="MemoryMB";
    E={
        [math]::Round(
            $_.WorkingSet64 / 1MB,
            1
        )
    }
} |
Format-Table -AutoSize |
Out-String -Width 180
'''

        output = self._run_powershell(
            script,
            timeout=30,
        )

        return DiagnosticResult(
            True,
            "Top Processes",
            output,
            "Top processes collected successfully.",
        )

    # ------------------------------------------------------------------
    # Services
    # ------------------------------------------------------------------

    def services(
        self,
    ) -> DiagnosticResult:

        script = r'''
$running = (
    Get-Service |
    Where-Object Status -eq "Running"
).Count

$stopped = (
    Get-Service |
    Where-Object Status -eq "Stopped"
).Count

$other = (
    Get-Service |
    Where-Object {
        $_.Status -notin @(
            "Running",
            "Stopped"
        )
    }
).Count

@(
    "Running : $running"
    "Stopped : $stopped"
    "Other   : $other"
    ""
    "Non-running automatic services:"
    (
        Get-CimInstance Win32_Service |
        Where-Object {
            $_.StartMode -eq "Auto" -and
            $_.State -ne "Running"
        } |
        Select-Object Name,
        State,
        StartMode |
        Format-Table -AutoSize |
        Out-String -Width 160
    )
) -join "`n"
'''

        output = self._run_powershell(
            script,
            timeout=30,
        )

        return DiagnosticResult(
            True,
            "Services Status",
            output,
            "Windows services status collected successfully.",
        )

    # ------------------------------------------------------------------
    # Windows Update
    # ------------------------------------------------------------------

    def windows_update(
        self,
    ) -> DiagnosticResult:

        script = r'''
$service = Get-Service `
    -Name wuauserv `
    -ErrorAction SilentlyContinue

$uso = Get-Process `
    -Name UsoClient `
    -ErrorAction SilentlyContinue

@(
    "Windows Update service : $($service.Status)"
    "Update service start   : $($service.StartType)"
    "Update client process  : $(
        if ($uso) {
            "Running"
        }
        else {
            "Not running"
        }
    )"
) -join "`n"
'''

        output = self._run_powershell(
            script
        )

        return DiagnosticResult(
            True,
            "Windows Update",
            output,
            "Windows Update status collected successfully.",
        )

    # ------------------------------------------------------------------
    # System Errors
    # ------------------------------------------------------------------

    def event_log_errors(
        self,
    ) -> DiagnosticResult:

        script = r'''
Get-WinEvent `
    -FilterHashtable @{
        LogName="System"
        Level=2
        StartTime=(Get-Date).AddDays(-7)
    } `
    -ErrorAction SilentlyContinue |
Select-Object -First 15 `
    TimeCreated,
    Id,
    ProviderName,
    Message |
Format-List |
Out-String -Width 200
'''

        output = self._run_powershell(
            script,
            timeout=30,
        )

        if not output:
            output = (
                "No System error events found "
                "in the last 7 days."
            )

        return DiagnosticResult(
            True,
            "System Errors",
            output,
            "Recent System error events collected successfully.",
        )

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------

    def execute(
        self,
        operation: str,
    ) -> DiagnosticResult:

        operations = {
            "system_information":
                self.system_information,

            "memory":
                self.memory,

            "disks":
                self.disks,

            "graphics":
                self.graphics,

            "network":
                self.network,

            "processes":
                self.processes,

            "services":
                self.services,

            "windows_update":
                self.windows_update,

            "event_log_errors":
                self.event_log_errors,
        }

        handler = operations.get(
            operation
        )

        if handler is None:
            raise ValueError(
                f"Unknown diagnostic operation: "
                f"{operation}"
            )

        return handler()