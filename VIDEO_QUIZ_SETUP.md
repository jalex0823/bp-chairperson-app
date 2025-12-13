# Video Quiz System Setup Guide

## Overview
The video quiz system allows users to watch training videos and take quizzes to earn ChairPoints. Users must score 70% or higher to pass and earn 50 ChairPoints per quiz.

## Features
- 🎥 Video-based training content
- 📝 Multiple choice quizzes
- 🏆 ChairPoints rewards (50 points per passed quiz)
- 📊 Score tracking and history
- 🔒 Video completion required before quiz submission
- ♻️ Retake option (points awarded only once)

## Database Setup

### 1. Run the Migration
```bash
python add_quiz_attempts_table.py
```

This creates the `quiz_attempts` table to track quiz completions.

## Video Setup

### 2. Upload Video Files
Place your video files in `static/videos/` with these exact names:
- `registration_tutorial.mp4` - Registration tutorial video
- `hosting_tutorial.mp4` - Hosting tutorial video

**Supported formats:** MP4 (recommended), WebM, OGG

**Recommended specs:**
- Resolution: 720p or 1080p
- Codec: H.264
- Audio: AAC
- File size: < 50MB for faster loading

## Quiz Configuration

### 3. Add Quiz Questions
Edit `app.py` and update the `QUIZZES` dictionary with your questions:

```python
QUIZZES = {
    'registration': {
        'id': 'registration',
        'title': 'How to Register to Host a BP Online Zoom Meeting',
        'video': 'registration_tutorial.mp4',
        'description': 'Learn how to register as a chairperson for Back Porch meetings.',
        'questions': [
            {
                'question': 'What is the first step to register as a chairperson?',
                'options': [
                    'Click on the calendar',
                    'Go to your profile',
                    'Log in to your account',
                    'Send an email'
                ],
                'correct': 2  # Index of correct answer (0-based)
            },
            {
                'question': 'How many days in advance can you sign up?',
                'options': [
                    'Same day only',
                    'Up to 30 days',
                    'Up to 60 days',
                    'Up to 90 days'
                ],
                'correct': 2
            },
            # Add more questions...
        ]
    },
    'hosting': {
        'id': 'hosting',
        'title': 'How to Host a Zoom Meeting',
        'video': 'hosting_tutorial.mp4',
        'description': 'Learn the best practices for hosting a Back Porch Zoom meeting.',
        'questions': [
            {
                'question': 'When should you start the Zoom meeting?',
                'options': [
                    'Exactly at start time',
                    '5 minutes early',
                    '10 minutes early',
                    '15 minutes early'
                ],
                'correct': 2
            },
            # Add more questions...
        ]
    }
}
```

## User Access

### Dashboard Integration
Users can access quizzes from:
1. **Dashboard Quick Actions** - "Training Quizzes" button in the right sidebar
2. **Direct URL** - `/quizzes` route

### Quiz Flow
1. User clicks "Training Quizzes" from dashboard
2. Sees list of available quizzes with completion status
3. Clicks "Start Quiz" to view video and questions
4. Must watch at least 80% of video to unlock quiz submission
5. Completes quiz and submits answers
6. Receives immediate feedback with score
7. Earns 50 ChairPoints if score ≥ 70%

## Routes

- `GET /quizzes` - List all available quizzes
- `GET /quiz/<quiz_id>` - View specific quiz with video
- `POST /quiz/<quiz_id>/submit` - Submit quiz answers

## Database Schema

### quiz_attempts table
```sql
CREATE TABLE quiz_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    quiz_id VARCHAR(50) NOT NULL,
    score INT NOT NULL,
    total_questions INT NOT NULL,
    correct_answers INT NOT NULL,
    passed TINYINT(1) NOT NULL,
    answers TEXT,
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    points_awarded INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## Customization

### Passing Score
To change the passing score, edit in `app.py`:
```python
passed = score >= 70  # Change 70 to desired percentage
```

### ChairPoints Reward
To change points awarded, edit in `app.py`:
```python
points_awarded = 50  # Change 50 to desired amount
```

### Video Completion Requirement
To change required video watch percentage, edit in `quiz_view.html`:
```javascript
if (video.currentTime / video.duration >= 0.8) {  // Change 0.8 (80%)
```

## Testing

### Test the System
1. Log in as a regular user
2. Navigate to Training Quizzes
3. Watch a video
4. Complete a quiz
5. Verify:
   - Score is calculated correctly
   - ChairPoints are awarded (if passed)
   - Quiz shows as completed on list page
   - Points only awarded once on retake

## Troubleshooting

### Video Not Playing
- Check file path: `static/videos/[filename].mp4`
- Verify video format is MP4
- Check browser console for errors
- Ensure file permissions allow reading

### Quiz Not Submitting
- Check that all questions are answered
- Verify database connection
- Check browser console for JavaScript errors

### Points Not Awarded
- Verify user passed with 70%+
- Check that user hasn't already completed quiz
- Review database for quiz_attempts record
- Check user.chair_points field was updated

## Future Enhancements

Potential improvements:
- Quiz categories and difficulty levels
- Time limits for quiz completion
- Question randomization
- Progress saving (incomplete quizzes)
- Leaderboard for quiz completion
- Admin dashboard for quiz statistics
- Video transcripts/captions
- Multiple video chapters

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review application logs
3. Verify database migrations ran successfully
4. Ensure all required files are in place
