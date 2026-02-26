#!/usr/bin/env python3
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import json
import subprocess
from pathlib import Path
import yaml

app = Flask(__name__)
CORS(app)

RECORDINGS_DIR = '/recordings'
CONFIG_FILE = '/config/docker-compose.yml'
CLEANUP_SCRIPT = '/scripts/cleanup-recordings.sh'
STATE_FILE = '/recordings/.recording_state'

def get_recording_state():
    """Get the desired recording state from file"""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return f.read().strip() == 'enabled'
        return True  # Default to enabled
    except:
        return True

def set_recording_state(enabled):
    """Save the desired recording state to file"""
    try:
        with open(STATE_FILE, 'w') as f:
            f.write('enabled' if enabled else 'disabled')
    except Exception as e:
        print(f"Error saving recording state: {e}")

@app.route('/api/recordings', methods=['GET'])
def list_recordings():
    """List all recordings with metadata"""
    try:
        result = {
            'total_count': 0,
            'total_size': 0,
            'cameras': {}
        }

        for camera in ['camera1', 'camera2']:
            camera_dir = os.path.join(RECORDINGS_DIR, camera)
            camera_data = {
                'count': 0,
                'size': 0,
                'files': []
            }

            if os.path.exists(camera_dir):
                for filename in os.listdir(camera_dir):
                    if filename.endswith('.mp4'):
                        filepath = os.path.join(camera_dir, filename)
                        file_size = os.path.getsize(filepath)
                        
                        camera_data['files'].append({
                            'name': filename,
                            'size': file_size,
                            'duration': 10  # Default segment time
                        })
                        camera_data['count'] += 1
                        camera_data['size'] += file_size

            result['cameras'][camera] = camera_data
            result['total_count'] += camera_data['count']
            result['total_size'] += camera_data['size']

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recordings/<camera>/<filename>', methods=['GET'])
def get_recording(camera, filename):
    """Serve a recording file"""
    try:
        filepath = os.path.join(RECORDINGS_DIR, camera, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404

        return send_file(filepath, mimetype='video/mp4')

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recordings/<camera>/<filename>', methods=['DELETE'])
def delete_recording(camera, filename):
    """Delete a specific recording"""
    try:
        filepath = os.path.join(RECORDINGS_DIR, camera, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404

        os.remove(filepath)
        return jsonify({'success': True, 'message': 'Recording deleted'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recordings/all', methods=['DELETE'])
def delete_all_recordings():
    """Delete all recordings"""
    try:
        deleted_count = 0

        for camera in ['camera1', 'camera2']:
            camera_dir = os.path.join(RECORDINGS_DIR, camera)
            if os.path.exists(camera_dir):
                for filename in os.listdir(camera_dir):
                    if filename.endswith('.mp4'):
                        filepath = os.path.join(camera_dir, filename)
                        os.remove(filepath)
                        deleted_count += 1

        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Deleted {deleted_count} recordings'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cleanup', methods=['POST'])
def trigger_cleanup():
    """Manually trigger cleanup of old recordings"""
    try:
        # Run the cleanup script
        if os.path.exists(CLEANUP_SCRIPT):
            result = subprocess.run(['/bin/sh', CLEANUP_SCRIPT], capture_output=True, text=True)
            
            # Count remaining files to estimate what was deleted
            deleted_count = 0
            return jsonify({
                'success': True,
                'deleted_count': deleted_count,
                'message': 'Cleanup executed successfully',
                'output': result.stdout
            })
        else:
            return jsonify({'error': 'Cleanup script not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recording/toggle', methods=['POST'])
def toggle_recording():
    """Enable or disable recording"""
    try:
        data = request.json
        enabled = data.get('enabled', True)
        
        container_names = ['splitcam_recorder_camera1', 'splitcam_recorder_camera2']
        
        if enabled:
            # Start recorder containers
            result = subprocess.run(
                ['docker', 'start'] + container_names,
                capture_output=True,
                text=True
            )
        else:
            # Stop recorder containers
            result = subprocess.run(
                ['docker', 'stop'] + container_names,
                capture_output=True,
                text=True
            )
        
        if result.returncode == 0:
            # Save the desired state
            set_recording_state(enabled)
            
            return jsonify({
                'success': True,
                'enabled': enabled,
                'message': f'Recording {"enabled" if enabled else "disabled"} successfully'
            })
        else:
            return jsonify({
                'error': f'Failed to toggle recording: {result.stderr}'
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recording/status', methods=['GET'])
def recording_status():
    """Get current recording status"""
    try:
        # Check the saved state first
        desired_state = get_recording_state()
        
        # Check if recorder containers are running
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'name=recorder', '--format', '{{.Names}}'],
            capture_output=True,
            text=True
        )
        
        running_recorders = result.stdout.strip().split('\n')
        containers_running = len([r for r in running_recorders if r]) >= 2
        
        # If containers are running but should be stopped, stop them
        if containers_running and not desired_state:
            container_names = ['splitcam_recorder_camera1', 'splitcam_recorder_camera2']
            subprocess.run(
                ['docker', 'stop'] + container_names,
                capture_output=True,
                text=True
            )
            containers_running = False
        
        # If containers are stopped but should be running, start them
        elif not containers_running and desired_state:
            container_names = ['splitcam_recorder_camera1', 'splitcam_recorder_camera2']
            subprocess.run(
                ['docker', 'start'] + container_names,
                capture_output=True,
                text=True
            )
            containers_running = True
        
        return jsonify({
            'enabled': desired_state,
            'running_containers': running_recorders if containers_running else []
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current recording settings"""
    try:
        # Default settings
        settings = {
            'segment_time': 10,
            'retention_hours': 24,
            'video_quality': 'copy',
            'audio_bitrate': '128k'
        }
        
        return jsonify(settings)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update recording settings and restart containers"""
    try:
        settings = request.json
        segment_time = settings.get('segment_time', 10)
        retention_hours = settings.get('retention_hours', 24)
        video_quality = settings.get('video_quality', 'copy')
        audio_bitrate = settings.get('audio_bitrate', '128k')

        # Update docker-compose.yml
        compose_file = '/workspace/docker-compose.yml'
        if os.path.exists(compose_file):
            with open(compose_file, 'r') as f:
                compose_data = yaml.safe_load(f)

            # Update recorder commands
            segment_seconds = segment_time * 60
            
            for camera in ['recorder-camera1', 'recorder-camera2']:
                if camera in compose_data['services']:
                    camera_num = camera[-1]
                    
                    # Build video codec args
                    if video_quality == 'copy':
                        video_args = '-c:v copy'
                    elif video_quality == 'high':
                        video_args = '-c:v libx264 -preset medium -crf 23 -s 1920x1080'
                    elif video_quality == 'medium':
                        video_args = '-c:v libx264 -preset medium -crf 28 -s 1280x720'
                    else:  # low
                        video_args = '-c:v libx264 -preset medium -crf 32 -s 854x480'

                    command = f"-rtsp_transport tcp -i rtsp://go2rtc:8554/camera{camera_num} {video_args} -c:a aac -b:a {audio_bitrate} -f segment -segment_time {segment_seconds} -segment_atclocktime 1 -strftime 1 -reset_timestamps 1 /recordings/%Y-%m-%d_%H-%M-%S.mp4"
                    
                    compose_data['services'][camera]['command'] = command

            # Save updated docker-compose.yml
            with open(compose_file, 'w') as f:
                yaml.dump(compose_data, f, default_flow_style=False)

            # Update cleanup script retention time
            cleanup_file = '/workspace/cleanup-recordings.sh'
            if os.path.exists(cleanup_file):
                with open(cleanup_file, 'r') as f:
                    cleanup_content = f.read()

                retention_minutes = retention_hours * 60
                # Replace the mmin value
                cleanup_content = cleanup_content.replace('-mmin +1440', f'-mmin +{retention_minutes}')

                with open(cleanup_file, 'w') as f:
                    f.write(cleanup_content)

            # Restart recorder containers
            subprocess.run(['docker-compose', '-f', compose_file, 'restart', 'recorder-camera1', 'recorder-camera2'], 
                          cwd='/workspace', check=True)

            return jsonify({
                'success': True,
                'message': 'Settings updated and recorders restarted'
            })
        else:
            return jsonify({'error': 'docker-compose.yml not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
