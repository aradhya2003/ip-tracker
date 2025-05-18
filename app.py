from flask import Flask, request, jsonify
import ipinfo
import os
from user_agents import parse

app = Flask(__name__)

# Initialize IPinfo handler
access_token = os.getenv('IPINFO_TOKEN', '')  # Get from https://ipinfo.io/signup
handler = ipinfo.getHandler(access_token)

@app.route('/')
def track_visitor():
    # Get client IP (handles proxies)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in ip:  # Handle multiple IPs
        ip = ip.split(',')[0].strip()

    # Get IP details
    try:
        details = handler.getDetails(ip)
    except:
        details = None

    # Parse user agent
    ua = parse(request.headers.get('User-Agent', ''))
    
    # Prepare response
    visitor_info = {
        "ip": ip,
        "location": {
            "city": getattr(details, 'city', 'Unknown'),
            "region": getattr(details, 'region', 'Unknown'),
            "country": getattr(details, 'country_name', 'Unknown'),
            "coordinates": getattr(details, 'loc', 'Unknown'),
            "postal": getattr(details, 'postal', 'Unknown'),
            "timezone": getattr(details, 'timezone', 'Unknown')
        },
        "network": {
            "isp": getattr(details, 'org', 'Unknown'),
            "asn": getattr(details, 'asn', {}).get('asn', 'Unknown')
        },
        "browser": {
            "name": ua.browser.family,
            "version": ua.browser.version_string
        },
        "os": {
            "name": ua.os.family,
            "version": ua.os.version_string
        },
        "device": "Mobile" if ua.is_mobile else "Desktop" if ua.is_pc else "Tablet"
    }

    # Print to console (for debugging)
    print("\n=== Visitor Information ===")
    for category, data in visitor_info.items():
        print(f"{category.upper()}:")
        if isinstance(data, dict):
            for k, v in data.items():
                print(f"  {k}: {v}")
        else:
            print(f"  {data}")

    return jsonify(visitor_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)