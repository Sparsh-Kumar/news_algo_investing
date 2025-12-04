import os
from datetime import datetime, timezone
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from dotenv import load_dotenv
from helpers.types import DatabaseConfig
from database.mongo_database import MongoDatabase

load_dotenv()

app = Flask(__name__, static_folder='dashboard', static_url_path='')
# Configure CORS to allow all origins (since dashboard is served from same server, this ensures compatibility)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/api/llm-responses/today', methods=['GET', 'OPTIONS'])
def get_today_responses():
  # Handle preflight requests
  if request.method == 'OPTIONS':
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
    return response, 200
  database_config = DatabaseConfig(
    url = os.getenv('MONGODB_URI'),
    name = os.getenv('MONGODB_NAME')
  )
  mongodb_database = MongoDatabase(config=database_config)
  llm_handle = mongodb_database.get_table_handle('llm_request_responses')
  
  now = datetime.now(timezone.utc)
  start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=timezone.utc)
  end_of_day = datetime(now.year, now.month, now.day, 23, 59, 59, 999999, tzinfo=timezone.utc)
  
  records = list(llm_handle.find({
    'created_at': {'$gte': start_of_day, '$lte': end_of_day}
  }).sort('created_at', -1))
  
  for record in records:
    record['_id'] = str(record['_id'])
    if 'created_at' in record:
      record['created_at'] = record['created_at'].isoformat()
    if 'updated_at' in record:
      record['updated_at'] = record['updated_at'].isoformat()
  
  response = jsonify({
    'success': True,
    'count': len(records),
    'data': records
  })
  
  # Explicitly set CORS headers
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
  
  return response, 200

@app.route('/')
def index():
  return send_from_directory('dashboard', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
  # Only serve static files, not API routes
  if path.startswith('api/'):
    return jsonify({'error': 'Not found'}), 404
  return send_from_directory('dashboard', path)

if __name__ == '__main__':
  # Get configuration from environment variables
  debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
  host = os.getenv('FLASK_HOST', '0.0.0.0')
  port = int(os.getenv('FLASK_PORT', '5000'))
  
  app.run(debug=debug_mode, host=host, port=port)





