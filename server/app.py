
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db, Exercise, Workout, WorkoutExercises
from schemas import (
    ExerciseSchema,
    WorkoutSchema,
    WorkoutExercisesSchema,
)

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

workout_exercise_schema = WorkoutExercisesSchema()


def error_response(message, status_code):
    return jsonify({"error": message}), status_code


def read_json():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return None

    return data



@app.route("/workouts", methods=["GET"])
def get_workouts():
    workouts = Workout.query.order_by(Workout.id).all()
    return jsonify(workouts_schema.dump(workouts)), 200


@app.route("/workouts/<int:id>", methods=["GET"])
def get_workout(id):
    workout = db.session.get(Workout, id)

    if workout is None:
        return error_response("Workout not found.", 404)

    return jsonify(workout_schema.dump(workout)), 200


@app.route("/workouts", methods=["POST"])
def create_workout():
    data = read_json()

    if data is None:
        return error_response("Request body must be a JSON object.", 400)

    try:
        validated_data = workout_schema.load(data)

        workout = Workout(**validated_data)
        workout.validate()

        db.session.add(workout)
        db.session.commit()

        return jsonify(workout_schema.dump(workout)), 201

    except ValidationError as error:
        db.session.rollback()
        return jsonify({"errors": error.messages}), 400

    except ValueError as error:
        db.session.rollback()
        return error_response(str(error), 400)

    except IntegrityError:
        db.session.rollback()
        return error_response("Workout could not be saved.", 400)


@app.route("/workouts/<int:id>", methods=["DELETE"])
def delete_workout(id):
    workout = db.session.get(Workout, id)

    if workout is None:
        return error_response("Workout not found.", 404)

    try:
        
        WorkoutExercises.query.filter_by(
            workout_id=id
        ).delete(synchronize_session=False)

        db.session.delete(workout)
        db.session.commit()

        return jsonify({
            "message": "Workout deleted successfully."
        }), 200

    except IntegrityError:
        db.session.rollback()
        return error_response("Workout could not be deleted.", 409)


@app.route("/exercises", methods=["GET"])
def get_exercises():
    exercises = Exercise.query.order_by(Exercise.id).all()
    return jsonify(exercises_schema.dump(exercises)), 200


@app.route("/exercises/<int:id>", methods=["GET"])
def get_exercise(id):
    exercise = db.session.get(Exercise, id)

    if exercise is None:
        return error_response("Exercise not found.", 404)

    return jsonify(exercise_schema.dump(exercise)), 200


@app.route("/exercises", methods=["POST"])
def create_exercise():
    data = read_json()

    if data is None:
        return error_response("Request body must be a JSON object.", 400)

    try:
        validated_data = exercise_schema.load(data)

        exercise = Exercise(**validated_data)
        exercise.validate()

        db.session.add(exercise)
        db.session.commit()

        return jsonify(exercise_schema.dump(exercise)), 201

    except ValidationError as error:
        db.session.rollback()
        return jsonify({"errors": error.messages}), 400

    except ValueError as error:
        db.session.rollback()
        return error_response(str(error), 400)

    except IntegrityError:
        db.session.rollback()
        return error_response("Exercise could not be saved.", 400)


@app.route("/exercises/<int:id>", methods=["DELETE"])
def delete_exercise(id):
    exercise = db.session.get(Exercise, id)

    if exercise is None:
        return error_response("Exercise not found.", 404)

    try:
        
        WorkoutExercises.query.filter_by(
            exercise_id=id
        ).delete(synchronize_session=False)

        db.session.delete(exercise)
        db.session.commit()

        return jsonify({
            "message": "Exercise deleted successfully."
        }), 200

    except IntegrityError:
        db.session.rollback()
        return error_response("Exercise could not be deleted.", 409)



@app.route(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises",
    methods=["POST"],
)
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    exercise = db.session.get(Exercise, exercise_id)

    if workout is None:
        return error_response("Workout not found.", 404)

    if exercise is None:
        return error_response("Exercise not found.", 404)

    existing = WorkoutExercises.query.filter_by(
        workout_id=workout_id,
        exercise_id=exercise_id,
    ).first()

    if existing is not None:
        return error_response(
            "This exercise is already assigned to this workout.",
            409,
        )

    data = read_json()

    if data is None:
        return error_response("Request body must be a JSON object.", 400)

    try:
        
        validated_data = workout_exercise_schema.load(data)

        workout_exercise = WorkoutExercises(
            workout_id=workout_id,
            exercise_id=exercise_id,
            **validated_data,
        )

        workout_exercise.validate()

        db.session.add(workout_exercise)
        db.session.commit()

        return jsonify(
            workout_exercise_schema.dump(workout_exercise)
        ), 201

    except ValidationError as error:
        db.session.rollback()
        return jsonify({"errors": error.messages}), 400

    except ValueError as error:
        db.session.rollback()
        return error_response(str(error), 400)

    except IntegrityError:
        db.session.rollback()
        return error_response(
            "Workout exercise could not be saved.",
            409,
        )


if __name__ == "__main__":
    app.run(port=5555, debug=True)


