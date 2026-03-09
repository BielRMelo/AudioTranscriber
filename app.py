import streamlit as st
import os
import tempfile
import time
from pathlib import Path
from audio_processor import AudioProcessor
from transcription_service import TranscriptionService
from database_service import DatabaseService

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
    db_service = DatabaseService()
    
    # Sidebar with configuration and database features
    with st.sidebar:
        st.header("🔑 Configuration")
        # Check for API key in env or session state
        api_key = os.environ.get("GEMINI_API_KEY") or st.session_state.get("gemini_api_key", "")
        
        entered_api_key = st.text_input(
            "Gemini API Key",
            value=api_key,
            type="password",
            placeholder="AIzaSy...",
            help="Enter your Google Gemini API Key. You can get one at https://ai.google.dev"
        )
        
        if entered_api_key:
            st.session_state["gemini_api_key"] = entered_api_key
            # Temporarily set in env for google-genai to pick it up if needed by default, 
            # though we will also pass it explicitly.
            os.environ["GEMINI_API_KEY"] = entered_api_key
            
        if not entered_api_key:
            st.warning("Please enter your Gemini API Key to use the transcription feature.")
            
        st.divider()
        
        st.header("📊 Database Features")
        
        # Statistics
        stats = db_service.get_transcription_stats()
        st.metric("Total Transcriptions", stats['total_transcriptions'])
        st.metric("Success Rate", f"{stats['success_rate']:.1f}%")
        if stats['average_processing_time']:
            st.metric("Avg Processing Time", f"{stats['average_processing_time']:.1f}s")
        
        # Search functionality
        st.subheader("🔍 Search Transcriptions")
        search_term = st.text_input("Search in transcriptions", placeholder="Enter search term...")
        if search_term:
            search_results = db_service.search_transcriptions(search_term)
            if search_results:
                st.write(f"Found {len(search_results)} results:")
                for result in search_results[:5]:  # Show first 5 results
                    with st.expander(f"{result['filename']} - {result['created_at'].strftime('%Y-%m-%d %H:%M')}"):
                        st.text(result['transcription_text'][:200] + "..." if len(result['transcription_text']) > 200 else result['transcription_text'])
            else:
                st.write("No results found.")
        
        # Recent transcriptions
        st.subheader("📝 Recent Transcriptions")
        recent_transcriptions = db_service.get_transcription_history(limit=5)
        if recent_transcriptions:
            for record in recent_transcriptions:
                with st.expander(f"{record['filename']} - {record['created_at'].strftime('%Y-%m-%d %H:%M')}"):
                    st.text(f"Language: {record['language']}")
                    st.text(f"Duration: {record['duration']:.1f}s" if record['duration'] else "Duration: Unknown")
                    st.text(f"Success: {'✅' if record['success'] else '❌'}")
                    if record['transcription_text']:
                        st.text_area("Transcription", record['transcription_text'], height=100, disabled=True)
        else:
            st.write("No transcriptions yet.")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
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
                current_api_key = st.session_state.get("gemini_api_key")
                if not current_api_key:
                    st.error("Please enter your Gemini API Key in the sidebar first.")
                else:
                    process_audio_file(uploaded_file, audio_processor, transcription_service, db_service, current_api_key)
    
    with col2:
        # Language selection
        st.header("⚙️ Settings")
        language = st.selectbox(
            "Transcription Language",
            options=['pt', 'en', 'es', 'fr'],
            format_func=lambda x: {'pt': 'Portuguese', 'en': 'English', 'es': 'Spanish', 'fr': 'French'}[x],
            index=0
        )
        st.session_state['selected_language'] = language

def process_audio_file(uploaded_file, audio_processor, transcription_service, db_service, api_key):
    """Process the uploaded audio file through conversion and transcription"""
    
    # Create progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Get selected language from session state
    language = st.session_state.get('selected_language', 'pt')
    
    # Track timing
    start_time = time.time()
    
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
        
        # Get audio information
        audio_info = audio_processor.get_audio_info(mp3_path)
        duration = audio_info.get('duration') if audio_info else None
        
        # Step 3: Transcribe audio
        language_names = {'pt': 'Portuguese', 'en': 'English', 'es': 'Spanish', 'fr': 'French'}
        status_text.text(f"🎤 Transcribing audio ({language_names.get(language, 'Portuguese')})...")
        progress_bar.progress(70)
        
        transcription = transcription_service.transcribe_audio(mp3_path, language=language, api_key=api_key)
        
        # Step 4: Save to database
        status_text.text("💾 Saving to database...")
        progress_bar.progress(85)
        
        processing_time = time.time() - start_time
        
        record_id = db_service.save_transcription(
            filename=uploaded_file.name,
            file_size=uploaded_file.size,
            language=language,
            transcription_text=transcription,
            duration=duration,
            processing_time=processing_time,
            success=True
        )
        
        # Step 5: Create downloadable text file
        status_text.text("📝 Preparing transcription file...")
        progress_bar.progress(90)
        
        # Generate filename for transcription
        original_name = Path(uploaded_file.name).stem
        txt_filename = f"{original_name}_transcription.txt"
        
        progress_bar.progress(100)
        status_text.text("✅ Processing complete!")
        
        # Display results
        st.header("📝 Transcription Results")
        
        # Show processing info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Processing Time", f"{processing_time:.1f}s")
        with col2:
            st.metric("Duration", f"{duration:.1f}s" if duration else "Unknown")
        with col3:
            st.metric("Language", language_names.get(language, 'Unknown'))
        
        # Show transcription in a text area
        st.subheader("Transcribed Text:")
        st.text_area(
            "Transcription",
            value=transcription,
            height=200,
            help=f"Transcribed text in {language_names.get(language, 'Portuguese')}"
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
        
        # Show database record info
        if record_id:
            st.success(f"📁 Saved to database (Record ID: {record_id})")
        
    except Exception as e:
        # Save error to database
        processing_time = time.time() - start_time
        db_service.save_transcription(
            filename=uploaded_file.name,
            file_size=uploaded_file.size,
            language=language,
            transcription_text="",
            duration=None,
            processing_time=processing_time,
            success=False,
            error_message=str(e)
        )
        
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
