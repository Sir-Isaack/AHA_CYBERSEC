import argparse
import subprocess
import sys
import os
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--domain", help="Domain to search")
parser.add_argument("-o", "--output", help="Preferred output file")
args = parser.parse_args()

if args.domain:
    domain = args.domain
else:
    domain = input("Enter the domain to search: ").strip()

if args.output:
    output = args.output
else:
    output = input("Enter the preferref output file name: ").strip()

subdomain_file = output
live_file = os.path.splitext(output)[0] + "_live.txt"

httpx_path = shutil.which("httpx")

if not httpx_path:
    print("[ERROR] httpx is not installed or not in PATH.")
    sys.exit(1)

print(f"[+] Enumarating subdomains for {domain}...")

try:
    subprocess.run(
        ["subfinder", "-d", domain, "-o", subdomain_file],
        check=True
    )
    print(f"[+] Results saved to {subdomain_file}")
except FileNotFoundError:
    print("[ERROR] subfinder is not installed.")
    sys.exit(1)
except subprocess.CalledProcessError:
    print("[ERROR] subfinder failed.")
    sys.exit(1)

print("[+] Checking for live hosts...")

try:
    with open(subdomain_file, "r") as infile, open(live_file, "w") as outfile:
        subprocess.run(
            [httpx_path, "-silent"],
            stdin=infile,
            stdout=outfile,
            check=True
        )

    print(f"[+] Live hosts saved to {live_file}")
except FileNotFoundError:
    print("[ERROR] httpx is not installed.")
    sys.exit(1)

try:
    with open(live_file, "r") as file:
        live_hosts = file.readlines()

    if live_hosts:
        print(f"[+] Found {len(live_hosts)} live host(s).")
        for host in live_hosts:
            print(f"[LIVE] {host.strip()}")
    else:
        print("[-] No live hosts found.")

except OSError as error:
    print(f"[ERROR] Could not read output file: {error}")
    sys.exit(1)

