"""Web interface for Drone Operations Agent."""
from flask import Flask, render_template, request, jsonify
import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agent import DroneOperationsAgent

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize agent with optional Google Sheets support
try:
    # Try separate Google Sheets first
    pilot_sheet_id = os.getenv("PILOT_SHEET_ID")
    drone_sheet_id = os.getenv("DRONE_SHEET_ID")
    mission_sheet_id = os.getenv("MISSION_SHEET_ID")
    
    # Fallback to single sheet or CSV
    google_sheets_id = os.getenv("GOOGLE_SHEETS_ID")
    
    if pilot_sheet_id and drone_sheet_id and mission_sheet_id:
        print("Loading from separate Google Sheets...")
        agent = DroneOperationsAgent(
            csv_path="./sample-data",
            pilot_sheet_id=pilot_sheet_id,
            drone_sheet_id=drone_sheet_id,
            mission_sheet_id=mission_sheet_id
        )
    elif google_sheets_id:
        print("Loading from Google Sheets...")
        agent = DroneOperationsAgent(csv_path="./sample-data", google_sheets_id=google_sheets_id)
    else:
        print("Loading from CSV files...")
        agent = DroneOperationsAgent(csv_path="./sample-data")
    
    print("OK: Agent initialized successfully!")
except Exception as e:
    print(f"ERROR: Error initializing agent: {e}")
    agent = None

@app.route('/')
def index():
    """Render the main chat interface."""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    if not agent:
        return jsonify({"error": "Agent not initialized"}), 500
    
    data = request.json
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
    
    try:
        response = agent.process_query(user_message)
        return jsonify({
            "success": True,
            "message": response
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Get agent status and database summary."""
    if not agent:
        return jsonify({"error": "Agent not initialized"}), 500
    
    return jsonify({
        "status": "ready",
        "summary": agent.get_database_summary()
    })

@app.route('/api/help', methods=['GET'])
def help_text():
    """Get help text."""
    if not agent:
        return jsonify({"error": "Agent not initialized"}), 500
    
    return jsonify({
        "help": agent._get_help_text()
    })

@app.route('/api/history', methods=['GET'])
def conversation_history():
    """Get conversation history."""
    if not agent:
        return jsonify({"error": "Agent not initialized"}), 500
    
    return jsonify({
        "history": agent.conversation_history
    })

@app.route('/api/sheets/status', methods=['GET'])
def sheets_status():
    """Get Google Sheets sync status."""
    if not agent:
        return jsonify({"error": "Agent not initialized"}), 500
    
    return jsonify({
        "use_google_sheets": agent.db.use_google_sheets,
        "spreadsheet_id": agent.db.spreadsheet_id or None,
        "message": "Connected to Google Sheets" if agent.db.use_google_sheets else "Using CSV data"
    })

@app.route('/api/sheets/sync', methods=['POST'])
def sheets_sync():
    """Sync current data to Google Sheets."""
    if not agent:
        return jsonify({"error": "Agent not initialized"}), 500
    
    if not agent.db.use_google_sheets:
        return jsonify({
            "success": False,
            "message": "Google Sheets not configured. Set GOOGLE_SHEETS_ID environment variable."
        }), 400
    
    try:
        success = agent.db.sync_to_google_sheets()
        return jsonify({
            "success": success,
            "message": "Data synced to Google Sheets successfully" if success else "Failed to sync to Google Sheets"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error syncing: {str(e)}"
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Server error"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
