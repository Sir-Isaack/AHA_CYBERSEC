import argparse
import subprocess
import sys
import os
import shutil
import urllib.request
import urllib.parse
import json

# ============================================================
# SCRIPT WRITE-UP
# ============================================================
# This script performs subdomain enumeration and live-host
# detection for a domain selected by the user.
#
# Subfinder discovers subdomains and saves them to the output
# file selected by the user.
#
# Httpx checks the discovered subdomains and identifies live
# hosts. The live hosts are saved to a "_live.txt" file.
#
# The script also supports optional real-time notifications
# through Telegram, Discord, and Slack.
#
# Telegram uses a bot token and username or chat ID.
# Discord uses a bot token and channel ID.
# Slack uses a webhook URL.
#
# If N/A or a blank value is provided for a notification
# channel, that channel is skipped silently.
#
# Every live host is displayed as it is discovered.
# Configured notification channels receive each live host.
#
# Httpx is located automatically using shutil.which(), so
# its installation path does not need to be hardcoded.
#
# The script handles missing tools, failed commands, network
# errors, and file errors gracefully.
# ============================================================


# Send notification to Telegram
def send_telegram(message, bot_token, chat_id):
    if not bot_token or not chat_id:
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": message
    }).encode()

    try:
        urllib.request.urlopen(url, data=data, timeout=10)
        print("[+] Telegram notification sent.")
    except Exception as error:
        print(f"[ERROR] Telegram notification failed: {error}")


# Send notification to Discord
def send_discord(message, bot_token, channel_id):
    if not bot_token or not channel_id:
        return

    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"

    data = json.dumps({
        "content": message
    }).encode()

    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bot {bot_token}"
        }
    )

    try:
        urllib.request.urlopen(request, timeout=10)
        print("[+] Discord notification sent.")
    except Exception as error:
        print(f"[ERROR] Discord notification failed: {error}")


# Send notification to Slack
def send_slack(message, webhook_url):
    if not webhook_url:
        return

    data = json.dumps({
        "text": message
    }).encode()

    request = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    try:
        urllib.request.urlopen(request, timeout=10)
        print("[+] Slack notification sent.")
    except Exception as error:
        print(f"[ERROR] Slack notification failed: {error}")


# Send notification to all configured channels
def send_notifications(
    message,
    telegram_token,
    telegram_chat_id,
    discord_token,
    discord_channel_id,
    slack_webhook
):
    send_telegram(
        message,
        telegram_token,
        telegram_chat_id
    )

    send_discord(
        message,
        discord_token,
        discord_channel_id
    )

    send_slack(
        message,
        slack_webhook
    )


# Create command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--domain", help="Domain to search")
parser.add_argument("-o", "--output", help="Preferred output file")
args = parser.parse_args()


# Ask for domain if not provided
if args.domain:
    domain = args.domain
else:
    domain = input("Enter the domain to search: ").strip()


# Ask for output file if not provided
if args.output:
    output = args.output
else:
    output = input("Enter the preferred output file name: ").strip()


# Ask for Telegram details
print("\n--- Telegram Notification ---")

telegram_token = input(
    "Enter Telegram bot token (N/A to skip): "
).strip()

telegram_chat_id = ""

if telegram_token and telegram_token.lower() != "n/a":
    telegram_chat_id = input(
        "Enter Telegram username or chat ID (N/A to skip): "
    ).strip()

    if telegram_chat_id.lower() == "n/a":
        telegram_token = ""
        telegram_chat_id = ""


# Ask for Discord details
print("\n--- Discord Notification ---")

discord_token = input(
    "Enter Discord bot token (N/A to skip): "
).strip()

discord_channel_id = ""

if discord_token and discord_token.lower() != "n/a":
    discord_channel_id = input(
        "Enter Discord channel ID (N/A to skip): "
    ).strip()

    if discord_channel_id.lower() == "n/a":
        discord_token = ""
        discord_channel_id = ""


# Ask for Slack details
print("\n--- Slack Notification ---")

slack_webhook = input(
    "Enter Slack webhook URL (N/A to skip): "
).strip()

if slack_webhook.lower() == "n/a":
    slack_webhook = ""


# Create output filenames
subdomain_file = output
live_file = os.path.splitext(output)[0] + "_live.txt"


# Find httpx automatically
httpx_path = shutil.which("httpx")

if not httpx_path:
    print("[ERROR] httpx is not installed or not in PATH.")
    sys.exit(1)


# Run subfinder
print(f"\n[+] Enumerating subdomains for {domain}...")

try:
    subprocess.run(
        ["subfinder", "-d", domain, "-o", subdomain_file],
        check=True
    )

    print(f"[+] Results saved to {subdomain_file}")

except FileNotFoundError:
    print("[ERROR] subfinder is not installed or not in PATH.")
    sys.exit(1)

except subprocess.CalledProcessError:
    print("[ERROR] subfinder failed.")
    sys.exit(1)


# Run httpx
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
    print("[ERROR] httpx is not installed or not in PATH.")
    sys.exit(1)

except subprocess.CalledProcessError:
    print("[ERROR] httpx failed.")
    sys.exit(1)


# Read live hosts
try:
    with open(live_file, "r") as file:
        live_hosts = file.readlines()

    if live_hosts:
        print(f"[+] Found {len(live_hosts)} live host(s).\n")

        # Process each live host
        for host in live_hosts:
            host = host.strip()

            if not host:
                continue

            # Display live host
            print(f"[LIVE] {host}")

            # Create notification message
            message = (
                f"Live host found for {domain}:\n"
                f"{host}"
            )

            # Send notification
            send_notifications(
                message,
                telegram_token,
                telegram_chat_id,
                discord_token,
                discord_channel_id,
                slack_webhook
            )

    else:
        print("[-] No live hosts found.")

except OSError as error:
    print(f"[ERROR] Could not read output file: {error}")
    sys.exit(1)


# Display final success message
print("\n========================================")
print("        PROCESS WAS SUCCESSFUL")
print("========================================")
print(f"All subdomains for {domain} saved to: {subdomain_file}")
print(f"Live subdomains saved to: {live_file}")
print("========================================")
