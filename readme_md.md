# Hybrid Text Compression System

A web-based text compression system that combines Huffman Coding and Lempel-Ziv-Welch (LZW) algorithms to achieve superior compression ratios for text files.

## Features

- **Hybrid Compression Algorithm**: Combines LZW and Huffman coding for optimal compression
- **Web-Based Interface**: Easy-to-use drag-and-drop interface
- **User Authentication**: Secure user registration and login system
- **Compression History**: Track all your compression activities
- **Real-time Performance Metrics**: View compression ratios, file sizes, and processing times
- **Lossless Compression**: Perfect data recovery without any information loss
- **Mobile Responsive**: Works perfectly on all devices

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Database**: MySQL
- **Styling**: Custom CSS with modern design principles
- **Authentication**: Flask-SQLAlchemy with Werkzeug password hashing

## Installation

### Prerequisites

- Python 3.8 or higher
- MySQL Server
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hybrid-text-compression
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MySQL database**
   ```sql
   CREATE DATABASE compression_db;
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your database credentials:
   ```env
   SECRET_KEY=your-very-secure-secret-key-here
   DB_HOST=localhost
   DB_USER=your-mysql-username
   DB_PASSWORD=your-mysql-password
   DB_NAME=compression_db
   ```

6. **Initialize the database**
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

7. **Create required directories**
   ```bash
   mkdir uploads compressed
   ```

8. **Run the application**
   ```bash
   python app.py
   ```

   The application will be available at `http://localhost:5000`

## Usage

### For Users

1. **Register/Login**: Create an account or sign in to access the compression features
2. **Upload File**: Drag and drop or select a .txt file (max 16MB)
3. **Compress**: Click the compress button to process your file
4. **View Results**: See compression statistics including:
   - Original file size
   - Compressed file size
   - Compression ratio
   - Processing time
5. **Download**: Download the compressed file
6. **History**: View your compression history with detailed metrics

### API Endpoints

- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout
- `GET /dashboard` - User dashboard
- `POST /compress` - File compression
- `GET /download/<file_id>` - Download compressed file
- `GET /history` - Compression history

## Algorithm Details

### Hybrid Compression Process

1. **LZW Compression**: First stage uses dictionary-based compression to identify and replace repeating patterns
2. **Huffman Encoding**: Second stage applies statistical compression to assign shorter codes to frequent symbols
3. **Combined Benefits**: Achieves better compression ratios than either algorithm alone

### Performance

- **Average Compression Ratio**: 3:1 to 10:1 depending on text redundancy
- **Processing Speed**: < 1 second for most text files
- **Memory Efficient**: Optimized for web-based processing

## File Structure

```
hybrid-text-compression/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── .env.example         # Environment variables template
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
├── static/              # Static assets
│   ├── css/
│   │   └── style.css    # Main stylesheet
│   └── js/
│       └── main.js      # JavaScript functionality
├── uploads/             # Uploaded files (created at runtime)
└── compressed/          # Compressed files (created at runtime)
```

## Database Schema

### Users Table
- `user_id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `password_hash`
- `registration_date`

### Text Files Table
- `file_id` (Primary Key)
- `filename`
- `file_path`
- `file_size`
- `upload_date`
- `user_id` (Foreign Key)

### Compressed Files Table
- `result_id` (Primary Key)
- `file_id` (Foreign Key)
- `algorithm_used`
- `compressed_content_path`
- `compression_ratio`
- `original_size`
- `compressed_size`
- `compression_time`
- `compression_date`

## Security Features

- Password hashing using Werkzeug
- Session-based authentication
- CSRF protection
- File type validation
- File size limits
- Secure file handling

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

## Deployment

### Production Deployment with Gunicorn

1. Install Gunicorn: `pip install gunicorn`
2. Run with: `gunicorn --bind 0.0.0.0:8000 app:app`

### Environment Variables for Production

```env
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
DB_HOST=your-production-db-host
DB_USER=your-production-db-user
DB_PASSWORD=your-production-db-password
```

## Performance Optimization

- Enable gzip compression at the web server level
- Use a CDN for static assets
- Implement Redis for session storage in production
- Use connection pooling for database connections

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check MySQL server is running
   - Verify credentials in `.env` file
   - Ensure database exists

2. **File Upload Issues**
   - Check file permissions on upload directories
   - Verify file size limits
   - Ensure only .txt files are uploaded

3. **Compression Errors**
   - Check available disk space
   - Verify file encoding is UTF-8
   - Monitor memory usage for large files

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on research by Isong Josephine Friday
- Implements hybrid compression as described in academic literature
- Uses industry-standard security practices
- Follows modern web development patterns

## Support

For support, please open an issue on the repository or contact the development team.
