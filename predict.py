from cog import BasePredictor, Input, Path
import os
import ffmpeg
import tempfile

class Predictor(BasePredictor):
    def setup(self):
        """Load the model into memory to make running multiple predictions efficient"""
        pass

    def predict(
        self,
        video_file: Path = Input(
            description="Input video file (MP4, MOV, AVI, etc.)",
            default=None
        ),
        audio_file: Path = Input(
            description="Input audio file (MP3, WAV, AAC, etc.)",
            default=None
        ),
        duration_mode: str = Input(
            description="How to handle duration when video and audio lengths differ",
            choices=["video", "audio"],
            default="video"
        ),
        replace_audio: bool = Input(
            description="Replace original audio completely (True) or mix with original audio (False)",
            default=True
        ),
        audio_volume: float = Input(
            description="Audio volume multiplier (1.0 = original volume)",
            default=1.0,
            ge=0.0,
            le=5.0
        ),
        output_format: str = Input(
            description="Output video format",
            choices=["mp4", "mov", "avi", "mkv"],
            default="mp4"
        ),
        video_codec: str = Input(
            description="Video codec for output",
            choices=["h264", "h265", "vp9", "copy"],
            default="h264"
        ),
        audio_codec: str = Input(
            description="Audio codec for output",
            choices=["aac", "mp3", "copy"],
            default="aac"
        )
    ) -> Path:
        """Merge video and audio files with simplified options for easier use"""
        
        if not video_file and not audio_file:
            raise ValueError("At least one of video_file or audio_file must be provided")
        
        # Create temporary output file with specified format
        output_path = tempfile.mktemp(suffix=f'.{output_format}')
        
        try:
            # Build ffmpeg command
            inputs = {}
            
            # Video input
            if video_file:
                inputs['video'] = ffmpeg.input(str(video_file))
                video_stream = inputs['video']['v']
            
            # Audio input
            if audio_file:
                inputs['audio'] = ffmpeg.input(str(audio_file))
                audio_stream = inputs['audio']['a']
                
                # Apply volume adjustment
                if audio_volume != 1.0:
                    audio_stream = audio_stream.filter('volume', audio_volume)
            
            # Handle different scenarios
            output_streams = []
            
            if video_file and audio_file:
                # Both video and audio provided
                if replace_audio:
                    # Replace audio completely
                    output_streams = [video_stream, audio_stream]
                else:
                    # Mix original video audio with new audio (50/50 mix)
                    original_audio = inputs['video']['a'].filter('volume', 0.5)
                    new_audio = audio_stream.filter('volume', 0.5)
                    mixed_audio = ffmpeg.filter([original_audio, new_audio], 'amix', inputs=2)
                    output_streams = [video_stream, mixed_audio]
            
            elif video_file:
                # Only video provided - just process video with original audio
                output_streams = [video_stream, inputs['video']['a']]
            
            elif audio_file:
                # Only audio provided - create video with black screen
                black_video = ffmpeg.input('color=black:size=1280x720:rate=30', f='lavfi')
                output_streams = [black_video, audio_stream]
            
            # Build output kwargs with user-specified codecs
            output_kwargs = {
                'vcodec': video_codec,
                'acodec': audio_codec,
                'format': output_format
            }
            
            # Add quality settings for h264/h265 codecs
            if video_codec in ['h264', 'h265']:
                output_kwargs.update({
                    'crf': '23',        # Medium quality
                    'preset': 'medium'  # Balanced encoding speed
                })
            
            # Add audio bitrate for non-copy codecs
            if audio_codec != 'copy':
                output_kwargs['audio_bitrate'] = '192k'
            
            # Handle duration control based on user preference
            if video_file and audio_file and duration_mode == "video":
                # Limit output duration to video length (truncate audio if longer)
                output = ffmpeg.output(
                    *output_streams,
                    output_path,
                    shortest=None,
                    **output_kwargs
                )
            else:
                # Default behavior: match audio duration (extend video if needed)
                output = ffmpeg.output(
                    *output_streams,
                    output_path,
                    **output_kwargs
                )
            
            # Run ffmpeg command
            ffmpeg.run(output, overwrite_output=True, quiet=True)
            
            return Path(output_path)
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(output_path):
                os.remove(output_path)
            raise Exception(f"Error processing video/audio: {str(e)}")