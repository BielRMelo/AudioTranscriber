import ffmpeg
import tempfile
import os
from pathlib import Path
import imageio_ffmpeg

class AudioProcessor:
    """Handles audio format conversion using FFmpeg"""
    
    def __init__(self):
        self.supported_input_formats = ['.ogg']
        self.output_format = '.mp3'
    
    def convert_ogg_to_mp3(self, ogg_file_path):
        """
        Convert OGG audio file to MP3 format
        
        Args:
            ogg_file_path (str): Path to the input OGG file
            
        Returns:
            str: Path to the converted MP3 file
            
        Raises:
            Exception: If conversion fails
        """
        try:
            # Validate input file exists
            if not os.path.exists(ogg_file_path):
                raise FileNotFoundError(f"Input file not found: {ogg_file_path}")
            
            # Create temporary file for MP3 output
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_mp3:
                mp3_output_path = temp_mp3.name
            
            # Use ffmpeg to convert OGG to MP3
            
            # Determine ffmpeg executable path
            ffmpeg_cmd = 'ffmpeg'
            try:
                # Test system ffmpeg
                ffmpeg.probe(ogg_file_path)
            except Exception:
                # Fallback to imageio-ffmpeg bundled executable
                ffmpeg_cmd = imageio_ffmpeg.get_ffmpeg_exe()
                
            (
                ffmpeg
                .input(ogg_file_path)
                .output(
                    mp3_output_path,
                    acodec='mp3',  # Use MP3 codec
                    audio_bitrate='192k',  # Set bitrate for good quality
                    ar=44100,  # Sample rate
                    ac=2  # Stereo channels
                )
                .overwrite_output()  # Overwrite output file if it exists
                .run(cmd=ffmpeg_cmd, capture_stdout=True, capture_stderr=True)
            )
            
            # Verify the output file was created
            if not os.path.exists(mp3_output_path):
                raise Exception("MP3 conversion failed - output file not created")
            
            # Check if output file has content
            if os.path.getsize(mp3_output_path) == 0:
                raise Exception("MP3 conversion failed - output file is empty")
            
            return mp3_output_path
            
        except FileNotFoundError as e:
            if "WinError 2" in str(e) or "No such file" in str(e):
                raise Exception("O FFmpeg não foi encontrado no seu sistema. Por favor, instale o FFmpeg e adicione-o ao PATH do Windows para que o aplicativo possa converter o áudio.")
            raise Exception(f"Audio conversion failed: {str(e)}")
        except Exception as e:
            # Handle FFmpeg specific errors
            if hasattr(e, 'stderr') and e.stderr:
                stderr_text = e.stderr.decode('utf-8') if isinstance(e.stderr, bytes) else str(e.stderr)
                error_message = f"FFmpeg conversion error: {stderr_text}"
            else:
                error_message = f"Audio conversion failed: {str(e)}"
            raise Exception(error_message)
    
    def validate_audio_file(self, file_path):
        """
        Validate that the file is a supported audio format
        
        Args:
            file_path (str): Path to the audio file
            
        Returns:
            bool: True if file is valid, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                return False
            
            # Check file extension
            file_extension = Path(file_path).suffix.lower()
            if file_extension not in self.supported_input_formats:
                return False
            
            # Use appropriate ffmpeg command
            ffmpeg_cmd = 'ffmpeg'
            try:
                ffmpeg.probe(file_path)
            except Exception:
                ffmpeg_cmd = imageio_ffmpeg.get_ffmpeg_exe()
            
            # Try to probe the file with ffmpeg to verify it's a valid audio file
            probe = ffmpeg.probe(file_path, cmd=ffmpeg_cmd)
            
            # Check if there are audio streams
            audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']
            
            return len(audio_streams) > 0
            
        except Exception:
            return False
    
    def get_audio_info(self, file_path):
        """
        Get information about the audio file
        
        Args:
            file_path (str): Path to the audio file
            
        Returns:
            dict: Audio file information
        """
        try:
            ffmpeg_cmd = 'ffmpeg'
            try:
                ffmpeg.probe(file_path)
            except Exception:
                ffmpeg_cmd = imageio_ffmpeg.get_ffmpeg_exe()
                
            probe = ffmpeg.probe(file_path, cmd=ffmpeg_cmd)
            
            # Get general format information
            format_info = probe.get('format', {})
            
            # Get audio stream information
            audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']
            
            if not audio_streams:
                return None
            
            audio_stream = audio_streams[0]  # Use first audio stream
            
            return {
                'duration': float(format_info.get('duration', 0)),
                'bitrate': int(format_info.get('bit_rate', 0)),
                'size': int(format_info.get('size', 0)),
                'codec': audio_stream.get('codec_name'),
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'channels': int(audio_stream.get('channels', 0))
            }
            
        except Exception as e:
            return None
