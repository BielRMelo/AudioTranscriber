import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///transcriptions.db")
Base = declarative_base()

class TranscriptionRecord(Base):
    """Database model for storing transcription records"""
    __tablename__ = 'transcriptions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    duration = Column(Float, nullable=True)  # Duration in seconds
    language = Column(String(10), nullable=False, default='pt')
    transcription_text = Column(Text, nullable=False)
    processing_time = Column(Float, nullable=True)  # Time taken for processing
    created_at = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

class DatabaseService:
    """Service for managing database operations"""
    
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        self.create_tables()
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        try:
            Base.metadata.create_all(self.engine)
        except SQLAlchemyError as e:
            print(f"Error creating tables: {e}")
    
    def save_transcription(self, filename, file_size, language, transcription_text, 
                          duration=None, processing_time=None, success=True, error_message=None):
        """
        Save a transcription record to the database
        
        Args:
            filename (str): Original filename
            file_size (int): File size in bytes
            language (str): Language code
            transcription_text (str): Transcribed text
            duration (float, optional): Audio duration in seconds
            processing_time (float, optional): Processing time in seconds
            success (bool): Whether transcription was successful
            error_message (str, optional): Error message if failed
            
        Returns:
            int: ID of the saved record, or None if failed
        """
        session = self.Session()
        try:
            record = TranscriptionRecord(
                original_filename=filename,
                file_size=file_size,
                language=language,
                transcription_text=transcription_text,
                duration=duration,
                processing_time=processing_time,
                success=success,
                error_message=error_message
            )
            
            session.add(record)
            session.commit()
            return record.id
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error saving transcription: {e}")
            return None
        finally:
            session.close()
    
    def get_transcription_history(self, limit=50):
        """
        Get recent transcription history
        
        Args:
            limit (int): Maximum number of records to return
            
        Returns:
            list: List of transcription records
        """
        session = self.Session()
        try:
            records = session.query(TranscriptionRecord)\
                           .order_by(TranscriptionRecord.created_at.desc())\
                           .limit(limit)\
                           .all()
            
            # Convert to dictionary for easier handling
            result = []
            for record in records:
                result.append({
                    'id': record.id,
                    'filename': record.original_filename,
                    'file_size': record.file_size,
                    'duration': record.duration,
                    'language': record.language,
                    'transcription_text': record.transcription_text,
                    'processing_time': record.processing_time,
                    'created_at': record.created_at,
                    'success': record.success,
                    'error_message': record.error_message
                })
            
            return result
            
        except SQLAlchemyError as e:
            print(f"Error fetching transcription history: {e}")
            return []
        finally:
            session.close()
    
    def get_transcription_stats(self):
        """
        Get statistics about transcriptions
        
        Returns:
            dict: Statistics including total count, success rate, etc.
        """
        session = self.Session()
        try:
            total_count = session.query(TranscriptionRecord).count()
            successful_count = session.query(TranscriptionRecord)\
                                    .filter(TranscriptionRecord.success == True)\
                                    .count()
            
            # Calculate average processing time
            avg_processing_time = session.query(TranscriptionRecord.processing_time)\
                                       .filter(TranscriptionRecord.processing_time.isnot(None))\
                                       .all()
            
            avg_time = None
            if avg_processing_time:
                times = [t[0] for t in avg_processing_time if t[0] is not None]
                avg_time = sum(times) / len(times) if times else None
            
            # Calculate total audio duration processed
            total_duration = session.query(TranscriptionRecord.duration)\
                                  .filter(TranscriptionRecord.duration.isnot(None))\
                                  .all()
            
            total_audio_time = None
            if total_duration:
                durations = [d[0] for d in total_duration if d[0] is not None]
                total_audio_time = sum(durations) if durations else None
            
            return {
                'total_transcriptions': total_count,
                'successful_transcriptions': successful_count,
                'success_rate': (successful_count / total_count * 100) if total_count > 0 else 0,
                'average_processing_time': avg_time,
                'total_audio_duration': total_audio_time
            }
            
        except SQLAlchemyError as e:
            print(f"Error fetching transcription stats: {e}")
            return {
                'total_transcriptions': 0,
                'successful_transcriptions': 0,
                'success_rate': 0,
                'average_processing_time': None,
                'total_audio_duration': None
            }
        finally:
            session.close()
    
    def search_transcriptions(self, search_term, limit=20):
        """
        Search transcriptions by text content
        
        Args:
            search_term (str): Term to search for
            limit (int): Maximum number of results
            
        Returns:
            list: List of matching transcription records
        """
        session = self.Session()
        try:
            records = session.query(TranscriptionRecord)\
                           .filter(TranscriptionRecord.transcription_text.ilike(f'%{search_term}%'))\
                           .order_by(TranscriptionRecord.created_at.desc())\
                           .limit(limit)\
                           .all()
            
            result = []
            for record in records:
                result.append({
                    'id': record.id,
                    'filename': record.original_filename,
                    'transcription_text': record.transcription_text,
                    'created_at': record.created_at,
                    'language': record.language
                })
            
            return result
            
        except SQLAlchemyError as e:
            print(f"Error searching transcriptions: {e}")
            return []
        finally:
            session.close()
    
    def delete_transcription(self, transcription_id):
        """
        Delete a transcription record
        
        Args:
            transcription_id (int): ID of the record to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        session = self.Session()
        try:
            record = session.query(TranscriptionRecord)\
                          .filter(TranscriptionRecord.id == transcription_id)\
                          .first()
            
            if record:
                session.delete(record)
                session.commit()
                return True
            return False
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error deleting transcription: {e}")
            return False
        finally:
            session.close()
    
    def get_transcription_by_id(self, transcription_id):
        """
        Get a specific transcription by ID
        
        Args:
            transcription_id (int): ID of the transcription
            
        Returns:
            dict: Transcription record or None if not found
        """
        session = self.Session()
        try:
            record = session.query(TranscriptionRecord)\
                          .filter(TranscriptionRecord.id == transcription_id)\
                          .first()
            
            if record:
                return {
                    'id': record.id,
                    'filename': record.original_filename,
                    'file_size': record.file_size,
                    'duration': record.duration,
                    'language': record.language,
                    'transcription_text': record.transcription_text,
                    'processing_time': record.processing_time,
                    'created_at': record.created_at,
                    'success': record.success,
                    'error_message': record.error_message
                }
            return None
            
        except SQLAlchemyError as e:
            print(f"Error fetching transcription by ID: {e}")
            return None
        finally:
            session.close()