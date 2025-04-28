import os
from quart import Quart, render_template, request, jsonify, send_file
from dotenv import load_dotenv
from pathlib import Path
import json
from io import BytesIO
import asyncio

# Initialize paths for data storage
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
DATA_FILE = DATA_DIR / 'temp_result.json'

from backend.agents.orchestrator import OrchestratorAgent
from backend.utils.docx_generator import generate_docx

# Load environment variables from .env in the app directory
dotenv_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

app = Quart(__name__, 
    static_folder='frontend/static',
    template_folder='frontend/templates'
)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')

@app.route('/')
async def index():
    """Render the main form page"""
    return await render_template('index.html')

@app.route('/review')
async def review():
    """Render the review page"""
    return await render_template('review.html')

@app.route('/api/generate-grant', methods=['POST'])
async def generate_grant():
    """API endpoint to generate grant content"""
    data = await request.get_json()
    # Remove existing result for fresh polling
    if DATA_FILE.exists():
        DATA_FILE.unlink()
    # Extract required information
    nonprofit_website = data.get('nonprofit_website', '')
    grant_url = data.get('grant_url', '')
    nonprofit_name = data.get('nonprofit_name', '')
    nonprofit_mission = data.get('nonprofit_mission', '')
    
    # Initialize the orchestrator agent to coordinate the process
    orchestrator = OrchestratorAgent()
    
    # Launch generation process asynchronously
    async def generate_in_background():
        try:
            # Offload synchronous grant generation to a thread to avoid blocking the event loop
            result = await asyncio.to_thread(
                orchestrator.generate_grant_content,
                nonprofit_website,
                grant_url,
                nonprofit_name,
                nonprofit_mission
            )
            # Ensure data directory exists
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            # Store result in a temporary JSON file
            with DATA_FILE.open('w', encoding='utf-8') as f:
                json.dump(result, f)
        except Exception as bg_e:
            app.logger.error(f"Background generation error: {bg_e}")
    
    # Schedule background async task
    asyncio.create_task(generate_in_background())
    
    return jsonify({
        'status': 'processing',
        'message': 'Grant generation started. Redirecting to review page.'
    })

@app.route('/api/get-grant-status', methods=['GET'])
async def get_grant_status():
    """Check the status of grant generation"""
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open('r', encoding='utf-8') as f:
                result = json.load(f)
        except Exception as f_e:
            app.logger.error(f"Error reading result file: {f_e}")
            return jsonify({'status': 'error', 'message': 'Could not read result file.'}), 500
        return jsonify({
            'status': 'completed',
            'data': result
        })
    else:
        return jsonify({
            'status': 'processing',
            'message': 'Grant generation is still in progress'
        })

@app.route('/api/save-grant', methods=['POST'])
async def save_grant():
    """Save the edited grant as a docx file"""
    data = await request.get_json()
    content = data.get('content', {})
    
    # Generate docx file
    docx_bytes = generate_docx(content)
    
    # Create a BytesIO object to serve the file
    buffer = BytesIO(docx_bytes)
    buffer.seek(0)
    
    return await send_file(
        buffer,
        as_attachment=True,
        attachment_filename='grant_application.docx',
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true', port=5000) 