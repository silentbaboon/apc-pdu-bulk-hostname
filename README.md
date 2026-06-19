# APC PDU Bulk Hostname Deployer

Bulk hostname deployment tool for APC NetShelter Rack PDUs — automates SSH login, first-login password handling, and hostname assignment via the APC CLI using expect.

---

## Overview

This tool reads a CSV of IP/hostname pairs and sets the hostname on each PDU via the APC CLI. It handles the forced first-login password change that APC PDUs require out of the box, making it suitable for provisioning large numbers of devices with no manual interaction.

---

## Requirements

- Python 3.x (standard library only — no pip installs needed)
- `expect` system package

Install expect on RHEL/CentOS/Fedora:
```bash
dnf install expect -y
```

---

## Files

| File | Description |
|---|---|
| `deploy_hostnames.py` | Main script — reads CSV and sets hostname on each PDU |
| `set_hostname.exp` | Expect script — handles SSH login and APC CLI commands |
| `pdu_hostname_ip.csv` | Example CSV input file |

---

## Setup

1. Clone the repo:
    ```bash
    git clone https://github.com/silentbaboon/apc-pdu-bulk-hostname.git
    cd apc-pdu-bulk-hostname
    ```

2. Edit `pdu_hostname_ip.csv`:
    ```
    ip,hostname
    10.0.0.1,hostname
    10.0.0.2,hostname
    ```

3. Edit the CONFIG section at the top of `deploy_hostnames.py`:
    ```python
    CSV_FILE     = "pdu_hostname_ip.csv"
    PDU_PASSWORD = "changeme"   # Current password on all PDUs
    ```

---

## Usage

```bash
python3 deploy_hostnames.py
```

Example output:
```
Setting hostnames on 4 PDU(s)...

  [OK]   10.0.0.1 → hostname
  [OK]   10.0.0.2 → hostname
  [FAIL] 10.0.0.3 (hostname) — timed out
  [OK]   10.0.0.4 → hostname

Done. 3 succeeded, 1 failed.

Failed PDUs:
  10.0.0.3 (hostname)
```

---

## How It Works

1. `deploy_hostnames.py` reads the CSV and iterates over each IP/hostname pair.
2. For each PDU, it invokes `set_hostname.exp` via subprocess, passing the IP, password, and hostname as arguments.
3. The expect script SSHs into the PDU using legacy-compatible SSH ciphers and key algorithms required by APC NMC firmware.
4. Once logged in, the hostname is set with `system -n "<hostname>"` via the APC CLI, then the session exits cleanly.
5. `deploy_hostnames.py` checks the output for `E000` (APC's success code) to confirm the command was accepted.
6. Results are printed to stdout with `[OK]` or `[FAIL]` status, and a summary of any failures is shown at the end.

> **Note:** This script assumes PDUs are already provisioned with a known password. If you need to handle first-login forced password changes, see the companion project `apc-pdu-bulk_config`.

---

## CSV Format

The input CSV must have `ip` and `hostname` columns. Lines beginning with `#` are ignored.

```
ip,hostname
10.0.0.1,hostname
10.0.0.2,hostname
```

> **Note:** `pdu_hostname_ip.csv` is listed in `.gitignore` — never commit your real IP/hostname list to the repository.

---

## Security Notes

- **Never commit real passwords** to the repository. Keep credentials out of all tracked files.
- The CSV containing real IPs and hostnames is gitignored by default.
- SSH host key checking is disabled (`StrictHostKeyChecking=no`) for convenience during bulk provisioning — use only on trusted networks.

---

## License

MIT — see [LICENSE](LICENSE) for details.
