import os
import requests
import time
import urllib3
import getpass

# Suppress insecure HTTPS warnings (UDR uses self-signed certs locally)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_recent_offline_clients():
    router_ip = "192.168.0.1"
    url = f"https://{router_ip}"
    
    print(f"=== UniFi Dream Router (UDR) Offline Client Monitor ===")
    print(f"Target: {url}")
    print("\nNote: It is highly recommended to use a Local Read-Only admin account.")
    print("If you haven't created one, go to your UDR OS Settings -> Admins & Users.")
    
    username = "homeassistant"
    password = "xSd3%1RlNh0D"
    
    session = requests.Session()
    
    # 1. Authenticate with UniFi OS
    login_data = {
        'username': username,
        'password': password
    }
    
    try:
        print("\nAuthenticating...")
        login_response = session.post(f"{url}/api/auth/login", json=login_data, verify=False, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"[-] Failed to connect to UDR: {e}")
        return
        
    if login_response.status_code != 200:
        print(f"[-] Authentication failed! HTTP {login_response.status_code}")
        return
    print("[+] Authentication successful.")

    # Set CSRF token for UniFi OS routing if provided
    csrf_token = login_response.headers.get('x-csrf-token')
    if csrf_token:
        session.headers.update({'X-CSRF-Token': csrf_token})
        
    # 2. Fetch all known clients from the Network proxy app
    site_id = "default"
    try:
        print("[*] Fetching historical device data...")
        # On UniFi OS, we proxy directly to the internal Network application
        users_req = session.get(f"{url}/proxy/network/api/s/{site_id}/stat/alluser", verify=False, timeout=15)
        
        if users_req.status_code != 200:
            print(f"[-] Failed to fetch clients list: HTTP {users_req.status_code}")
            return
            
        json_resp = users_req.json()
        data = json_resp.get('data', [])
        
    except Exception as e:
        print(f"[-] Error reading network data: {e}")
        return

    # 3. Filter for offline within the last 2 hours on Default VLAN
    print(f"[*] Analyzing {len(data)} known devices...")
    current_time = int(time.time())
    two_hours_ago = current_time - (2 * 60 * 60)
    
    offline_recent = []
    
    for client in data:
        # Check 'is_online' property; sometimes absent if deeply offline
        is_online = client.get('is_online', False)
        last_seen = client.get('last_seen', 0)
        
        # Check if the device's last IP starts with 192.168.0.
        last_ip = client.get('last_ip', '')
        is_target_ip = str(last_ip).startswith('192.168.0.')
        
        if not is_online and last_seen > two_hours_ago and is_target_ip:
            offline_recent.append(client)
            
    # 4. Format and Send to Slack
    SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL', 'https://hooks.slack.com/services/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')
    
    if not offline_recent:
        slack_msg = "✅ No devices have gone offline in the last 2 hours on the `192.168.0.*` subnet."
    else:
        # Sort by most recently seen
        offline_recent.sort(key=lambda x: x.get('last_seen', 0), reverse=True)
        
        slack_msg = f"⚠️ *OFFLINE DEVICES (LAST 2h) [192.168.0.*]*: {len(offline_recent)}\n\n"
        for c in offline_recent:
            hostname = c.get('name', c.get('hostname', 'Unknown Device'))
            mac = c.get('mac', 'Unknown MAC')
            ip = c.get('last_ip', 'Unknown IP')
            last_seen_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(c.get('last_seen', 0)))
            
            slack_msg += f"• *{hostname}*\n"
            slack_msg += f"  - MAC: `{mac}`\n"
            slack_msg += f"  - IP: `{ip}`\n"
            slack_msg += f"  - Last Seen: {last_seen_str}\n\n"

    print(f"[*] Sending results to Slack (#all-homelab) for {len(offline_recent)} offline device(s)...")
    
    if SLACK_WEBHOOK_URL == 'YOUR_SLACK_WEBHOOK_URL_HERE':
        print("[-] WARNING: Slack Webhook URL not set. Printing to console instead.")
        print("\n--- SLACK MESSAGE PREVIEW ---")
        print(slack_msg)
        print("-----------------------------\n")
    else:
        slack_payload = {
            "channel": "#all-homelab",
            "text": slack_msg
        }
        try:
            slack_res = requests.post(SLACK_WEBHOOK_URL, json=slack_payload, timeout=10)
            if slack_res.status_code == 200:
                print("[+] Successfully sent message to Slack.")
            else:
                print(f"[-] Failed to send to Slack: HTTP {slack_res.status_code} - {slack_res.text}")
        except Exception as e:
            print(f"[-] Error sending to Slack: {e}")

if __name__ == "__main__":
    get_recent_offline_clients()
