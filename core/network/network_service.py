from __future__ import annotations

import ipaddress
import re
import socket
import subprocess
from dataclasses import dataclass
from typing import Callable


@dataclass
class NetworkResult:
    success: bool
    title: str
    output: str
    details: str = ""


class NetworkService:
    """Windows network utilities used by AIO Toolbox."""

    CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    @classmethod
    def _run_command(
        cls,
        command: list[str],
        timeout: int = 30,
        line_callback: Callable[[str], None] | None = None,
    ) -> tuple[int, str, str]:
        """
        Run a Windows command.

        When line_callback is provided, stdout is streamed line-by-line
        while the command is running.
        """

        if line_callback is None:
            try:
                process = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    encoding="cp850",
                    errors="replace",
                    timeout=timeout,
                    creationflags=cls.CREATE_NO_WINDOW,
                )

                return (
                    process.returncode,
                    process.stdout.strip(),
                    process.stderr.strip(),
                )

            except subprocess.TimeoutExpired as exc:
                stdout = exc.stdout or ""
                stderr = exc.stderr or ""

                if isinstance(stdout, bytes):
                    stdout = stdout.decode(
                        "cp850",
                        errors="replace",
                    )

                if isinstance(stderr, bytes):
                    stderr = stderr.decode(
                        "cp850",
                        errors="replace",
                    )

                raise TimeoutError(
                    f"Η εντολή ξεπέρασε το όριο των "
                    f"{timeout} δευτερολέπτων.\n"
                    f"{stdout}\n"
                    f"{stderr}".strip()
                ) from exc

            except FileNotFoundError as exc:
                raise RuntimeError(
                    f"Δεν βρέθηκε η εντολή των Windows: "
                    f"{command[0]}"
                ) from exc

            except OSError as exc:
                raise RuntimeError(str(exc)) from exc

        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                text=True,
                encoding="cp850",
                errors="replace",
                bufsize=1,
                creationflags=cls.CREATE_NO_WINDOW,
            )

            lines: list[str] = []

            assert process.stdout is not None

            for raw_line in process.stdout:
                line = raw_line.rstrip("\r\n")
                lines.append(line)

                if line_callback is not None:
                    line_callback(line)

            returncode = process.wait(timeout=timeout)

            output = "\n".join(lines).strip()

            return (
                returncode,
                output,
                "",
            )

        except subprocess.TimeoutExpired as exc:
            process.kill()
            process.wait()

            raise TimeoutError(
                f"Η εντολή ξεπέρασε το όριο των "
                f"{timeout} δευτερολέπτων."
            ) from exc

        except FileNotFoundError as exc:
            raise RuntimeError(
                f"Δεν βρέθηκε η εντολή των Windows: "
                f"{command[0]}"
            ) from exc

        except OSError as exc:
            raise RuntimeError(str(exc)) from exc

    @staticmethod
    def _validate_host(host: str) -> str:
        host = host.strip()

        if not host:
            raise ValueError(
                "Πρέπει να εισάγεις hostname ή IP address."
            )

        if len(host) > 253:
            raise ValueError(
                "Το hostname είναι πολύ μεγάλο."
            )

        if any(
            char in host
            for char in (
                " ",
                "\t",
                "\r",
                "\n",
                ";",
                "|",
                "&",
                ">",
                "<",
                '"',
                "'",
                "`",
            )
        ):
            raise ValueError(
                "Το hostname ή IP address δεν είναι έγκυρο."
            )

        try:
            ipaddress.ip_address(host)
            return host
        except ValueError:
            pass

        hostname_pattern = re.compile(
            r"^(?=.{1,253}$)"
            r"(?:[A-Za-z0-9]"
            r"(?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)*"
            r"[A-Za-z0-9]"
            r"(?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$"
        )

        if not hostname_pattern.match(host):
            raise ValueError(
                "Το hostname ή IP address δεν είναι έγκυρο."
            )

        return host

    @staticmethod
    def _validate_port(port: int | str) -> int:
        try:
            value = int(str(port).strip())
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Η θύρα πρέπει να είναι αριθμός."
            ) from exc

        if not 1 <= value <= 65535:
            raise ValueError(
                "Η θύρα πρέπει να είναι μεταξύ "
                "1 και 65535."
            )

        return value

    @staticmethod
    def _clean_output(text: str) -> str:
        return text.replace("\x00", "").strip()

    # ------------------------------------------------------------------
    # Ping
    # ------------------------------------------------------------------

    def ping(
        self,
        host: str,
        count: int = 4,
        timeout_ms: int = 1000,
        line_callback: Callable[[str], None] | None = None,
    ) -> NetworkResult:

        host = self._validate_host(host)

        if not 1 <= count <= 20:
            raise ValueError(
                "Το πλήθος των ping πρέπει να είναι "
                "μεταξύ 1 και 20."
            )

        if not 100 <= timeout_ms <= 10000:
            raise ValueError(
                "Το timeout πρέπει να είναι μεταξύ "
                "100 και 10000 ms."
            )

        returncode, stdout, stderr = self._run_command(
            [
                "ping",
                "-n",
                str(count),
                "-w",
                str(timeout_ms),
                host,
            ],
            timeout=max(
                10,
                int((count * timeout_ms) / 1000) + 10,
            ),
            line_callback=line_callback,
        )

        output = self._clean_output(
            stdout or stderr
        )

        return NetworkResult(
            success=returncode == 0,
            title=f"Ping — {host}",
            output=output,
            details=(
                "Ο προορισμός απάντησε επιτυχώς."
                if returncode == 0
                else
                "Δεν λήφθηκε επιτυχής απάντηση "
                "από τον προορισμό."
            ),
        )

    # ------------------------------------------------------------------
    # Traceroute
    # ------------------------------------------------------------------

    def traceroute(
        self,
        host: str,
        max_hops: int = 30,
        timeout_ms: int = 1000,
        line_callback: Callable[[str], None] | None = None,
    ) -> NetworkResult:

        host = self._validate_host(host)

        if not 1 <= max_hops <= 64:
            raise ValueError(
                "Τα maximum hops πρέπει να είναι "
                "μεταξύ 1 και 64."
            )

        if not 100 <= timeout_ms <= 10000:
            raise ValueError(
                "Το timeout πρέπει να είναι μεταξύ "
                "100 και 10000 ms."
            )

        returncode, stdout, stderr = self._run_command(
            [
                "tracert",
                "-h",
                str(max_hops),
                "-w",
                str(timeout_ms),
                host,
            ],
            timeout=max(
                60,
                max_hops * 3,
            ),
            line_callback=line_callback,
        )

        output = self._clean_output(
            stdout or stderr
        )

        return NetworkResult(
            success=returncode == 0,
            title=f"Traceroute — {host}",
            output=output,
            details=(
                "Η διαδρομή ολοκληρώθηκε."
                if returncode == 0
                else
                "Η διαδρομή ολοκληρώθηκε με "
                "σφάλματα ή timeouts."
            ),
        )

    # ------------------------------------------------------------------
    # DNS Lookup
    # ------------------------------------------------------------------

    def dns_lookup(
        self,
        host: str,
    ) -> NetworkResult:

        host = self._validate_host(host)

        lines = [
            f"DNS Lookup: {host}",
            "",
        ]

        addresses: set[str] = set()

        try:
            results = socket.getaddrinfo(
                host,
                None,
                socket.AF_UNSPEC,
                socket.SOCK_STREAM,
            )

            for result in results:
                addresses.add(
                    result[4][0]
                )

        except socket.gaierror as exc:
            return NetworkResult(
                success=False,
                title=f"DNS Lookup — {host}",
                output=(
                    "DNS resolution failed.\n\n"
                    f"{exc}"
                ),
                details=(
                    "Δεν ήταν δυνατή η επίλυση "
                    "του hostname."
                ),
            )

        if addresses:
            lines.append(
                "Resolved addresses:"
            )

            for address in sorted(addresses):
                try:
                    parsed = ipaddress.ip_address(
                        address
                    )

                    address_type = (
                        "IPv4"
                        if parsed.version == 4
                        else "IPv6"
                    )

                except ValueError:
                    address_type = "IP"

                lines.append(
                    f"  {address:<40} "
                    f"{address_type}"
                )

        try:
            ipaddress.ip_address(host)

        except ValueError:
            pass

        else:
            try:
                reverse_name = socket.gethostbyaddr(
                    host
                )[0]

                lines.extend(
                    [
                        "",
                        "Reverse DNS:",
                        f"  {reverse_name}",
                    ]
                )

            except (
                socket.herror,
                socket.gaierror,
            ):
                lines.extend(
                    [
                        "",
                        "Reverse DNS:",
                        "  No PTR record found.",
                    ]
                )

        return NetworkResult(
            success=True,
            title=f"DNS Lookup — {host}",
            output="\n".join(lines),
            details=(
                f"Βρέθηκαν {len(addresses)} "
                "address(es)."
            ),
        )

    # ------------------------------------------------------------------
    # Port Test
    # ------------------------------------------------------------------

    def port_test(
        self,
        host: str,
        port: int | str,
        timeout: float = 2.0,
    ) -> NetworkResult:

        host = self._validate_host(host)
        port = self._validate_port(port)

        if not 0.5 <= timeout <= 30:
            raise ValueError(
                "Το timeout πρέπει να είναι μεταξύ "
                "0.5 και 30 sec."
            )

        try:
            with socket.create_connection(
                (host, port),
                timeout=timeout,
            ) as connection:

                local_address = (
                    connection.getsockname()
                )

                remote_address = (
                    connection.getpeername()
                )

            output = (
                f"Target\n"
                f"  Host:           {host}\n"
                f"  Port:           {port}\n"
                f"\n"
                f"Connection\n"
                f"  Status:         OPEN / REACHABLE\n"
                f"  Local endpoint: "
                f"{local_address[0]}:{local_address[1]}\n"
                f"  Remote endpoint:"
                f"{remote_address[0]}:{remote_address[1]}"
            )

            return NetworkResult(
                success=True,
                title=(
                    f"Port Test — "
                    f"{host}:{port}"
                ),
                output=output,
                details=(
                    "Η TCP σύνδεση ήταν επιτυχής."
                ),
            )

        except socket.timeout:

            output = (
                f"Target\n"
                f"  Host:   {host}\n"
                f"  Port:   {port}\n"
                f"\n"
                f"Connection\n"
                f"  Status: TIMEOUT"
            )

            return NetworkResult(
                success=False,
                title=(
                    f"Port Test — "
                    f"{host}:{port}"
                ),
                output=output,
                details=(
                    "Η σύνδεση έκανε timeout."
                ),
            )

        except ConnectionRefusedError:

            output = (
                f"Target\n"
                f"  Host:   {host}\n"
                f"  Port:   {port}\n"
                f"\n"
                f"Connection\n"
                f"  Status: CLOSED / REFUSED"
            )

            return NetworkResult(
                success=False,
                title=(
                    f"Port Test — "
                    f"{host}:{port}"
                ),
                output=output,
                details=(
                    "Ο host απάντησε αλλά η θύρα "
                    "απέρριψε τη σύνδεση."
                ),
            )

        except OSError as exc:

            output = (
                f"Target\n"
                f"  Host:   {host}\n"
                f"  Port:   {port}\n"
                f"\n"
                f"Connection\n"
                f"  Status: FAILED\n"
                f"  Error:  {exc}"
            )

            return NetworkResult(
                success=False,
                title=(
                    f"Port Test — "
                    f"{host}:{port}"
                ),
                output=output,
                details=(
                    "Η TCP σύνδεση απέτυχε."
                ),
            )

    # ------------------------------------------------------------------
    # IP Configuration
    # ------------------------------------------------------------------

    def ip_configuration(
        self,
    ) -> NetworkResult:

        returncode, stdout, stderr = (
            self._run_command(
                [
                    "ipconfig",
                    "/all",
                ],
                timeout=15,
            )
        )

        return NetworkResult(
            success=returncode == 0,
            title="IP Configuration",
            output=self._clean_output(
                stdout or stderr
            ),
            details=(
                "Εμφανίστηκε η πλήρης "
                "TCP/IP configuration."
                if returncode == 0
                else
                "Δεν ήταν δυνατή η ανάκτηση "
                "της IP configuration."
            ),
        )

    # ------------------------------------------------------------------
    # Network Adapters
    # ------------------------------------------------------------------

    def network_adapters(
        self,
    ) -> NetworkResult:

        powershell_script = (
            "Get-NetAdapter | "
            "Select-Object "
            "Name, InterfaceDescription, "
            "Status, LinkSpeed, MacAddress | "
            "Format-Table -AutoSize | "
            "Out-String -Width 240"
        )

        try:

            returncode, stdout, stderr = (
                self._run_command(
                    [
                        "powershell.exe",
                        "-NoProfile",
                        "-NonInteractive",
                        "-Command",
                        powershell_script,
                    ],
                    timeout=20,
                )
            )

            output = self._clean_output(
                stdout or stderr
            )

            if returncode == 0 and output:
                return NetworkResult(
                    success=True,
                    title="Network Adapters",
                    output=output,
                    details=(
                        "Εμφανίστηκαν οι διαθέσιμοι "
                        "network adapters."
                    ),
                )

        except (
            RuntimeError,
            TimeoutError,
        ):
            pass

        returncode, stdout, stderr = (
            self._run_command(
                [
                    "ipconfig",
                    "/all",
                ],
                timeout=15,
            )
        )

        return NetworkResult(
            success=returncode == 0,
            title="Network Adapters",
            output=self._clean_output(
                stdout or stderr
            ),
            details=(
                "Χρησιμοποιήθηκε το ipconfig "
                "ως fallback."
                if returncode == 0
                else
                "Δεν ήταν δυνατή η ανάκτηση "
                "των network adapters."
            ),
        )

    # ------------------------------------------------------------------
    # Internet Connectivity
    # ------------------------------------------------------------------

    def internet_connectivity(
        self,
    ) -> NetworkResult:

        target = "www.microsoft.com"

        lines = [
            "Internet Connectivity Test",
            "",
            f"Target: {target}",
            "",
        ]

        resolved_addresses: list[str] = []

        try:

            results = socket.getaddrinfo(
                target,
                443,
                socket.AF_UNSPEC,
                socket.SOCK_STREAM,
            )

            for result in results:

                address = result[4][0]

                if address not in resolved_addresses:
                    resolved_addresses.append(
                        address
                    )

        except socket.gaierror as exc:

            lines.extend(
                [
                    "1. DNS Resolution",
                    "   FAILED",
                    f"   {exc}",
                    "",
                    "2. TCP 443 Connectivity",
                    "   SKIPPED",
                ]
            )

            return NetworkResult(
                success=False,
                title="Internet Connectivity",
                output="\n".join(lines),
                details=(
                    "Απέτυχε το DNS resolution."
                ),
            )

        lines.extend(
            [
                "1. DNS Resolution",
                "   SUCCESS",
                (
                    "   Addresses: "
                    + ", ".join(
                        resolved_addresses
                    )
                ),
                "",
            ]
        )

        tcp_error = ""

        for address in resolved_addresses:

            try:

                with socket.create_connection(
                    (address, 443),
                    timeout=3,
                ):
                    lines.extend(
                        [
                            "2. TCP 443 Connectivity",
                            "   SUCCESS",
                            "",
                            "Overall Status",
                            "   INTERNET CONNECTION "
                            "AVAILABLE",
                        ]
                    )

                    return NetworkResult(
                        success=True,
                        title="Internet Connectivity",
                        output="\n".join(lines),
                        details=(
                            "DNS και TCP/443 "
                            "λειτουργούν κανονικά."
                        ),
                    )

            except OSError as exc:
                tcp_error = str(exc)

        lines.extend(
            [
                "2. TCP 443 Connectivity",
                "   FAILED",
            ]
        )

        if tcp_error:
            lines.append(
                f"   {tcp_error}"
            )

        lines.extend(
            [
                "",
                "Overall Status",
                "   INTERNET CONNECTION FAILED",
            ]
        )

        return NetworkResult(
            success=False,
            title="Internet Connectivity",
            output="\n".join(lines),
            details=(
                "Το DNS λειτουργεί αλλά απέτυχε "
                "η TCP σύνδεση στην 443."
            ),
        )

    # ------------------------------------------------------------------
    # Generic operation dispatcher
    # ------------------------------------------------------------------

    def execute(
        self,
        operation: str,
        *,
        host: str = "",
        port: int | str = 0,
        progress_callback: Callable[
            [str],
            None,
        ]
        | None = None,
    ) -> NetworkResult:

        if progress_callback:
            progress_callback(
                f"Starting {operation}..."
            )

        if operation == "ping":

            result = self.ping(
                host,
                line_callback=progress_callback,
            )

        elif operation == "traceroute":

            result = self.traceroute(
                host,
                line_callback=progress_callback,
            )

        elif operation == "dns_lookup":

            result = self.dns_lookup(host)

        elif operation == "port_test":

            result = self.port_test(
                host,
                port,
            )

        elif operation == "ip_configuration":

            result = self.ip_configuration()

        elif operation == "network_adapters":

            result = self.network_adapters()

        elif operation == "internet_connectivity":

            result = self.internet_connectivity()

        else:

            raise ValueError(
                f"Άγνωστη network operation: "
                f"{operation}"
            )

        if progress_callback:

            progress_callback(
                "Completed successfully."
                if result.success
                else
                "Operation completed with errors."
            )

        return result