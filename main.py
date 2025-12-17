import paramiko
import argparse
import sys
import socket
import os


class WPMaintenanceTool:
    def __init__(self, host, port, user, password, wp_path):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.wp_path = wp_path
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.report_data = {}

        # Ensure local logs directory exists for reports and backups
        self.log_dir = "logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def connect(self):
        """Phase 1.3 & 4.1: Secure connection with robust error handling."""
        try:
            print(f"🔗 Connecting to {self.host}:{self.port} as '{self.user}'...")
            self.client.connect(
                self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                timeout=10,
            )
            print("✅ Connection Established.")
        except paramiko.AuthenticationException:
            print("❌ Auth Error: Invalid username or password.")
            sys.exit(1)
        except (socket.timeout, paramiko.SSHException) as e:
            print(f"❌ Connection Error: {e}")
            sys.exit(1)

    def run_command(self, command):
        """Helper to execute remote commands and capture output."""
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read().decode("utf-8").strip(), stderr.read().decode(
            "utf-8"
        ).strip()

    # --- SETUP & CLEANING ---

    def setup_wordpress(self, db_name, db_user, db_pass, db_host):
        """Phase 3.6: Bootstrap a fresh WP installation remotely."""
        print("🛠️ Checking installation status...")
        out, _ = self.run_command(f"ls {self.wp_path}/wp-config.php")

        if "wp-config.php" in out:
            print("✨ WordPress is already installed. Skipping setup.")
            return

        print("📦 Downloading and Installing WordPress...")
        commands = [
            f"wp core download --path={self.wp_path}",
            f"wp config create --dbname={db_name} --dbuser={db_user} --dbpass={db_pass} --dbhost={db_host} --path={self.wp_path}",
            f"wp core install --url='http://localhost:8080' --title='Dev Site' --admin_user='admin' --admin_password='password123' --admin_email='admin@example.com' --path={self.wp_path}",
            f"wp plugin install akismet --activate --path={self.wp_path}",
        ]

        for cmd in commands:
            self.run_command(cmd)
        print("✅ Setup complete!")

    def clean_environment(self):
        """Wipe files and reset database for a fresh start."""
        print("🚨 DANGER: Cleaning environment...")
        # Reset DB tables and remove all files in web root
        self.run_command(f"wp db reset --yes --path={self.wp_path}")
        self.run_command(f"rm -rf {self.wp_path}/* {self.wp_path}/.* 2>/dev/null")
        print("🧹 Environment is now empty.")

    # --- MAINTENANCE & DIAGNOSTICS ---

    def optimize_database(self):
        """Run database repair and optimization."""
        print("⚙️ Optimizing Database...")
        self.run_command(f"wp db optimize --path={self.wp_path}")

    def backup_database(self):
        """Phase 3.2: Create remote export and download to logs/ folder."""
        print("📦 Creating remote database backup...")
        remote_path = "/tmp/wp_backup.sql"
        local_path = os.path.join(self.log_dir, "local_wp_backup.sql")

        self.run_command(f"wp db export {remote_path} --path={self.wp_path}")

        print(f"📥 Downloading backup to {local_path}...")
        sftp = self.client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()

        self.run_command(f"rm {remote_path}")
        print(f"💾 Backup saved locally: {local_path}")

    def perform_updates(self):
        """Update core and plugins."""
        print("🚀 Updating WordPress Core & Plugins...")
        self.run_command(f"wp core update --path={self.wp_path}")
        self.run_command(f"wp core update-db --path={self.wp_path}")
        self.run_command(f"wp plugin update --all --path={self.wp_path}")

    def check_permissions(self):
        out, _ = self.run_command(f"find {self.wp_path}/wp-content/ -type d -perm 777")
        self.report_data["insecure_dirs"] = out.split("\n") if out else []

    def check_server_health(self):
        disk, _ = self.run_command("df -h / | awk 'NR==2 {print $5}'")
        mem, _ = self.run_command('free -m | awk \'NR==2 {print $3 "MB/" $2 "MB"}\'')
        self.report_data["disk_usage"] = disk or "Unknown"
        self.report_data["mem_usage"] = mem or "Unknown"

    def check_wp_status(self):
        core, _ = self.run_command(f"wp core check-update --path={self.wp_path}")
        plugins, _ = self.run_command(
            f"wp plugin list --status=active --field=name,version --path={self.wp_path}"
        )
        self.report_data["wp_update"] = (
            "⚠️ Update Available" if core else "✅ Up to date"
        )
        self.report_data["active_plugins"] = (
            plugins.split("\n") if plugins else ["None"]
        )

    def check_db_size(self):
        query = (
            "SELECT table_name, ROUND((data_length + index_length)/1024/1024, 2) "
            "FROM information_schema.TABLES WHERE table_schema='wordpress' "
            "ORDER BY 2 DESC LIMIT 3;"
        )
        out, _ = self.run_command(f'wp db query "{query}" --path={self.wp_path}')
        self.report_data["top_tables"] = out or "No data."

    def get_logs(self):
        """Fetch latest error logs from Apache."""
        log, _ = self.run_command("tail -n 10 /var/log/apache2/error.log")
        self.report_data["logs"] = log or "No recent errors."

    # --- REPORT GENERATION ---

    def generate_report(self):
        """Output results to terminal and logs/ folder."""
        report_path = os.path.join(self.log_dir, "wp_report.md")
        report = [
            f"# 🗺️ WP Maintenance Report: {self.host}",
            f"### 🖥️ Health: Disk {self.report_data['disk_usage']} | Mem {self.report_data['mem_usage']}",
            f"### 🛡️ Status: Core {self.report_data['wp_update']} | 777 Dirs: {len(self.report_data['insecure_dirs'])}",
            "### 📊 Top Database Tables\n```\n"
            + self.report_data["top_tables"]
            + "\n```",
            "### 🔌 Active Plugins\n"
            + "\n".join([f"* {p}" for p in self.report_data["active_plugins"]]),
            "### 📝 Recent Error Logs\n```\n" + self.report_data["logs"] + "\n```",
        ]

        full_report = "\n".join(report)
        with open(report_path, "w") as f:
            f.write(full_report)

        print("\n" + "=" * 30 + "\nFINAL REPORT\n" + "=" * 30)
        print(full_report)
        print(f"\n💾 Report saved to {report_path}")

    def close(self):
        self.client.close()
        print("🔌 Disconnected.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python 3.14 WP-Automator")
    parser.add_argument("--user", default="testuser")
    parser.add_argument("--passw", default="password")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=2222)
    parser.add_argument("--path", default="/var/www/html")
    parser.add_argument("--setup", action="store_true", help="Bootstrap WordPress")
    parser.add_argument("--clean", action="store_true", help="Wipe environment")
    parser.add_argument("--update", action="store_true", help="Backup and Update")
    parser.add_argument("--optimize", action="store_true", help="Optimize DB")

    args = parser.parse_args()

    tool = WPMaintenanceTool(args.host, args.port, args.user, args.passw, args.path)
    tool.connect()

    # Execution Logic
    if args.clean:
        tool.clean_environment()
    if args.setup:
        tool.setup_wordpress("wordpress", "wp_user", "wp_password", "db")
    if args.update:
        tool.backup_database()
        tool.perform_updates()
    if args.optimize:
        tool.optimize_database()

    # Always Run Diagnostics
    tool.check_permissions()
    tool.check_server_health()
    tool.check_wp_status()
    tool.check_db_size()
    tool.get_logs()
    tool.generate_report()

    tool.close()
    print("✨ Task Complete.")
