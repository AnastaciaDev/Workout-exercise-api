
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint

db = SQLAlchemy()


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    equipment_needed = db.Column(
        db.Boolean, nullable=False, default=False
    )

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) >= 2",
            name="check_exercise_name"
        ),
        CheckConstraint(
            "length(trim(category)) >= 2",
            name="check_exercise_category"
        ),
    )

    workout_exercises = db.relationship(
        "WorkoutExercises",
        back_populates="exercise",
        cascade="all, delete-orphan"
    )

    def validate(self):
        if not isinstance(self.name, str) or not 2 <= len(self.name.strip()) <= 100:
            raise ValueError("Name must contain 2–100 characters.")

        if not isinstance(self.category, str) or not 2 <= len(self.category.strip()) <= 50:
            raise ValueError("Category must contain 2–50 characters.")

        if not isinstance(self.equipment_needed, bool):
            raise ValueError("equipment_needed must be True or False.")


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=False, default="")

    __table_args__ = (
        CheckConstraint(
            "duration_minutes > 0",
            name="check_workout_duration"
        ),
        CheckConstraint(
            "length(notes) <= 1000",
            name="check_workout_notes_length"
        ),
    )

    workout_exercises = db.relationship(
        "WorkoutExercises",
        back_populates="workout",
        cascade="all, delete-orphan"
    )

    def validate(self):
        
        from datetime import date as Date

        if not isinstance(self.date, Date):
            raise ValueError("A valid workout date is required.")

        if (
            isinstance(self.duration_minutes, bool)
            or not isinstance(self.duration_minutes, int)
            or self.duration_minutes <= 0
        ):
            raise ValueError("Duration must be a positive integer.")

        if not isinstance(self.notes, str) or len(self.notes) > 1000:
            raise ValueError("Notes must be text with at most 1000 characters.")


class WorkoutExercises(db.Model):
    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, primary_key=True)

    workout_id = db.Column(
        db.Integer,
        db.ForeignKey("workouts.id", ondelete="CASCADE"),
        nullable=False
    )

    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False
    )

    reps = db.Column(db.Integer, nullable=False, default=0)
    sets = db.Column(db.Integer, nullable=False, default=0)
    duration_seconds = db.Column(db.Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint(
            "workout_id",
            "exercise_id",
            name="unique_exercise_per_workout"
        ),
        CheckConstraint("reps >= 0", name="check_reps"),
        CheckConstraint("sets >= 0", name="check_sets"),
        CheckConstraint(
            "duration_seconds >= 0",
            name="check_duration_seconds"
        ),
    )

    workout = db.relationship(
        "Workout",
        back_populates="workout_exercises"
    )

    exercise = db.relationship(
        "Exercise",
        back_populates="workout_exercises"
    )

    def validate(self):
        for field in ("reps", "sets", "duration_seconds"):
            value = getattr(self, field)

            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or value < 0
            ):
                raise ValueError(
                    f"{field} must be a non-negative integer."
                )


