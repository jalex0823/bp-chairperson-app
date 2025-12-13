#!/usr/bin/env python3
"""
Check certificate status for a user
"""
from app import app, db, User, QuizAttempt

def main():
    with app.app_context():
        # Find user by BP ID
        user = User.query.filter_by(bp_id='BP-1002').first()
        
        if not user:
            print("User BP-1002 not found!")
            return
        
        print(f"User: {user.display_name or user.username}")
        print(f"User ID: {user.id}")
        print(f"BP ID: {user.bp_id}")
        print(f"ChairPoints: {user.chair_points or 0}")
        print()
        
        # Check quiz attempts
        attempts = QuizAttempt.query.filter_by(user_id=user.id).all()
        
        if not attempts:
            print("No quiz attempts found.")
            return
        
        print(f"Total Quiz Attempts: {len(attempts)}")
        print()
        
        passed_attempts = [a for a in attempts if a.passed]
        print(f"Passed Attempts: {len(passed_attempts)}")
        
        for attempt in passed_attempts:
            print(f"  - Quiz: {attempt.quiz_id}")
            print(f"    Score: {attempt.score}%")
            print(f"    Correct: {attempt.correct_answers}/{attempt.total_questions}")
            print(f"    Points: {attempt.points_awarded}")
            print(f"    Date: {attempt.completed_at}")
            print()
        
        # Check if eligible for certificate
        quiz_ids = set([a.quiz_id for a in passed_attempts])
        required = {'registration_quiz', 'hosting_quiz'}
        
        if required.issubset(quiz_ids):
            print("✓ ELIGIBLE FOR CERTIFICATE!")
            print(f"\nTo view certificate, visit:")
            print(f"http://localhost:5000/certificate/{user.id}")
        else:
            missing = required - quiz_ids
            print(f"✗ NOT eligible yet. Missing: {', '.join(missing)}")

if __name__ == "__main__":
    main()
