import json
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime
import threading
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit

from .integrated_bio_system import IntegratedBioSystem
import os

class BioDashboard:
    def __init__(self, host: str = '0.0.0.0', port: int = 5000):
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.system = IntegratedBioSystem()
        self.host = host
        self.port = port
        self.update_interval = 2.0  # seconds
        self.update_thread = None
        self.dashboard_active = False
        
        # Setup routes
        self._setup_routes()
        self._setup_socket_handlers()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/api/status')
        def get_status():
            return jsonify(self.system.get_system_status())
        
        @self.app.route('/api/start', methods=['POST'])
        def start_system():
            success = self.system.startup_sequence()
            return jsonify({'success': success, 'status': self.system.get_system_status()})
        
        @self.app.route('/api/stop', methods=['POST'])
        def stop_system():
            self.system.shutdown_sequence()
            return jsonify({'success': True, 'status': self.system.get_system_status()})
        
        @self.app.route('/api/emergency-stop', methods=['POST'])
        def emergency_stop():
            self.system.emergency_stop()
            return jsonify({'success': True})
        
        @self.app.route('/api/data/ingest', methods=['POST'])
        def ingest_data():
            data = request.json
            if not data or 'data_type' not in data or 'values' not in data:
                return jsonify({'error': 'Invalid data format'}), 400
            
            success = self.system.ingest_biological_data(
                data['data_type'], 
                data['values'],
                data.get('source', 'api')
            )
            return jsonify({'success': success})
        
        @self.app.route('/api/treatment/cycle', methods=['POST'])
        def run_treatment_cycle():
            data = request.json or {}
            audio_path = data.get('audio_path')
            
            result = self.system.run_treatment_cycle(audio_path)
            if result:
                return jsonify({'success': True, 'result': result})
            else:
                return jsonify({'success': False, 'error': 'Treatment cycle failed'}), 500
        
        @self.app.route('/api/history/<data_type>')
        def get_history(data_type: str):
            limit = int(request.args.get('limit', 100))
            # This would interface with data processor history
            return jsonify({'data_type': data_type, 'history': []})  # Placeholder
    
    def _setup_socket_handlers(self):
        """Setup SocketIO event handlers"""
        @self.socketio.on('connect')
        def handle_connect():
            logging.info(f"Client connected: {request.sid}")
            emit('system_status', self.system.get_system_status())
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logging.info(f"Client disconnected: {request.sid}")
        
        @self.socketio.on('start_updates')
        def handle_start_updates():
            self.dashboard_active = True
            emit('update_started', {'interval': self.update_interval})
        
        @self.socketio.on('stop_updates')
        def handle_stop_updates():
            self.dashboard_active = False
            emit('update_stopped', {})
    
    def _update_loop(self):
        """Background update loop for real-time data"""
        while self.dashboard_active:
            try:
                status = self.system.get_system_status()
                self.socketio.emit('real_time_update', status)
                time.sleep(self.update_interval)
            except Exception as e:
                logging.error(f"Update loop error: {e}")
                time.sleep(1)
    
    def start_dashboard(self):
        """Start the dashboard server"""
        try:
            # Create templates directory if needed
            import os
            templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
            os.makedirs(templates_dir, exist_ok=True)
            
            # Create basic HTML template
            self._create_html_template(templates_dir)
            
            logging.info(f"Starting bio-dashboard on {self.host}:{self.port}")
            
            # Start update thread
            self.dashboard_active = True
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()
            
            # Start Flask server
            self.socketio.run(self.app, host=self.host, port=self.port, debug=False)
            
        except Exception as e:
            logging.error(f"Failed to start dashboard: {e}")
        finally:
            self.dashboard_active = False
    
    def _create_html_template(self, templates_dir: str):
        """Create HTML template for dashboard"""
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bio-Rehabilitation Dashboard</title>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .dashboard { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric { font-size: 2em; font-weight: bold; color: #2c3e50; }
        .progress-bar { background: #ecf0f1; height: 20px; border-radius: 10px; overflow: hidden; margin: 10px 0; }
        .progress-fill { background: #3498db; height: 100%; transition: width 0.3s ease; }
        .chart-container { height: 300px; margin-top: 20px; }
        .controls { display: flex; gap: 10px; margin-bottom: 20px; }
        button { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .btn-start { background: #27ae60; color: white; }
        .btn-stop { background: #e74c3c; color: white; }
        .btn-emergency { background: #c0392b; color: white; font-weight: bold; }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>Neuro-Rehabilitation Monitoring System</h1>
            <p>Real-time biological repair progress monitoring</p>
        </div>

        <div class="controls">
            <button class="btn-start" onclick="startSystem()">Start System</button>
            <button class="btn-stop" onclick="stopSystem()">Stop System</button>
            <button class="btn-emergency" onclick="emergencyStop()">EMERGENCY STOP</button>
        </div>

        <div class="status-grid">
            <div class="card">
                <h3>Overall Progress</h3>
                <div class="metric" id="overall-progress">0%</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="progress-bar" style="width: 0%"></div>
                </div>
            </div>

            <div class="card">
                <h3>BBB Integrity</h3>
                <div class="metric" id="bbb-integrity">0%</div>
                <div>Blood-Brain Barrier Restoration</div>
            </div>

            <div class="card">
                <h3>Neuroinflammation</h3>
                <div class="metric" id="inflammation-level">100%</div>
                <div>Inflammation Resolution</div>
            </div>

            <div class="card">
                <h3>Treatment Phase</h3>
                <div class="metric" id="treatment-phase">Offline</div>
                <div>Current Protocol</div>
            </div>
        </div>

        <div class="card">
            <h3>Real-time Progress</h3>
            <div class="chart-container">
                <canvas id="progress-chart"></canvas>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let progressChart = null;

        socket.on('connect', () => {
            console.log('Connected to server');
            socket.emit('start_updates');
        });

        socket.on('real_time_update', (data) => {
            updateDashboard(data);
        });

        function updateDashboard(data) {
            // Update overall progress
            const progress = data.repair_progress || 0;
            document.getElementById('overall-progress').textContent = progress.toFixed(1) + '%';
            document.getElementById('progress-bar').style.width = progress + '%';

            // Update BBB integrity
            const bbbIntegrity = data.bio_status?.blood_brain_barrier?.integrity_percent || 0;
            document.getElementById('bbb-integrity').textContent = bbbIntegrity.toFixed(1) + '%';

            // Update inflammation
            const inflammation = data.bio_status?.neuroinflammation?.level_percent || 100;
            document.getElementById('inflammation-level').textContent = inflammation.toFixed(1) + '%';

            // Update treatment phase
            document.getElementById('treatment-phase').textContent = data.treatment_phase || 'Offline';

            // Update chart
            updateChart(progress);
        }

        function updateChart(progress) {
            // Chart update logic would go here
        }

        async function startSystem() {
            const response = await fetch('/api/start', { method: 'POST' });
            const result = await response.json();
            console.log('System started:', result);
        }

        async function stopSystem() {
            const response = await fetch('/api/stop', { method: 'POST' });
            const result = await response.json();
            console.log('System stopped:', result);
        }

        async function emergencyStop() {
            if (confirm('Are you sure you want to emergency stop?')) {
                const response = await fetch('/api/emergency-stop', { method: 'POST' });
                const result = await response.json();
                console.log('Emergency stop activated:', result);
            }
        }

        // Initialize chart
        const ctx = document.getElementById('progress-chart').getContext('2d');
        progressChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Repair Progress',
                    data: [],
                    borderColor: '#3498db',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    </script>
</body>
</html>'''
        
        with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
            f.write(html_content)
    
    def stop_dashboard(self):
        """Stop the dashboard"""
        self.dashboard_active = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=2.0)
        logging.info("Dashboard stopped")

# Command line interface
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    import argparse
    parser = argparse.ArgumentParser(description="Bio-Rehabilitation Dashboard")
    parser.add_argument('--host', default='0.0.0.0', help="Host address")
    parser.add_argument('--port', type=int, default=5000, help="Port number")
    parser.add_argument('--simulate', action='store_true', help="Run simulation mode")
    
    args = parser.parse_args()
    
    dashboard = BioDashboard(host=args.host, port=args.port)
    
    try:
        if args.simulate:
            # Run simulation in background
            import threading
            def run_simulation():
                time.sleep(2)  # Wait for dashboard to start
                dashboard.system.simulate_treatment_progress(12)  # 12-hour simulation
            
            sim_thread = threading.Thread(target=run_simulation, daemon=True)
            sim_thread.start()
        
        dashboard.start_dashboard()
        
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    finally:
        dashboard.stop_dashboard()