# Camera Viewer - Split Screen with DVR

WebRTC-based live camera viewer with split-screen support, DVR recording, and web-based control panel using go2rtc.

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
- nginx web server (camera viewer on port 8082)
- FFmpeg recorders (DVR recording for each camera)
- API service (recording management backend)
- Cleanup service (automatic old recording deletion)

### Step 3: View Cameras

Open your browser and navigate to:

**http://localhost:8082**

Both cameras will automatically connect and display side-by-side!

## 🎯 Features

### Live Viewing
- ✅ Split-screen view (side-by-side cameras)
- ✅ Auto-connect on page load
- ✅ Low-latency WebRTC streaming
- ✅ Individual camera status indicators
- ✅ Full browser controls (play, pause, volume, fullscreen)
- ✅ Responsive design (stacks vertically on mobile)

### DVR Recording
- ✅ Automatic continuous recording for all cameras
- ✅ 10-minute MP4 segments (configurable)
- ✅ 24-hour retention (configurable)
- ✅ H.264 video with AAC audio
- ✅ Automatic cleanup of old recordings

### Control Panel
- ✅ Web-based control panel for all settings
- ✅ Recording viewer with playback
- ✅ Download recordings
- ✅ Delete individual or all recordings
- ✅ Adjust segment duration (1-60 minutes)
- ✅ Configure retention period (1-168 hours)
- ✅ Video quality settings
- ✅ Audio bitrate configuration
- ✅ Storage usage statistics
- ✅ Manual cleanup trigger

## 📹 Using the Control Panel

### Live View Tab
- View live streams from both cameras
- Real-time connection status
- Connect/disconnect controls

### Recordings Tab
- Browse all recorded files organized by camera
- View recording statistics (count, total size)
- Play recordings in-browser
- Download recordings to your computer
- Delete individual recordings
- See file sizes and timestamps

### Settings Tab
**Recording Settings:**
- Segment Duration: How long each recording file should be (1-60 minutes)
- Retention Period: How long to keep recordings before auto-deletion (1-168 hours)
- Video Quality: Source quality (copy), or transcode to High/Medium/Low
- Audio Bitrate: Audio quality for recordings (48k-192k)

**Storage Management:**
- Manually trigger cleanup of old recordings
- Delete all recordings with confirmation

⚠️ Note: Changing settings requires restarting the recording containers. Active recordings are saved before restart.

## 🗂️ Recording Storage

Recordings are stored in:
```
./recordings/
  ├── camera1/
  │   ├── 2026-02-13_11-21-02.mp4
  │   ├── 2026-02-13_11-30-00.mp4
  │   └── ...
  └── camera2/
      ├── 2026-02-13_11-21-02.mp4
      ├── 2026-02-13_11-30-00.mp4
      └── ...
```

File naming format: `YYYY-MM-DD_HH-MM-SS.mp4`
, 8082, 8554, or 8555 are already in use, edit `docker-compose.yml`:
```yaml
ports:
  - "8083:80"  # Change external port
```

### Recordings not appearing

1. **Check recorder logs:**
   ```bash
   docker logs splitcam_recorder_camera1
   docker logs splitcam_recorder_camera2
   ```

2. **Check API service:**
   ```bash
   docker logs splitcam_api
   curl http://localhost:8082/api/recordings
   ```
2
   ```

Note: All ports (1984, 8082, 8554, 8555)
   ls -lh recordings/camera2/
   ```

### High disk usage

- Reduce retention period in Settings tab
- Use lower video quality setting
- Reduce segment duration
- Manually clean old recordings
http://localhost:8082/api/recordings/camera1/2026-02-13_11-21-02.mp4
http://localhost:8082/api/recordings/camera2/2026-02-13_11-21-02.mp4
```

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
all services:
- `go2rtc`: WebRTC gateway (ports 1984, 8554, 8555)
- `web`: Nginx serving index.html (port 8082)
- `recorder-camera1` & `recorder-camera2`: FFmpeg DVR recorders
- `api`: Python Flask API for recording management
- `cleanup`: Automatic old recording cleanup (runs hourly)

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
Split-screen viewer with tabs:
- Live View: Real-time camera streaming
- Recordings: Browse and playback recordings
- Settings: Configure DVR settings

### api/app.py
Flask backend for:
- Listing recordings
- Serving recording files
- Deleting recordings
- Updating DVR settings
- Managing storage
## 📋 Common RTSP URLs for Tapo/TP-Link Cameras

Try these alternatives if `stream1` doesn't work:
- `rtsp:all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker logs splitcam_go2rtc
docker logs splitcam_camera-web
docker logs splitcam_recorder_camera1
docker logs splitcam_recorder_camera2
docker logs splitcam_api

# Restart after config changes
docker compose restart

# Restart just the recorders
docker compose restart recorder-camera1 recorder-camera2

# View running containers
docker ps

# Check recording storage usage
du -sh recordings/*

# Manually trigger cleanup
docker exec splitcam_cleanup sh /cleanup-recordings.sh

# Access API directly
curl http://localhost:8082/api/recordings
```

## 💾 Disk Space Management

### Estimated Storage Requirements

With default settings (10-minute segments, 24-hour retention):
- Camera 1 (2304x1296): ~3-4 MB per minute = ~4.3-5.8 GB per day
- Camera 2 (1920x1080): ~1.5-2 MB per minute = ~2.2-2.9 GB per day
- **Total: ~6.5-8.7 GB per day for 2 cameras**

### Reducing Storage Usage

1. **Decrease retention period** (Settings → Retention Period)
   - 12 hours: ~3-4 GB total
   - 6 hours: ~1.5-2 GB total

2. **Lower video quality** (Settings → Video Quality)
   - Medium (720p): ~60% of original size
   - Low (480p): ~40% of original size

3. **Copy original quality** (default)
   - No re-encoding, preserves original quality
   - Lowest CPU usageamera1:
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
