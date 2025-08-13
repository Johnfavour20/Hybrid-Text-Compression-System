from flask import Flask, request, jsonify, send_file, render_template, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import pickle
import heapq
from collections import defaultdict, Counter
from datetime import datetime
import time
import tempfile
import uuid
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Use SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///compression_db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['COMPRESSED_FOLDER'] = 'compressed'

db = SQLAlchemy(app)

# Create upload directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['COMPRESSED_FOLDER'], exist_ok=True)

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    files = db.relationship('TextFile', backref='user', lazy=True)

class TextFile(db.Model):
    __tablename__ = 'text_files'
    file_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    
    # Relationships
    compressed_files = db.relationship('CompressedFile', backref='original_file', lazy=True)

class CompressedFile(db.Model):
    __tablename__ = 'compressed_files'
    result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_id = db.Column(db.Integer, db.ForeignKey('text_files.file_id'), nullable=False)
    algorithm_used = db.Column(db.String(100), default="Hybrid-Huffman-LZW")
    compressed_content_path = db.Column(db.String(500), nullable=False)
    compression_ratio = db.Column(db.Float, nullable=False)
    original_size = db.Column(db.Integer, nullable=False)
    compressed_size = db.Column(db.Integer, nullable=False)
    compression_time = db.Column(db.Float, nullable=False)
    compression_date = db.Column(db.DateTime, default=datetime.utcnow)

# Huffman Coding Implementation
class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanCompressor:
    def __init__(self):
        self.codes = {}
        self.reverse_codes = {}
        self.tree = None

    def build_frequency_table(self, text):
        return Counter(text)

    def build_huffman_tree(self, freq_table):
        heap = [HuffmanNode(char, freq) for char, freq in freq_table.items()]
        heapq.heapify(heap)

        while len(heap) > 1:
            node1 = heapq.heappop(heap)
            node2 = heapq.heappop(heap)

            merged = HuffmanNode(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2

            heapq.heappush(heap, merged)

        return heap[0] if heap else None

    def generate_codes(self, root):
        if not root:
            return

        if root.char is not None:
            self.codes[root.char] = '0' if not hasattr(self, 'codes') or not self.codes else '0'
            return

        self._generate_codes_helper(root, '')

    def _generate_codes_helper(self, node, code):
        if node.char is not None:
            self.codes[node.char] = code
            self.reverse_codes[code] = node.char
            return

        if node.left:
            self._generate_codes_helper(node.left, code + '0')
        if node.right:
            self._generate_codes_helper(node.right, code + '1')

    def compress(self, text):
        if not text:
            return '', {}

        freq_table = self.build_frequency_table(text)
        
        # Handle single character case
        if len(freq_table) == 1:
            char = list(freq_table.keys())[0]
            self.codes[char] = '0'
            return '0' * len(text), {'tree': None, 'codes': self.codes}

        self.tree = self.build_huffman_tree(freq_table)
        self.generate_codes(self.tree)

        compressed = ''.join(self.codes[char] for char in text)
        return compressed, {'tree': self.tree, 'codes': self.codes}

    def decompress(self, compressed_data, metadata):
        if not compressed_data:
            return ''

        codes = metadata['codes']
        tree = metadata['tree']
        
        if not tree:  # Single character case
            char = list(codes.keys())[0]
            return char * len(compressed_data)

        result = []
        current = tree
        
        for bit in compressed_data:
            if bit == '0':
                current = current.left
            else:
                current = current.right
            
            if current.char is not None:
                result.append(current.char)
                current = tree

        return ''.join(result)

# LZW Implementation
class LZWCompressor:
    def __init__(self):
        self.dictionary = {}
        self.dict_size = 256

    def compress(self, text):
        # Initialize dictionary with ASCII characters
        dictionary = {chr(i): i for i in range(256)}
        dict_size = 256
        
        result = []
        current_string = ""
        
        for char in text:
            combined = current_string + char
            if combined in dictionary:
                current_string = combined
            else:
                result.append(dictionary[current_string])
                dictionary[combined] = dict_size
                dict_size += 1
                current_string = char
        
        if current_string:
            result.append(dictionary[current_string])
        
        return result, dictionary

    def decompress(self, compressed_data, original_dict):
        # Create reverse dictionary for decompression
        dictionary = {v: k for k, v in original_dict.items() if v < 256}
        dict_size = 256
        
        if not compressed_data:
            return ""
        
        result = []
        prev_code = compressed_data[0]
        result.append(dictionary[prev_code])
        
        for code in compressed_data[1:]:
            if code in dictionary:
                current_string = dictionary[code]
            else:
                current_string = dictionary[prev_code] + dictionary[prev_code][0]
            
            result.append(current_string)
            dictionary[dict_size] = dictionary[prev_code] + current_string[0]
            dict_size += 1
            prev_code = code
        
        return ''.join(result)

# Hybrid Compression System
class HybridCompressor:
    def __init__(self):
        self.lzw_compressor = LZWCompressor()
        self.huffman_compressor = HuffmanCompressor()

    def compress(self, text):
        start_time = time.time()
        
        # Step 1: Apply LZW compression
        lzw_result, lzw_dict = self.lzw_compressor.compress(text)
        
        # Convert LZW result to string for Huffman processing
        lzw_string = ' '.join(map(str, lzw_result))
        
        # Step 2: Apply Huffman compression to LZW output
        huffman_result, huffman_metadata = self.huffman_compressor.compress(lzw_string)
        
        compression_time = time.time() - start_time
        
        # Calculate compression ratio
        original_size = len(text.encode('utf-8'))
        # Approximate compressed size (bits to bytes)
        compressed_size = len(huffman_result) // 8 + (1 if len(huffman_result) % 8 else 0)
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 0
        
        metadata = {
            'lzw_dict': lzw_dict,
            'huffman_metadata': huffman_metadata,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': compression_ratio,
            'compression_time': compression_time
        }
        
        return huffman_result, metadata

    def decompress(self, compressed_data, metadata):
        # Step 1: Huffman decompression
        lzw_string = self.huffman_compressor.decompress(compressed_data, metadata['huffman_metadata'])
        
        # Convert back to LZW format
        lzw_codes = list(map(int, lzw_string.split()))
        
        # Step 2: LZW decompression
        original_text = self.lzw_compressor.decompress(lzw_codes, metadata['lzw_dict'])
        
        return original_text

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data:
                return jsonify({'success': False, 'message': 'No data provided'})
            
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')
            
            # Validation
            if not all([username, email, password, confirm_password]):
                return jsonify({'success': False, 'message': 'All fields are required'})
            
            if password != confirm_password:
                return jsonify({'success': False, 'message': 'Passwords do not match'})
            
            if len(password) < 6:
                return jsonify({'success': False, 'message': 'Password must be at least 6 characters long'})
            
            if len(username) < 3:
                return jsonify({'success': False, 'message': 'Username must be at least 3 characters long'})
            
            # Check if user exists
            if User.query.filter_by(email=email).first():
                return jsonify({'success': False, 'message': 'Email already registered'})
            
            if User.query.filter_by(username=username).first():
                return jsonify({'success': False, 'message': 'Username already taken'})
            
            # Create new user
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': 'Registration successful',
                'redirect_url': url_for('login')
            })
            
        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {str(e)}")  # For debugging
            return jsonify({'success': False, 'message': 'Registration failed. Please try again.'}), 500
    
    # GET request - show registration form
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'success': False, 'message': 'No data provided'})
            
            email = data.get('email', '').strip()
            password = data.get('password', '')
            
            if not email or not password:
                return jsonify({'success': False, 'message': 'Email and password are required'})
            
            user = User.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.password_hash, password):
                session['user_id'] = user.user_id
                session['username'] = user.username
                return jsonify({'success': True, 'message': 'Login successful'})
            else:
                return jsonify({'success': False, 'message': 'Invalid email or password'})
                
        except Exception as e:
            print(f"Login error: {str(e)}")  # For debugging
            return jsonify({'success': False, 'message': 'Login failed. Please try again.'}), 500
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        user_files = TextFile.query.filter_by(user_id=session['user_id']).order_by(TextFile.upload_date.desc()).all()
        return render_template('dashboard.html', files=user_files, username=session['username'])
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        return redirect(url_for('index'))

@app.route('/compress', methods=['POST'])
@login_required
def compress_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'})
        
        if not file.filename.lower().endswith('.txt'):
            return jsonify({'success': False, 'message': 'Only .txt files are allowed'})
        
        # Read file content
        try:
            content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            return jsonify({'success': False, 'message': 'File must be a valid UTF-8 text file'})
        
        if not content.strip():
            return jsonify({'success': False, 'message': 'File is empty'})
        
        # Save original file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Save file record
        text_file = TextFile(
            filename=filename,
            file_path=file_path,
            file_size=len(content.encode('utf-8')),
            user_id=session['user_id']
        )
        db.session.add(text_file)
        db.session.flush()  # Get the ID
        
        # Compress using hybrid algorithm
        compressor = HybridCompressor()
        compressed_data, metadata = compressor.compress(content)
        
        # Save compressed file
        compressed_filename = f"compressed_{unique_filename}.pkl"
        compressed_path = os.path.join(app.config['COMPRESSED_FOLDER'], compressed_filename)
        
        with open(compressed_path, 'wb') as f:
            pickle.dump({'data': compressed_data, 'metadata': metadata}, f)
        
        # Save compression result
        compressed_file = CompressedFile(
            file_id=text_file.file_id,
            compressed_content_path=compressed_path,
            compression_ratio=metadata['compression_ratio'],
            original_size=metadata['original_size'],
            compressed_size=metadata['compressed_size'],
            compression_time=metadata['compression_time']
        )
        
        db.session.add(compressed_file)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'File compressed successfully',
            'result': {
                'original_size': metadata['original_size'],
                'compressed_size': metadata['compressed_size'],
                'compression_ratio': round(metadata['compression_ratio'], 2),
                'compression_time': round(metadata['compression_time'], 3),
                'file_id': text_file.file_id
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Compression error: {str(e)}")  # For debugging
        return jsonify({'success': False, 'message': f'Compression failed: {str(e)}'})

@app.route('/download/<int:file_id>')
@login_required
def download_compressed(file_id):
    try:
        text_file = TextFile.query.filter_by(file_id=file_id, user_id=session['user_id']).first()
        if not text_file:
            return jsonify({'success': False, 'message': 'File not found'})
        
        compressed_file = CompressedFile.query.filter_by(file_id=file_id).first()
        if not compressed_file:
            return jsonify({'success': False, 'message': 'Compressed file not found'})
        
        if not os.path.exists(compressed_file.compressed_content_path):
            return jsonify({'success': False, 'message': 'Compressed file not found on disk'})
        
        return send_file(
            compressed_file.compressed_content_path,
            as_attachment=True,
            download_name=f"compressed_{text_file.filename}.pkl"
        )
        
    except Exception as e:
        print(f"Download error: {str(e)}")  # For debugging
        return jsonify({'success': False, 'message': f'Download failed: {str(e)}'})

@app.route('/history')
@login_required
def compression_history():
    try:
        files = db.session.query(TextFile, CompressedFile).join(
            CompressedFile, TextFile.file_id == CompressedFile.file_id
        ).filter(TextFile.user_id == session['user_id']).order_by(TextFile.upload_date.desc()).all()
        
        history = []
        for text_file, compressed_file in files:
            history.append({
                'filename': text_file.filename,
                'upload_date': text_file.upload_date.strftime('%Y-%m-%d %H:%M'),
                'original_size': compressed_file.original_size,
                'compressed_size': compressed_file.compressed_size,
                'compression_ratio': compressed_file.compression_ratio,
                'compression_time': compressed_file.compression_time,
                'file_id': text_file.file_id
            })
        
        return jsonify({'success': True, 'history': history})
        
    except Exception as e:
        print(f"History error: {str(e)}")  # For debugging
        return jsonify({'success': False, 'message': 'Failed to load history'})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Page not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.errorhandler(413)
def too_large(error):
    return jsonify({'success': False, 'message': 'File too large. Maximum size is 16MB.'}), 413

if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Print some helpful information
        print("Server starting...")
        print("Access the application at: http://localhost:5001")
        print("Available routes:")
        print("  - / (Home)")
        print("  - /register (Registration)")
        print("  - /login (Login)")
        print("  - /dashboard (User Dashboard)")
        
    app.run(debug=True, port=5001)