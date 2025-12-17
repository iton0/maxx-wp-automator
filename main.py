import argparse
import logging
import os
import shlex
import socket
import sys
from datetime import datetime
from typing import NamedTuple, Protocol, cast

import paramiko


# Protocol for type-safe arguments
class ToolArguments(Protocol):
    user: str
    passw: str
    host: str
    port: int
    path: str
    setup: bool
    clean: bool
    update: bool
    optimize: bool


class CommandResult(NamedTuple):
    stdout: str
    stderr: str
    exit_status: int


class WPMaintenanceError(Exception):
    """Custom exception for WP Maintenance Tool errors."""

    pass


class WPMaintenanceTool:
    def __init__(
        self, host: str, port: int, user: str, password: str, wp_path: str
    ) -> None:
        self.host: str = host
        self.port: int = port
        self.user: str = user
        self.password: str = password
        self.wp_path: str = wp_path.rstrip("/")

        self.client: paramiko.SSHClient = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.report_data: dict[str, str | list[str]] = {}
        self.log_dir: str = "logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # Setup Logging
        log_file = os.path.join(
            self.log_dir, f"maintenance_{datetime.now().strftime('%Y%m%d')}.log"
        )
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
        )
        self.logger: logging.Logger = logging.getLogger(__name__)

    def connect(self) -> None:
        """Establishes SSH connection with safety checks."""
        try:
            self.logger.info(f"Connecting to {self.host}:{self.port}...")
            self.client.connect(
                self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                timeout=15,
            )

            res = self.run_command("which wp")
            if res.exit_status != 0:
                raise WPMaintenanceError("WP-CLI not found for this user.")

            self.logger.info("Connection established successfully.")
        except Exception as e:
            raise WPMaintenanceError(f"Connection failed: {e}")

    def run_command(self, command: str, timeout: int = 30) -> CommandResult:
        """Executes a command with a specific timeout."""
        try:
            _, stdout, stderr = self.client.exec_command(command, timeout=timeout)
            exit_status = stdout.channel.recv_exit_status()
            return CommandResult(
                stdout.read().decode("utf-8").strip(),
                stderr.read().decode("utf-8").strip(),
                exit_status,
            )
        except socket.timeout:
            self.logger.error(f"Command timed out: {command}")
            return CommandResult("", "Command timed out", 124)

    def _wp_cli(self, wp_cmd: str) -> CommandResult:
        """Executes WP-CLI commands securely."""
        full_cmd = f"wp {wp_cmd} --path={shlex.quote(self.wp_path)}"
        return self.run_command(full_cmd)

    def setup_wordpress(
        self, db_name: str, db_user: str, db_pass: str, db_host: str
    ) -> None:
        self.logger.info("Checking WordPress installation...")
        check = self.run_command(f"ls {shlex.quote(self.wp_path)}/wp-config.php")
        if check.exit_status == 0:
            self.logger.warning("WordPress already configured. Skipping setup.")
            return

        _ = self.run_command(f"mkdir -p {shlex.quote(self.wp_path)}")

        site_url = f"http://{self.host}:8080"

        commands = [
            "core download",
            f"config create --dbname={shlex.quote(db_name)} --dbuser={shlex.quote(db_user)} --dbpass={shlex.quote(db_pass)} --dbhost={shlex.quote(db_host)}",
            f"core install --url={shlex.quote(site_url)} --title='Dev Site' --admin_user='admin' --admin_password='password123' --admin_email='admin@example.com'",
        ]

        for cmd in commands:
            self.logger.info(f"Running: wp {cmd}")
            res = self._wp_cli(cmd)
            if res.exit_status != 0:
                self.logger.error(f"Setup step failed: {res.stderr}")
                break

    def clean_environment(self) -> None:
        self.logger.info("Cleaning remote environment...")
        _ = self._wp_cli("db reset --yes")
        if len(self.wp_path) > 5:
            _ = self.run_command(f"rm -rf {shlex.quote(self.wp_path)}/*")
            self.logger.info(f"Directory {self.wp_path} cleared.")

    def optimize_database(self) -> None:
        self.logger.info("Optimizing database...")
        res = self._wp_cli("db optimize")
        if res.exit_status != 0:
            self.logger.error(f"Optimize failed: {res.stderr}")

    def backup_database(self) -> None:
        remote_path = f"/tmp/wp_bak_{os.urandom(4).hex()}.sql"
        local_path = os.path.join(self.log_dir, "local_wp_backup.sql")

        try:
            self.logger.info("Exporting database...")
            export_res = self._wp_cli(f"db export {shlex.quote(remote_path)}")
            if export_res.exit_status == 0:
                sftp = self.client.open_sftp()
                sftp.get(remote_path, local_path)
                sftp.close()
                self.logger.info(f"Backup saved to: {local_path}")
            else:
                self.logger.error(f"Export failed: {export_res.stderr}")
        finally:
            _ = self.run_command(f"rm {shlex.quote(remote_path)}")

    def perform_updates(self) -> None:
        self.logger.info("Updating core and plugins...")
        _ = self._wp_cli("core update")
        _ = self._wp_cli("plugin update --all")

    def check_permissions(self) -> None:
        res = self.run_command(
            f"find {shlex.quote(self.wp_path)}/wp-content/ -type d -perm 777"
        )
        self.report_data["insecure_dirs"] = res.stdout.split("\n") if res.stdout else []

    def check_server_health(self) -> None:
        disk = self.run_command("df -h / --output=pcent | tail -1")
        mem = self.run_command('free -m | awk \'/Mem:/ {print $3 "MB/" $2 "MB"}\'')
        self.report_data["disk_usage"] = (
            disk.stdout if disk.exit_status == 0 else "Unknown"
        )
        self.report_data["mem_usage"] = (
            mem.stdout if mem.exit_status == 0 else "Unknown"
        )

    def check_wp_status(self) -> None:
        core = self._wp_cli("core check-update")
        plugins = self._wp_cli("plugin list --status=active --field=name,version")

        if "Success: WordPress is at the latest version" in core.stdout:
            status = "✅ Up to date"
        else:
            status = "⚠️ Update Available"

        self.report_data["wp_update"] = status
        self.report_data["active_plugins"] = (
            plugins.stdout.split("\n") if plugins.stdout else ["None"]
        )

    def generate_report(self) -> None:
        report_path = os.path.join(self.log_dir, "wp_report.md")
        insecure = self.report_data.get("insecure_dirs", [])
        plugin_list = "\n".join(
            [f"* {p}" for p in (self.report_data.get("active_plugins") or [])]
        )

        report_content = (
            f"# 🗺️ WP Maintenance Report: {self.host}\n\n"
            f"### 🖥️ Health: Disk {self.report_data.get('disk_usage')} | Mem {self.report_data.get('mem_usage')}\n"
            f"### 🛡️ Status: Core {self.report_data.get('wp_update')} | 777 Dirs: {len(insecure)}\n\n"
            f"### 🔌 Active Plugins\n{plugin_list}\n"
        )

        with open(report_path, "w") as f:
            _ = f.write(report_content)
        self.logger.info(f"Report generated: {report_path}")

    def close(self) -> None:
        self.client.close()
        self.logger.info("SSH connection closed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WP-Automator")
    _ = parser.add_argument("--user", required=True)
    _ = parser.add_argument("--passw", required=True)
    _ = parser.add_argument("--host", default="127.0.0.1")
    _ = parser.add_argument("--port", type=int, default=2222)
    _ = parser.add_argument("--path", default="/var/www/html")
    _ = parser.add_argument("--setup", action="store_true")
    _ = parser.add_argument("--clean", action="store_true")
    _ = parser.add_argument("--update", action="store_true")
    _ = parser.add_argument("--optimize", action="store_true")

    args = cast(ToolArguments, cast(object, parser.parse_args()))

    tool = WPMaintenanceTool(args.host, args.port, args.user, args.passw, args.path)

    try:
        tool.connect()

        if args.clean:
            tool.clean_environment()
        if args.setup:
            tool.setup_wordpress("wordpress", "wp_user", "wp_password", "db")
        if args.update:
            tool.backup_database()
            tool.perform_updates()
        if args.optimize:
            tool.optimize_database()

        tool.check_permissions()
        tool.check_server_health()
        tool.check_wp_status()
        tool.generate_report()

    except WPMaintenanceError as e:
        logging.critical(f"Execution failed: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        tool.close()
