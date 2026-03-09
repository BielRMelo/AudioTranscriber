import os
from google import genai

class TranscriptionService:
    """Handles audio transcription using Google Gemini"""
    
    def __init__(self):
        # We will initialize the client dynamically or try to get from env
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        
        # Supported languages
        self.supported_languages = {
            'pt': 'Portuguese',
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French'
        }
    
    def transcribe_audio(self, audio_file_path, language="pt", api_key=None):
        """
        Transcribe audio file using Google Gemini
        
        Args:
            audio_file_path (str): Path to the audio file
            language (str): Language code for transcription (default: 'pt' for Portuguese)
            api_key (str): Optional Gemini API Key directly passed from the UI
            
        Returns:
            str: Transcribed text
            
        Raises:
            Exception: If transcription fails
        """
        try:
            # Set up client with provided API key or fallback to env
            current_api_key = api_key or self.api_key
            if not current_api_key:
                raise ValueError("A Gemini API Key must be provided to transcribe audio.")
                
            client = genai.Client(api_key=current_api_key)
            
            # Validate input file
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
            # Check file size (reasonable limit for processing)
            file_size = os.path.getsize(audio_file_path)
            max_size = 50 * 1024 * 1024  # 50MB limit for Gemini
            
            if file_size > max_size:
                raise Exception(f"File too large ({file_size / (1024*1024):.1f}MB). Maximum size is 50MB.")
            
            # Validate language code
            if language not in self.supported_languages:
                language = 'pt'  # Default to Portuguese
            
            # Language mapping for Gemini
            language_names = {
                'pt': 'Portuguese',
                'en': 'English', 
                'es': 'Spanish',
                'fr': 'French'
            }
            
            # Read audio file
            with open(audio_file_path, 'rb') as audio_file:
                audio_bytes = audio_file.read()
            
            # Create transcription prompt based on language
            prompt = f"Please transcribe this audio file accurately in {language_names.get(language, 'Portuguese')}. Only return the transcribed text, no additional commentary."
            
            # Use Gemini to transcribe audio
            from google.genai import types
            import base64
            
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[
                    types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type="audio/mp3"
                    ),
                    prompt
                ]
            )
            
            # Extract transcribed text
            transcription = response.text if response.text else ""
            
            if not transcription or not transcription.strip():
                raise Exception("No speech detected in the audio file")
            
            return transcription.strip()
            
        except FileNotFoundError as e:
            raise Exception(f"File error: {str(e)}")
        
        except Exception as e:
            # Handle API errors and other exceptions
            error_message = str(e)
            
            if "invalid_api_key" in error_message.lower() or "api_key" in error_message.lower():
                raise Exception("Invalid Gemini API key. Please check your API key configuration.")
            elif "quota" in error_message.lower():
                raise Exception("Gemini API quota exceeded. Please check your account usage.")
            elif "rate_limit" in error_message.lower():
                raise Exception("API rate limit exceeded. Please try again in a moment.")
            elif "file_too_large" in error_message.lower():
                raise Exception("Audio file is too large for processing. Maximum size is 50MB.")
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
    
    def validate_api_key(self, api_key=None):
        """
        Validate that the Gemini API key is working
        
        Args:
            api_key (str): Optional Gemini API Key directly passed from the UI
            
        Returns:
            bool: True if API key is valid, False otherwise
        """
        try:
            current_api_key = api_key or self.api_key
            if not current_api_key:
                return False
                
            client = genai.Client(api_key=current_api_key)
            # Try a simple API call to validate the key
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents="Hello"
            )
            return True
        except Exception:
            return False
