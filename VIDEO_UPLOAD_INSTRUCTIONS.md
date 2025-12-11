# Video Upload Instructions

## Where to Place Video Files

Upload your training videos to the following location:

```
c:\Temp\bp-chairperson-app\static\videos\
```

## Required Video Files

You need to upload **TWO** video files with these exact names:

1. **registration_tutorial.mp4** - Registration tutorial video
2. **hosting_tutorial.mp4** - Hosting tutorial video

## Video Format Requirements

- **Format**: MP4 (recommended)
- **Codec**: H.264 video, AAC audio
- **Resolution**: 720p (1280x720) or 1080p (1920x1080)
- **File Size**: Under 100MB recommended for faster loading
- **Aspect Ratio**: 16:9

## How to Add Videos

### Option 1: Manual Copy
1. Navigate to: `c:\Temp\bp-chairperson-app\static\videos\`
2. Copy your MP4 files into this folder
3. Rename them to match the required names above

### Option 2: PowerShell
```powershell
# Example: Copy from Downloads to static/videos
Copy-Item "C:\Users\YourName\Downloads\your-registration-video.mp4" -Destination "c:\Temp\bp-chairperson-app\static\videos\registration_tutorial.mp4"
Copy-Item "C:\Users\YourName\Downloads\your-hosting-video.mp4" -Destination "c:\Temp\bp-chairperson-app\static\videos\hosting_tutorial.mp4"
```

## Video Conversion (if needed)

If your videos are not in MP4 format, you can convert them using:

### Using FFmpeg (Free)
```bash
ffmpeg -i input-video.mov -c:v libx264 -c:a aac -crf 23 registration_tutorial.mp4
```

### Using HandBrake (Free GUI Tool)
1. Download from https://handbrake.fr/
2. Import your video
3. Select "Web" preset
4. Set output name to `registration_tutorial.mp4`
5. Click "Start"

## Verify Videos Work

After uploading, test the videos:

1. Start your Flask app
2. Log in to the application
3. Go to Dashboard → Training Quizzes
4. Click on a quiz
5. Verify the video plays correctly

## Troubleshooting

### Video doesn't play
- Check the file name matches exactly (including .mp4 extension)
- Verify the file is in `static/videos/` folder
- Check browser console for errors (F12)
- Try a different browser (Chrome, Firefox, Edge)

### Video is too large
- Compress using HandBrake or FFmpeg
- Target file size: 50-100MB
- Reduce resolution if needed (720p is fine)

### Wrong format
- Convert to MP4 using tools above
- Use H.264 video codec
- Use AAC audio codec

## Current System Behavior

When users access a quiz:
1. ✅ Video plays automatically when they open the quiz page
2. ✅ They must watch at least 80% of the video
3. ✅ Quiz submission button unlocks after watching
4. ✅ They complete the quiz (20 questions)
5. ✅ Score 70%+ to pass and earn 50 ChairPoints
6. ✅ Receive a printable PDF certificate immediately

The certificate includes:
- User's name
- Quiz title
- Score percentage
- ChairPoints earned
- Completion date
- Back Porch ID
- Professional certificate design
