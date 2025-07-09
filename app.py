import streamlit as st
import os
import tempfile
from pathlib import Path
from audio_processor import AudioProcessor
from transcription_service import TranscriptionService

def main():
    st.set_page_config(
        page_title="OGG to MP3 Transcriber",
        page_icon="🎵",
        layout="wide"
    )
    
    st.title("🎵 OGG Audio Transcriber")
    st.markdown("Upload OGG audio files to convert to MP3 and transcribe in Brazilian Portuguese")
    
    # Initialize services
    audio_processor = AudioProcessor()
    transcription_service = TranscriptionService()
    
    # File upload section
    st.header("📁 Upload Audio File")
    uploaded_file = st.file_uploader(
        "Choose an OGG audio file",
        type=['ogg'],
        help="Upload .ogg audio files for conversion and transcription"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        st.info(f"File size: {uploaded_file.size / (1024*1024):.2f} MB")
        
        # Process button
        if st.button("🔄 Process Audio", type="primary"):
            process_audio_file(uploaded_file, audio_processor, transcription_service)

def process_audio_file(uploaded_file, audio_processor, transcription_service):
    """Process the uploaded audio file through conversion and transcription"""
    
    # Create progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Save uploaded file
        status_text.text("📥 Saving uploaded file...")
        progress_bar.progress(10)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_ogg:
            temp_ogg.write(uploaded_file.getbuffer())
            temp_ogg_path = temp_ogg.name
        
        # Step 2: Convert OGG to MP3
        status_text.text("🔄 Converting OGG to MP3...")
        progress_bar.progress(30)
        
        mp3_path = audio_processor.convert_ogg_to_mp3(temp_ogg_path)
        
        # Step 3: Transcribe audio
        status_text.text("🎤 Transcribing audio (Brazilian Portuguese)...")
        progress_bar.progress(70)
        
        transcription = transcription_service.transcribe_audio(mp3_path, language="pt")
        
        # Step 4: Create downloadable text file
        status_text.text("📝 Preparing transcription file...")
        progress_bar.progress(90)
        
        # Generate filename for transcription
        original_name = Path(uploaded_file.name).stem
        txt_filename = f"{original_name}_transcription.txt"
        
        progress_bar.progress(100)
        status_text.text("✅ Processing complete!")
        
        # Display results
        st.header("📝 Transcription Results")
        
        # Show transcription in a text area
        st.subheader("Transcribed Text:")
        st.text_area(
            "Transcription",
            value=transcription,
            height=200,
            help="Transcribed text in Brazilian Portuguese"
        )
        
        # Download button for transcription
        st.download_button(
            label="📥 Download Transcription (.txt)",
            data=transcription,
            file_name=txt_filename,
            mime="text/plain",
            help="Download the transcription as a text file"
        )
        
        # Audio player for the converted MP3
        st.subheader("🎵 Converted Audio (MP3):")
        with open(mp3_path, 'rb') as audio_file:
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mp3')
        
        # Download button for MP3
        mp3_filename = f"{original_name}.mp3"
        st.download_button(
            label="📥 Download MP3",
            data=audio_bytes,
            file_name=mp3_filename,
            mime="audio/mp3",
            help="Download the converted MP3 file"
        )
        
    except Exception as e:
        st.error(f"❌ Error processing audio: {str(e)}")
        st.error("Please check that your file is a valid OGG audio file and try again.")
    
    finally:
        # Cleanup temporary files
        try:
            if 'temp_ogg_path' in locals():
                os.unlink(temp_ogg_path)
            if 'mp3_path' in locals():
                os.unlink(mp3_path)
        except:
            pass  # Ignore cleanup errors

if __name__ == "__main__":
    main()
