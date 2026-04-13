# How Cloudflare Tunnel Actually Works: Complete Deep Dive

## The Setup Phase (What Happens Before Any User Visits)

### 1. Tunnel Creation and Authentication

When you ran `cloudflared tunnel create mmkv-tunnel`, here's what happened:

**On your server:**
- Generated a tunnel with unique ID: `eebd63fa-4ece-4bde-84e6-89fc81a84e60`
- Created credentials file: `/etc/cloudflared/eebd63fa-4ece-4bde-84e6-89fc81a84e60.json`
- This JSON file contains cryptographic keys that authenticate your server to Cloudflare

**In Cloudflare's systems:**
- Registered the tunnel ID in their database
- Associated it with your Cloudflare account
- Created a unique tunnel hostname: `eebd63fa-4ece-4bde-84e6-89fc81a84e60.cfargotunnel.com`

### 2. DNS Configuration

When you ran `cloudflared tunnel route dns mmkv-tunnel www.mmkv-visualizer.com`:

**Created DNS records in Cloudflare:**
```
Type: CNAME
Name: www.mmkv-visualizer.com
Target: eebd63fa-4ece-4bde-84e6-89fc81a84e60.cfargotunnel.com
Proxied: Yes (orange cloud)
```

This tells Cloudflare's DNS: "When someone asks for www.mmkv-visualizer.com, tell them it's at this tunnel"

### 3. Tunnel Service Startup

When `sudo systemctl start cloudflared` runs:

**The cloudflared process:**
1. Reads `/etc/cloudflared/config.yml`
2. Loads the credentials from the JSON file
3. **Makes OUTBOUND connections to Cloudflare's edge servers**
4. Establishes **4 persistent HTTP/2 connections** for redundancy
5. Uses the credentials to authenticate: "Hey Cloudflare, I'm tunnel eebd63fa-4ece..."
6. Keeps these connections alive 24/7 with heartbeat packets

**Critical point:** These are **OUTBOUND** connections from your server to Cloudflare. Your firewall/router sees them as normal outgoing traffic (like browsing the web). No inbound ports needed!

**The 4 connections:**
- Connect to different Cloudflare edge locations
- Provide redundancy (if one drops, others handle traffic)
- Load balance requests across connections
- Each connection uses WebSocket protocol over TLS (encrypted)

---

## The Request Phase (Step-by-Step When a User Visits)

### Step ①: User Types URL

```
User types: https://www.mmkv-visualizer.com
```

The browser needs to find out where this domain points.

### Step ②: DNS Resolution

**Browser → DNS Resolver:**
```
Query: "What's the IP address for www.mmkv-visualizer.com?"
```

**DNS Resolver → Cloudflare's Authoritative DNS:**
```
Query: "What's www.mmkv-visualizer.com?"
```

**Cloudflare DNS responds:**
```
Type: CNAME
Value: eebd63fa-4ece-4bde-84e6-89fc81a84e60.cfargotunnel.com
```

**DNS Resolver → Cloudflare DNS (again):**
```
Query: "What's eebd63fa-4ece-4bde-84e6-89fc81a84e60.cfargotunnel.com?"
```

**Cloudflare DNS responds:**
```
Type: A (multiple IPs for load balancing)
Values: 104.21.95.89, 172.67.170.62
```

These are **Cloudflare's edge server IPs**, not your home IP!

**DNS Resolver → Browser:**
```
"www.mmkv-visualizer.com resolves to 104.21.95.89 and 172.67.170.62"
```

### Step ③: Browser Connects to Cloudflare

**Browser establishes HTTPS connection:**

```
TCP Handshake: Browser ←→ 104.21.95.89 (Cloudflare edge server)
TLS Handshake: Negotiate encryption
```

**Browser sends HTTP/2 request:**
```
GET / HTTP/2
Host: www.mmkv-visualizer.com
User-Agent: Mozilla/5.0...
Accept: text/html,application/xhtml+xml...
[many other headers]
```

**This arrives at Cloudflare's edge server** (the one geographically closest to the user - could be New York, London, Tokyo, etc.)

### Step ④: Cloudflare Routes the Request

**Cloudflare's edge server:**

1. **Terminates the HTTPS connection** (decrypts the TLS)
2. **Looks at the Host header:** `www.mmkv-visualizer.com`
3. **Checks its routing table:**
   ```
   www.mmkv-visualizer.com → CNAME → eebd63fa-4ece-4bde-84e6-89fc81a84e60.cfargotunnel.com
   ```
4. **Realizes:** "This is a tunnel! I need to route this to tunnel eebd63fa-4ece..."
5. **Checks tunnel status:**
   ```
   Tunnel ID: eebd63fa-4ece-4bde-84e6-89fc81a84e60
   Status: CONNECTED
   Active connections: 4
   Source IP: 98.x.x.x (your home IP - only Cloudflare knows this)
   ```

6. **Selects one of the 4 active tunnel connections** (load balancing)

### Step ⑤: Request Travels Through the Tunnel

**Cloudflare → Your Server (via existing tunnel connection):**

The request is sent through the **already-established WebSocket connection**:

```
[Encrypted WebSocket frame]
Method: GET
Path: /
Headers: {
  Host: www.mmkv-visualizer.com
  User-Agent: Mozilla/5.0...
  X-Forwarded-For: 203.0.113.45 (actual user's IP)
  CF-Ray: 8e7f3a2b9c1d0e5f-JFK
  [all original headers preserved]
}
```

This travels through:
1. The internet (encrypted)
2. Your ISP (encrypted - they can't see the contents)
3. Your router (sees it as outbound connection response)
4. Your server

**Your cloudflared process receives it**

### Step ⑥: cloudflared Processes the Request

**The cloudflared service:**

1. **Receives the request** from the WebSocket
2. **Reads its config** (`/etc/cloudflared/config.yml`):
   ```yaml
   ingress:
     - hostname: www.mmkv-visualizer.com
       service: http://localhost:80
   ```
3. **Matches the hostname:** "This request is for www.mmkv-visualizer.com"
4. **Looks at the service:** "Route to http://localhost:80"
5. **Creates a NEW local HTTP request:**

```
cloudflared makes HTTP request to 127.0.0.1:80

GET / HTTP/1.1
Host: www.mmkv-visualizer.com
User-Agent: Mozilla/5.0...
X-Forwarded-For: 203.0.113.45
[all the original headers]
```

This is a **local-only connection** on your server (localhost to localhost).

### Step ⑦: Nginx Receives the Request

**Nginx (listening on port 80):**

1. **Receives the connection** on `127.0.0.1:80`
2. **Reads the request headers**
3. **Checks its configuration** (`/etc/nginx/sites-enabled/svelte-app`):
   ```nginx
   server {
       listen 80;
       server_name localhost;  # Matches!
       root /var/www/svelte-app;
       index index.html;
       
       location / {
           try_files $uri $uri/ /index.html;
       }
   }
   ```
4. **Applies the location rules:**
   - Request: `GET /`
   - `try_files $uri` → Look for file `/`
   - Not found
   - `try_files $uri/` → Look for directory `/` with index.html
   - Not found
   - Fallback: `/index.html` → Look for `/var/www/svelte-app/index.html`
   - **Found!**

5. **Reads the file from disk:**
   ```
   open("/var/www/svelte-app/index.html")
   read() → loads entire file into memory
   ```

6. **Logs the request:**
   ```
   Writes to: /var/log/nginx/svelte-app.access.log
   Format: 127.0.0.1 - - [07/Feb/2026:21:30:45 +0000] "GET / HTTP/1.1" 200 1234
   ```

### Step ⑧: Nginx Sends Response to cloudflared

**Nginx → cloudflared (localhost connection):**

```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 1234
Last-Modified: Fri, 07 Feb 2026 20:15:30 GMT
ETag: "65c3d8a2-4d2"

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>MMKV Visualizer</title>
    <script type="module" crossorigin src="/assets/index-a1b2c3d4.js"></script>
    <link rel="stylesheet" href="/assets/index-e5f6g7h8.css">
  </head>
  <body>
    <div id="app"></div>
  </body>
</html>
```

**cloudflared receives this response**

### Step ⑨: Response Travels Back Through Tunnel

**cloudflared → Cloudflare (via WebSocket):**

The response is packaged and sent back through the **same tunnel connection**:

```
[Encrypted WebSocket frame]
Status: 200 OK
Headers: {
  Content-Type: text/html; charset=utf-8
  Content-Length: 1234
  [nginx's response headers]
}
Body: [HTML content]
```

This travels:
1. From your server
2. Through your router (outbound connection)
3. Through your ISP
4. Over the internet (encrypted)
5. To Cloudflare's edge server

### Step ⑩: Cloudflare Delivers to User

**Cloudflare's edge server:**

1. **Receives the response** from the tunnel
2. **Adds its own headers:**
   ```
   server: cloudflare
   cf-ray: 8e7f3a2b9c1d0e5f-JFK
   cf-cache-status: DYNAMIC
   ```
3. **Re-encrypts with TLS** (for the user's HTTPS connection)
4. **Sends to the browser:**

```
HTTP/2 200 OK
server: cloudflare
content-type: text/html; charset=utf-8
cf-ray: 8e7f3a2b9c1d0e5f-JFK

[Your HTML content]
```

**The browser receives and renders your Svelte app!**

---

## The Tunnel's Persistent Connection

### How the 4 Connections Work

**Connection establishment:**
```
Your server (cloudflared) → Cloudflare Edge
Protocol: HTTP/2 over TLS (port 443 outbound)
Upgrade to WebSocket: Yes
Keep-Alive: Infinite (with heartbeats)
```

**Each connection:**
- Uses a different Cloudflare edge server for redundancy
- Sends heartbeat packets every 30 seconds
- If connection drops, cloudflared automatically reconnects
- Cloudflare load-balances requests across all 4 connections

**Connection lifecycle:**
```
[Server boots]
  ↓
systemd starts cloudflared service
  ↓
cloudflared reads config
  ↓
Establishes 4 outbound WebSocket connections to Cloudflare
  ↓
Authenticates with tunnel credentials
  ↓
Cloudflare: "Tunnel eebd63fa... is now ACTIVE"
  ↓
[Connections stay open indefinitely]
  ↓
Every 30s: Send heartbeat, receive acknowledgment
  ↓
[Requests flow bidirectionally through these connections]
  ↓
If connection drops: Auto-reconnect within seconds
  ↓
[Runs until service stops or server reboots]
```

### Why No Inbound Ports Needed

**Traditional hosting:**
```
User → Your Router (port 443 forwarded) → Your Server
      ↑ Inbound connection initiated from outside
```

**With Cloudflare Tunnel:**
```
Your Server → Establishes outbound connection → Cloudflare
            ← Requests flow through existing connection ←
```

**The magic:**
- Your server makes the initial connection (outbound)
- Once established, data flows BOTH ways
- Your router sees it as a normal outbound connection (like browsing)
- Cloudflare uses this bidirectional channel to send requests
- Your server sends responses back through the same channel

**Firewall perspective:**
```
Outbound connection to cloudflare.com:443 → ALLOWED (normal HTTPS)
Data flowing back through that connection → ALLOWED (it's a response to your outbound connection)
```

No need to open inbound ports!

---

## Security Features

### 1. Your Home IP is Hidden

**What the world sees:**
```
www.mmkv-visualizer.com → 104.21.95.89 (Cloudflare IP)
```

**What Cloudflare knows:**
```
Tunnel eebd63fa... is connected from 98.x.x.x (your home IP)
```

**What attackers see:**
```
Only Cloudflare's IP
Cannot find your home IP
Cannot DDoS your home connection
```

### 2. Automatic SSL/TLS

**User ←→ Cloudflare:**
- Full TLS encryption
- Certificate: Issued by Cloudflare (free)
- Auto-renewed
- Perfect forward secrecy

**Cloudflare ←→ Your Server:**
- WebSocket over TLS (encrypted tunnel)
- Mutual authentication with tunnel credentials

**Your Server (cloudflared ←→ nginx):**
- Plain HTTP (localhost only, no network exposure)
- Safe because it never leaves your machine

### 3. DDoS Protection

**Attack scenario:**
```
Attacker floods www.mmkv-visualizer.com
  ↓
Traffic hits Cloudflare (not you!)
  ↓
Cloudflare's DDoS protection activates
  ↓
Malicious traffic blocked at Cloudflare
  ↓
Only legitimate requests reach your tunnel
  ↓
Your home internet stays safe
```

---

## What Happens If...

### Your IP Changes (Dynamic IP)

```
1. Your ISP assigns new IP: 98.5.6.7 (was 98.1.2.3)
2. Existing tunnel connections break
3. cloudflared detects disconnection
4. cloudflared reconnects from new IP: 98.5.6.7
5. Cloudflare updates internal routing
6. Tunnel continues working seamlessly
```

**Downtime:** Usually <5 seconds during reconnection

### Your Server Reboots

```
1. Server shuts down
2. Tunnel connections close
3. Cloudflare marks tunnel as DISCONNECTED
4. Requests to your site get 502 Bad Gateway
5. Server boots up
6. systemd starts cloudflared service (auto-start enabled)
7. Tunnel reconnects
8. Site is live again
```

**Downtime:** Boot time + ~10 seconds

### One Tunnel Connection Drops

```
1. Connection 1 of 4 drops (network hiccup)
2. cloudflared reconnects Connection 1
3. Meanwhile, Connections 2, 3, 4 handle all traffic
4. Zero downtime for users
```

---

## Summary: The Complete Flow

```
User visits www.mmkv-visualizer.com
    ↓
DNS: "That's a CNAME to tunnel eebd63fa..."
    ↓
DNS: "That tunnel resolves to Cloudflare IP 104.21.95.89"
    ↓
Browser connects to Cloudflare (HTTPS)
    ↓
Cloudflare: "Route this to tunnel eebd63fa..."
    ↓
Request sent through encrypted WebSocket tunnel
    ↓
Your server's cloudflared receives it
    ↓
cloudflared forwards to localhost:80 (nginx)
    ↓
Nginx serves /var/www/svelte-app/index.html
    ↓
Response sent back to cloudflared
    ↓
cloudflared sends through tunnel to Cloudflare
    ↓
Cloudflare delivers to user's browser
    ↓
User sees your Svelte app!
```

**Every request follows this path. Every time. In milliseconds.**

---

## Key Takeaways

1. **The tunnel is always on** - 4 persistent connections from your server to Cloudflare
2. **All connections are outbound** - Your server initiates, no inbound ports needed
3. **Your IP stays hidden** - Only Cloudflare knows your home IP
4. **Dynamic IP is fine** - Tunnel auto-reconnects when IP changes
5. **Free SSL** - Cloudflare handles all certificates automatically
6. **DDoS protection** - Attacks hit Cloudflare, not your home internet
7. **Production-ready** - Runs as systemd service, auto-starts on boot
8. **Zero configuration on router** - No port forwarding, no static IP

This is why Cloudflare Tunnel is the perfect solution for self-hosting from home!
