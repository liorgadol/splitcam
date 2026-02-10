# Camera Viewer - Split Screen

WebRTC-based live camera viewer with split-screen support using go2rtc.

## 🚀 Quick Start

### Step 1: Configure Environment Variables

Create/edit `.env` file with your camera credentials:

```env
# Camera credentials - shared across all cameras
CAMERA_USER=your_username
CAMERA_PASSWORD=your_password

# Camera IP addresses
CAMERA1_IP=192.168.1.53
CAMERA2_IP=192.168.1.54
```

Camera names can be changed in `index.html`:
- Camera 1: Living Room
- Camera 2: Upstairs

### Step 2: Start Services

```bash
docker compose up -d
```

This starts:
- go2rtc (WebRTC gateway on port 1984)
- nginx web server (camera viewer on port 8080)

### Step 3: View Cameras

Open your browser and navigate to:

**http://localhost:8080**

Both cameras will automatically connect and display side-by-side!

## 🎯 Features

- ✅ Split-screen view (side-by-side cameras)
- ✅ Auto-connect on page load
- ✅ Low-latency WebRTC streaming
- ✅ Shared credentials via environment variables
- ✅ Individual camera status indicators
- ✅ Full browser controls (play, pause, volume, fullscreen)
- ✅ Responsive design (stacks vertically on mobile)
- ✅ Clean, modern UI

## 📡 Adding More Cameras

1. Add new IP to `.env`:
   ```env
   CAMERA3_IP=192.168.1.55
   ```

2. Add to `docker-compose.yml` environment section:
   ```yaml
   - CAMERA3_IP=${CAMERA3_IP}
   ```

3. Add stream to `go2rtc.yaml`:
   ```yaml
   streams:
     camera3:
       - rtsp://${CAMERA_USER}:${CAMERA_PASSWORD}@${CAMERA3_IP}:554/stream1
   ```

4. Update `index.html` (add camera to array and HTML grid)

5. Restart: `docker compose up -d`

## 🔧 Troubleshooting

### Cameras not connecting

1. **Check if services are running:**
   ```bash
   docker ps
   ```
   You should see `go2rtc` and `camera-web` containers.

2. **View go2rtc logs:**
   ```bash
   docker logs go2rtc
   ```

3. **Access go2rtc web UI:**
   Open http://localhost:1984 to check stream status and test manually.

4. **Verify environment variables:**
   ```bash
   cat .env
   ```

5. **Check RTSP connection:**
   Ensure cameras are accessible at the IPs in `.env` file.

### "Error: Failed to fetch" or CORS errors

The setup includes CORS configuration (`origin: "*"` in go2rtc.yaml), so this should not occur. If it does:
- Restart services: `docker compose restart`
- Check browser console for detailed errors

### Video connects but shows black screen

- Try alternative RTSP paths in `go2rtc.yaml`:
  ```yaml
  - rtsp://${CAMERA_USER}:${CAMERA_PASSWORD}@${CAMERA1_IP}/stream1  # without port
  - rtsp://${CAMERA_USER}:${CAMERA_PASSWORD}@${CAMERA1_IP}:554/stream2  # sub-stream
  ```

### Port conflicts

If ports 1984 or 8080 are already in use, edit `docker-compose.yml`:
```yaml
ports:
  - "8081:80"  # Change external port
```

## 📱 Access from Other Devices

## 📱 Access from Other Devices

1. Find your computer's IP address:
   ```bash
   ipconfig getifaddr en0  # macOS WiFi
   # or
   ip addr show  # Linux
   ```

2. Access from other device on same network:
   ```
   http://YOUR_COMPUTER_IP:8080
   ```

Note: Both go2rtc (1984) and WebRTC (8555) ports need to be accessible. The setup already exposes these ports.

## 📋 Common RTSP URLs for Tapo/TP-Link Cameras

Try these alternatives if `stream1` doesn't work:
- `rtsp://user:pass@IP:554/stream1` (Main stream - high quality)
- `rtsp://user:pass@IP:554/stream2` (Sub stream - lower quality)  
- `rtsp://user:pass@IP/stream1` (Without port)

## 🛠️ Configuration Files

### docker-compose.yml
Defines two services:
- `go2rtc`: WebRTC gateway (ports 1984, 8554, 8555)
- `web`: Nginx serving index.html (port 8080)

### go2rtc.yaml
Stream definitions with environment variable substitution:
```yaml
streams:
  camera1:
    - rtsp://${CAMERA_USER}:${CAMERA_PASSWORD}@${CAMERA1_IP}:554/stream1
```

### .env
Credentials and IP addresses (not tracked in git)

### index.html
Split-screen viewer with auto-connect functionality

## 🛡️ Security Notes

- `.env` file contains sensitive credentials - never commit to git
- Consider using a reverse proxy (nginx/caddy) for remote access
- For internet access, use VPN or proper authentication layer

## 📚 Resources

- [go2rtc GitHub](https://github.com/AlexxIT/go2rtc)
- [go2rtc Documentation](https://github.com/AlexxIT/go2rtc#configuration)
- [TP-Link Camera RTSP Guide](https://www.tp-link.com/us/support/faq/2680/)
- [WebRTC Documentation](https://webrtc.org/)

## 🎮 Useful Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker logs go2rtc
docker logs camera-web

# Restart after config changes
docker compose restart

# View running containers
docker ps
```

## 🐛 Still Having Issues?

1. Check browser console (F12 → Console tab) for JavaScript errors
2. Check go2rtc logs: `docker logs go2rtc`
3. Test streams directly at http://localhost:1984
4. Verify camera credentials and IP addresses in `.env`
