# Video Audio Merge

A Replicate Cog model for merging video and audio files with flexible output options. Perfect for content creators who need to replace soundtracks, add voiceovers, or combine separate video and audio streams.

## Features

- **Replace or Mix Audio**: Choose to completely replace the original audio or mix it with new audio
- **Multiple Format Support**: Output in MP4, MOV, AVI, or MKV formats
- **Codec Flexibility**: Support for H.264, H.265, VP9 video codecs and AAC, MP3 audio codecs
- **Volume Control**: Adjust the volume of the new audio track
- **Stream Copying**: Use 'copy' codec for faster processing when re-encoding isn't needed
- **Flexible Input**: Works with video-only, audio-only, or both inputs

## Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `video_file` | File | None | Input video file (MP4, MOV, AVI, etc.) |
| `audio_file` | File | None | Input audio file (MP3, WAV, AAC, etc.) |
| `replace_audio` | Boolean | True | Replace original audio completely (True) or mix with original audio (False) |
| `output_format` | String | "mp4" | Output video format: mp4, mov, avi, mkv |
| `video_codec` | String | "h264" | Video codec: h264, h265, vp9, copy |
| `audio_codec` | String | "aac" | Audio codec: aac, mp3, copy |
| `duration_mode` | String | "audio" | Duration control: "video" (match video length) or "audio" (match audio length) |
| `audio_volume` | Float | 1.0 | Audio volume multiplier (0.0 to 5.0, where 1.0 = original volume) |

## Usage Examples

### Replace Video Audio with New Track
```python
# Replace the original audio completely with a new soundtrack
output = replicate.run(
    "your-username/video-audio-merge",
    input={
        "video_file": open("my_video.mp4", "rb"),
        "audio_file": open("new_soundtrack.mp3", "rb"),
        "replace_audio": True,
        "audio_volume": 1.0
    }
)
```

### Mix Original Audio with Voiceover
```python
# Mix the original audio (50%) with a voiceover (50%)
output = replicate.run(
    "your-username/video-audio-merge",
    input={
        "video_file": open("my_video.mp4", "rb"),
        "audio_file": open("voiceover.wav", "rb"),
        "replace_audio": False,
        "audio_volume": 1.0
    }
)
```

### Create Video from Audio (with Black Screen)
```python
# Generate a video with black screen and your audio
output = replicate.run(
    "your-username/video-audio-merge",
    input={
        "audio_file": open("podcast.mp3", "rb"),
        "output_format": "mp4"
    }
)
```

### High-Quality Output with Custom Codecs
```python
# Use H.265 codec for better compression
output = replicate.run(
    "your-username/video-audio-merge",
    input={
        "video_file": open("source.mov", "rb"),
        "audio_file": open("audio.wav", "rb"),
        "output_format": "mov",
        "video_codec": "h265",
        "audio_codec": "aac",
        "audio_volume": 0.8
    }
)
```

### Fast Processing with Stream Copy
```python
# Use 'copy' codecs for fastest processing (no re-encoding)
output = replicate.run(
    "your-username/video-audio-merge",
    input={
        "video_file": open("video.mp4", "rb"),
        "audio_file": open("audio.aac", "rb"),
        "video_codec": "copy",
        "audio_codec": "copy"
    }
)
```

### Control Output Duration
```python
# Match video duration (truncate long audio, avoid frozen frames)
output = replicate.run(
    "your-username/video-audio-merge",
    input={
        "video_file": open("short_video.mp4", "rb"),  # 8 seconds
        "audio_file": open("long_audio.mp3", "rb"),   # 40 seconds
        "duration_mode": "video"  # Output will be 8 seconds
    }
)

# Match audio duration (extend video with frozen frame if needed)
output = replicate.run(
    "your-username/video-audio-merge",
    input={
        "video_file": open("short_video.mp4", "rb"),  # 8 seconds  
        "audio_file": open("long_audio.mp3", "rb"),   # 40 seconds
        "duration_mode": "audio"  # Output will be 40 seconds (default)
    }
)
```

## Use Cases

- **Content Creation**: Replace placeholder audio with final soundtracks
- **Podcast/Video Production**: Add background music or sound effects
- **Language Dubbing**: Replace original audio with translated versions
- **Audio Repair**: Replace corrupted audio tracks
- **Format Conversion**: Change container formats while merging audio
- **Voiceover Addition**: Mix narration with existing content

## Technical Details

### Supported Input Formats

**Video Files:**
- MP4, MOV, AVI, MKV, WebM, WMV, FLV

**Audio Files:**
- MP3, WAV, AAC, M4A, FLAC, OGG

### Output Quality

- **H.264/H.265**: Uses CRF 23 (medium quality) with medium preset for balanced quality and file size
- **Audio**: 192k bitrate for AAC/MP3 codecs (when not using 'copy')
- **Copy Codecs**: No re-encoding for maximum speed and quality preservation

### Audio Mixing Behavior

- **Replace Audio (True)**: Original video audio is completely removed
- **Mix Audio (False)**: Original audio (50% volume) + New audio (50% volume)
- **Volume Control**: Applied to the new audio before mixing

### Duration Control

- **Video Mode (`duration_mode="video"`)**: Output matches video duration
  - Longer audio tracks are truncated
  - Prevents frozen frames at the end
  - Ideal when you want exact video timing
  
- **Audio Mode (`duration_mode="audio"`)**: Output matches audio duration (default)
  - Shorter videos are extended by freezing the last frame
  - Longer videos are not truncated
  - Ideal for podcasts or when audio timing is priority

## Requirements

- Input files must be valid media files
- At least one input file (video or audio) must be provided
- For mixing mode, video file must contain an audio stream

## Error Handling

The model will return appropriate error messages for:
- Invalid or corrupted input files
- Unsupported file formats
- Missing required inputs
- Processing failures

## Development

This model is built using:
- **Cog**: For Replicate deployment
- **FFmpeg**: For media processing
- **Python**: Core logic and error handling

To run locally, ensure you have FFmpeg installed and the required Python packages.

## License

The code in this repository is licensed under the [Apache License 2.0](LICENSE).
