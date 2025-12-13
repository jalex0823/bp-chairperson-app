"""Test quiz configuration"""
from app import QUIZZES

print("=" * 60)
print("Quiz System Verification")
print("=" * 60)

for quiz_id, quiz in QUIZZES.items():
    print(f"\n✓ {quiz['title']}")
    print(f"  ID: {quiz_id}")
    print(f"  Video: {quiz['video']}")
    print(f"  Questions: {len(quiz['questions'])}")
    print(f"  Description: {quiz['description']}")
    
    # Verify all questions have correct format
    for i, q in enumerate(quiz['questions'], 1):
        assert 'question' in q, f"Question {i} missing 'question' field"
        assert 'options' in q, f"Question {i} missing 'options' field"
        assert 'correct' in q, f"Question {i} missing 'correct' field"
        assert len(q['options']) == 4, f"Question {i} should have 4 options"
        assert 0 <= q['correct'] <= 3, f"Question {i} correct answer out of range"
    
    print(f"  ✓ All questions validated")

print("\n" + "=" * 60)
print("✓ Quiz system fully configured and validated!")
print("=" * 60)
print("\nNext steps:")
print("1. Upload videos to static/videos/:")
print("   - registration_tutorial.mp4")
print("   - hosting_tutorial.mp4")
print("2. Start the app: python app.py")
print("3. Test at: Dashboard → Training Quizzes")
