import os
from openai import OpenAI

class TranscriptionService:
    """Handles audio transcription using OpenAI Whisper"""
    
    def __init__(self):
        # Get OpenAI API key from environment variables
        self.api_key = os.getenv("OPENAI_API_KEY", "default_key")
        self.client = OpenAI(api_key=self.api_key)
        
        # Supported languages
        self.supported_languages = {
            'pt': 'Portuguese',
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French'
        }
    
    def transcribe_audio(self, audio_file_path, language="pt"):
        """
        Transcribe audio file using OpenAI Whisper
        
        Args:
            audio_file_path (str): Path to the audio file
            language (str): Language code for transcription (default: 'pt' for Portuguese)
            
        Returns:
            str: Transcribed text
            
        Raises:
            Exception: If transcription fails
        """
        try:
            # Validate input file
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
            # Check file size (OpenAI has a 25MB limit)
            file_size = os.path.getsize(audio_file_path)
            max_size = 25 * 1024 * 1024  # 25MB in bytes
            
            if file_size > max_size:
                raise Exception(f"File too large ({file_size / (1024*1024):.1f}MB). Maximum size is 25MB.")
            
            # Validate language code
            if language not in self.supported_languages:
                language = 'pt'  # Default to Portuguese
            
            # Perform transcription
            with open(audio_file_path, 'rb') as audio_file:
                # Use OpenAI Whisper API for transcription
                # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,  # Specify language for better accuracy
                    response_format="text"  # Get plain text response
                )
            
            # Extract transcribed text
            transcription = response
            
            if not transcription or not transcription.strip():
                raise Exception("No speech detected in the audio file")
            
            return transcription.strip()
            
        except FileNotFoundError as e:
            raise Exception(f"File error: {str(e)}")
        
        except Exception as e:
            # Handle API errors and other exceptions
            error_message = str(e)
            
            if "invalid_api_key" in error_message.lower():
                raise Exception("Invalid OpenAI API key. Please check your API key configuration.")
            elif "quota" in error_message.lower():
                raise Exception("OpenAI API quota exceeded. Please check your account usage.")
            elif "rate_limit" in error_message.lower():
                raise Exception("API rate limit exceeded. Please try again in a moment.")
            elif "file_too_large" in error_message.lower():
                raise Exception("Audio file is too large for processing. Maximum size is 25MB.")
            else:
                raise Exception(f"Transcription failed: {error_message}")
    
    def get_supported_languages(self):
        """
        Get list of supported languages for transcription
        
        Returns:
            dict: Dictionary of language codes and names
        """
        return self.supported_languages.copy()
    
    def estimate_processing_time(self, audio_duration_seconds):
        """
        Estimate processing time based on audio duration
        
        Args:
            audio_duration_seconds (float): Duration of audio in seconds
            
        Returns:
            float: Estimated processing time in seconds
        """
        # Rough estimate: Whisper typically processes audio faster than real-time
        # But API calls add overhead, so estimate ~0.3x the audio duration + base time
        base_time = 10  # Base processing time in seconds
        processing_rate = 0.3  # Processing rate multiplier
        
        estimated_time = base_time + (audio_duration_seconds * processing_rate)
        return max(estimated_time, 15)  # Minimum 15 seconds
    
    def validate_api_key(self):
        """
        Validate that the OpenAI API key is working
        
        Returns:
            bool: True if API key is valid, False otherwise
        """
        try:
            # Try a simple API call to validate the key
            # This is a minimal test that doesn't consume significant quota
            models = self.client.models.list()
            return True
        except Exception:
            return False
