from database import StudentProgress

def calculate_points(reading_level, grade_level):
    base_points = 100
    level_difference = int(reading_level.split()[0]) - grade_level
    
    if level_difference > 0:
        return base_points + (level_difference * 50)
    elif level_difference < 0:
        return max(base_points // 2, 50)  # Minimum 50 points for effort
    else:
        return base_points

def get_achievements(db, student_id, points):
    achievements = []
    total_points = sum([p.points for p in db.query(StudentProgress).filter_by(student_id=student_id).all()])
    total_points += points  # Include current points
    
    if total_points >= 1000:
        achievements.append("Reading Champion")
    if total_points >= 500:
        achievements.append("Bookworm")
    if total_points >= 250:
        achievements.append("Eager Reader")
    
    consecutive_improvements = db.query(StudentProgress).filter_by(student_id=student_id).order_by(StudentProgress.timestamp.desc()).limit(3).all()
    if len(consecutive_improvements) == 3 and all(a.reading_level > b.reading_level for a, b in zip(consecutive_improvements, consecutive_improvements[1:])):
        achievements.append("Fast Learner")
    
    return achievements