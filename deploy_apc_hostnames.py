#!/usr/bin/env python3
"""
APC PDU Hostname Deployer
--------------------------
Reads a CSV of IP/hostname pairs and sets the hostname on each PDU
via the APC CLI using SSH + expect.
No pip installs required — standard library only.
Requires: expect (dnf install expect -y)
Usage:
    python3 deploy_hostnames.py
CSV format (ip,hostname):
    192.168.1.1,hostname
    192.168.1.2,hostname
"""
import csv
import os
import subprocess
import time
from pathlib import Path

# ---------------------------------------------
# CONFIG - edit these before running
# ---------------------------------------------
CSV_FILE      = "pdu_hostname_ip.csv"  # CSV with ip,hostname columns
PDU_PASSWORD  = "changeme"             # Current password on all PDUs
EXPECT_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "set_hostname.exp")

# ---------------------------------------------
# FUNCTIONS
# ---------------------------------------------
def load_csv(filepath: str) -> list:
    """Load IP/hostname pairs from CSV."""
    pairs = []
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ip = row["ip"].strip()
            hostname = row["hostname"].strip()
            if ip and hostname:
                pairs.append((ip, hostname))
    return pairs


def set_hostname(ip: str, hostname: str) -> bool:
    """
    SSH into the PDU and set the hostname via the APC CLI.
    Returns True on success, False on failure.
    """
    try:
        result = subprocess.run(
            ["expect", EXPECT_SCRIPT, ip, PDU_PASSWORD, hostname],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            print(f"  [FAIL] {ip} ({hostname}) — expect exited with code {result.returncode}")
            print(f"         {result.stderr.strip()}")
            return False
        if "E000" not in result.stdout:
            print(f"  [FAIL] {ip} ({hostname}) — unexpected response")
            print(f"         {result.stdout.strip()}")
            return False
        print(f"  [OK]   {ip} → {hostname}")
        return True
    except subprocess.TimeoutExpired:
        print(f"  [FAIL] {ip} ({hostname}) — timed out")
        return False
    except Exception as e:
        print(f"  [FAIL] {ip} ({hostname}) — {e}")
        return False


# ---------------------------------------------
# MAIN
# ---------------------------------------------
def main():
    csv_path = Path(CSV_FILE)
    if not csv_path.exists():
        print(f"ERROR: CSV file not found: {CSV_FILE}")
        return

    pdus = load_csv(CSV_FILE)
    print(f"Setting hostnames on {len(pdus)} PDU(s)...\n")

    success = 0
    failed  = 0
    failed_list = []

    for ip, hostname in pdus:
        if set_hostname(ip, hostname):
            success += 1
        else:
            failed += 1
            failed_list.append((ip, hostname))

    print(f"\nDone. {success} succeeded, {failed} failed.")
    if failed_list:
        print("\nFailed PDUs:")
        for ip, hostname in failed_list:
            print(f"  {ip} ({hostname})")


if __name__ == "__main__":
    main()
