# OGG to MP3 Audio Transcriber

## Overview

This is a Streamlit-based web application that converts OGG audio files to MP3 format and transcribes them to text using OpenAI's Whisper API. The application is specifically designed for Brazilian Portuguese transcription but supports multiple languages.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web framework
- **Interface**: Single-page application with file upload and processing workflow
- **User Experience**: Progress tracking with visual feedback during processing
- **Layout**: Wide layout configuration with sidebar for database features
- **Database UI**: Sidebar with statistics, search functionality, and recent transcriptions

### Backend Architecture
- **Modular Design**: Four main components separated into distinct modules:
  - `app.py`: Main Streamlit application and UI logic
  - `audio_processor.py`: Audio format conversion handling
  - `transcription_service.py`: Audio transcription functionality
  - `database_service.py`: PostgreSQL database operations and record management
- **Processing Pipeline**: Sequential workflow (upload → convert → transcribe → save to database)
- **Database Layer**: PostgreSQL with SQLAlchemy ORM for persistent storage

## Key Components

### Audio Processor (`audio_processor.py`)
- **Purpose**: Converts OGG audio files to MP3 format
- **Technology**: FFmpeg for audio conversion
- **Features**:
  - File validation and error handling
  - Configurable output quality (192k bitrate, 44.1kHz sample rate, stereo)
  - Temporary file management for converted outputs

### Transcription Service (`transcription_service.py`)
- **Purpose**: Transcribes audio files to text
- **Technology**: Google Gemini API
- **Features**:
  - Multi-language support (Portuguese, English, Spanish, French)
  - File size validation (50MB Gemini limit)
  - User-selectable language with Portuguese as default

### Database Service (`database_service.py`)
- **Purpose**: Manages persistent storage of transcription records
- **Technology**: PostgreSQL with SQLAlchemy ORM
- **Features**:
  - Transcription history storage with metadata
  - Search functionality across transcription text
  - Statistics tracking (success rates, processing times)
  - Error logging and recovery tracking

### Main Application (`app.py`)
- **Purpose**: Orchestrates the entire workflow and provides user interface
- **Features**:
  - File upload handling with OGG format validation
  - Progress tracking and status updates
  - Integration between audio processing and transcription services

## Data Flow

1. **File Upload**: User uploads OGG audio file through Streamlit interface
2. **Language Selection**: User selects transcription language (Portuguese, English, Spanish, French)
3. **Validation**: File type and size validation
4. **Temporary Storage**: Uploaded file saved to temporary location
5. **Audio Conversion**: OGG file converted to MP3 using FFmpeg
6. **Transcription**: MP3 file sent to OpenAI Whisper API for transcription
7. **Database Storage**: Transcription record saved to PostgreSQL with metadata
8. **Results Display**: Transcribed text presented to user with download options
9. **Cleanup**: Temporary files removed after processing

## External Dependencies

### Required Python Packages
- `streamlit`: Web application framework
- `ffmpeg-python`: Audio conversion wrapper
- `google-genai`: Google Gemini API client for audio transcription
- `psycopg2-binary`: PostgreSQL database adapter
- `sqlalchemy`: SQL toolkit and ORM for database operations
- `pathlib`: File path handling (built-in)
- `tempfile`: Temporary file management (built-in)
- `os`: Operating system interface (built-in)

### System Dependencies
- **FFmpeg**: Must be installed on the system for audio conversion
- **Gemini API Key**: Required environment variable `GEMINI_API_KEY`

### External Services
- **Google Gemini API**: Cloud-based audio transcription service
  - File size limit: 50MB
  - Supports multiple languages
  - Requires API authentication

## Deployment Strategy

### Environment Requirements
- Python 3.7+ environment
- FFmpeg installed and accessible in system PATH
- Gemini API key configured as environment variable
- Sufficient disk space for temporary file processing

### Configuration Needs
- Environment variable: `GEMINI_API_KEY`
- System dependency: FFmpeg binary
- Streamlit configuration for wide layout and custom page settings

### Deployment Files
- **run_app.bat**: Executável principal para iniciar o aplicativo
- **setup.bat**: Script de configuração automática (executa como administrador)
- **LEIA_ME.txt**: Instruções completas de instalação e uso
- **app.py**: Aplicativo principal Streamlit

### Scalability Considerations
- File processing is synchronous and single-threaded
- Temporary file storage scales with concurrent users
- OpenAI API rate limits may apply based on subscription tier
- Memory usage scales with uploaded file sizes

### Security Considerations
- API key security through environment variables
- Temporary file cleanup to prevent data persistence
- File type validation to prevent malicious uploads
- File size limits to prevent resource exhaustion