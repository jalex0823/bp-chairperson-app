# Video Hosting Configuration

## Current Setup

Quiz tutorial videos are hosted externally at **therealbackporch.com** to avoid GitHub file size limits and Heroku slug size constraints.

### Video URLs

- **Registration Tutorial**: `https://therealbackporch.com/Videos/BP_Zoom_Host_Registration_Walkthrough.mp4`
- **Hosting Tutorial**: `https://therealbackporch.com/Videos/BP_Zoom_Hosting_Chairing_Guide.mp4`

## Configuration

The video base URL is set in `config.py`:

```python
VIDEO_BASE_URL = os.environ.get(
    'VIDEO_BASE_URL',
    'https://therealbackporch.com/Videos/'
)
```

### Environment Variable (Optional)

To use a different video hosting location, set the `VIDEO_BASE_URL` environment variable:

```bash
# On Heroku
heroku config:set VIDEO_BASE_URL="https://your-cdn.com/videos/"

# Locally (in .env file)
VIDEO_BASE_URL=https://your-cdn.com/videos/
```

## Local Development

For local development, you can:

1. **Use external videos** (default): Videos load from therealbackporch.com
2. **Use local videos**: 
   - Place videos in `static/videos/` directory
   - Set `VIDEO_BASE_URL=/static/videos/` in your environment

## Adding New Quizzes

When adding a new quiz with a video:

1. Upload the video to your hosting location
2. Add the quiz to `QUIZZES` in `app.py` with the video filename
3. The app will automatically prepend `VIDEO_BASE_URL` to the filename

Example:
```python
'new-quiz': {
    'id': 'new-quiz',
    'title': 'New Quiz Title',
    'video': 'your_video_filename.mp4',  # Will become: https://therealbackporch.com/Videos/your_video_filename.mp4
    'description': 'Quiz description',
    'questions': [...]
}
```

## Notes

- Videos are NOT stored in the git repository (excluded via `.gitignore`)
- Local copies in `static/videos/` are for development only
- Production always uses the external URL from `VIDEO_BASE_URL`
