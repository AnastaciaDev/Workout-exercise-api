
from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercises


def seed_data():
    with app.app_context():
        
        WorkoutExercises.query.delete()
        Workout.query.delete()
        Exercise.query.delete()
        db.session.commit()

        try:
            
            squat = Exercise(
                name="Squats",
                category="Strength",
                equipment_needed=False
            )

            push_up = Exercise(
                name="Push-ups",
                category="Strength",
                equipment_needed=False
            )

            treadmill = Exercise(
                name="Treadmill Running",
                category="Cardio",
                equipment_needed=True
            )

            exercises = [squat, push_up, treadmill]

            
            for exercise in exercises:
                exercise.validate()

            db.session.add_all(exercises)
            db.session.flush()  

            
            workout1 = Workout(
                date=date(2026, 10, 20),
                duration_minutes=45,
                notes="Full-body strength session"
            )

            workout2 = Workout(
                date=date(2026, 10, 22),
                duration_minutes=30,
                notes="Cardio and conditioning"
            )

            workouts = [workout1, workout2]

            for workout in workouts:
                workout.validate()

            db.session.add_all(workouts)
            db.session.flush()  

            workout_exercises = [
                WorkoutExercises(
                    workout=workout1,
                    exercise=squat,
                    reps=12,
                    sets=3,
                    duration_seconds=0
                ),
                WorkoutExercises(
                    workout=workout1,
                    exercise=push_up,
                    reps=10,
                    sets=3,
                    duration_seconds=0
                ),
                WorkoutExercises(
                    workout=workout2,
                    exercise=treadmill,
                    reps=0,
                    sets=0,
                    duration_seconds=1200
                ),
            ]

            for item in workout_exercises:
                item.validate()

            db.session.add_all(workout_exercises)
            db.session.commit()

            print("Database seeded successfully!")
            print("Created 3 exercises, 2 workouts, and 3 workout-exercise records.")

        except Exception:
            db.session.rollback()
            raise


if __name__ == "__main__":
    seed_data()
