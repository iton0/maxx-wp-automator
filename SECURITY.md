# Security Policy

## 🛡️ Supported Versions

We currently provide security updates for the following versions:

| Version | Supported |
| --- | --- |
| 1.0.x | ✅ Yes |
| < 1.0.0 | ❌ No |

## 🔒 Reporting a Vulnerability

The security of this automation tool is a top priority. If you discover a security vulnerability (such as an issue with credential handling or SFTP transfer), please **do not open a public GitHub issue.** Instead, please report it via the following process:

1. **Email:** Send a report to `iton442@gmail.com`.
2. **Details:** Include a description of the vulnerability, a proof-of-concept (if possible), and the impact.
3. **Response:** You will receive an acknowledgment of your report within 48 hours.

## 🔑 Best Practices for Users

To keep your remote environments secure while using this tool:

* **Use SSH Keys:** While this tool supports password authentication, we strongly recommend configuring your Docker/Remote host for SSH Key-based auth.
* **Log Management:** Remember that the `logs/` folder contains sensitive database backups. Ensure this folder remains in your `.gitignore`.
* **Environment Variables:** Avoid hardcoding credentials in your shell history; use a `.env` file or secret manager where possible.
