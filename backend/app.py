from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_session import Session
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import json
import logging
from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app)

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'educore_'
Session(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection pool
class DBConnection:
    @staticmethod
    def get_connection():
        try:
            connection = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                auth_plugin='mysql_native_password'
            )
            return connection
        except Error as err:
            logger.error(f"Database connection error: {err}")
            return None

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200

# Database check endpoint
@app.route('/api/db-check', methods=['GET'])
def db_check():
    connection = DBConnection.get_connection()
    if connection:
        connection.close()
        return jsonify({
            'status': 'connected',
            'database': Config.DB_NAME
        }), 200
    else:
        return jsonify({
            'status': 'disconnected',
            'error': 'Cannot connect to database'
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )