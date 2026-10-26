
from marshmallow import (
    Schema,
    fields,
    validate,
    validates,
    ValidationError,
)


class WorkoutExercisesSchema(Schema):
    id = fields.Integer(dump_only=True)
    workout_id = fields.Integer(dump_only=True)
    exercise_id = fields.Integer(dump_only=True)

    reps = fields.Integer(
        load_default=0,
        strict=True,
        validate=validate.Range(min=0),
    )
    sets = fields.Integer(
        load_default=0,
        strict=True,
        validate=validate.Range(min=0),
    )
    duration_seconds = fields.Integer(
        load_default=0,
        strict=True,
        validate=validate.Range(min=0),
    )

    exercise = fields.Nested(
        "ExerciseSchema",
        only=("id", "name", "category", "equipment_needed"),
        dump_only=True,
    )

    workout = fields.Nested(
        "WorkoutSchema",
        only=("id", "date", "duration_minutes", "notes"),
        dump_only=True,
    )


class ExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)

    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100),
    )
    category = fields.String(
        required=True,
        validate=validate.Length(min=2, max=50),
    )
    equipment_needed = fields.Boolean(required=True)

    workout_exercises = fields.Nested(
        WorkoutExercisesSchema,
        many=True,
        dump_only=True,
    )

    @validates("name")
    def validate_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Name cannot be blank.")

    @validates("category")
    def validate_category(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Category cannot be blank.")

class WorkoutSchema(Schema):
    id = fields.Integer(dump_only=True)

    date = fields.Date(required=True)

    duration_minutes = fields.Integer(
        required=True,
        strict=True,
        validate=validate.Range(min=1),
    )

    notes = fields.String(
        load_default="",
        validate=validate.Length(max=1000),
    )

    workout_exercises = fields.Nested(
        WorkoutExercisesSchema,
        many=True,
        dump_only=True,
    )
