from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
import mysql.connector


app = Flask(__name__)
ma = Marshmallow(app)

@app.route('/')
def home():
    return "Welcome to the Fitness Database"




def get_db_connection():
    db_name = 'db_name'
    user = 'root'
    password = 'my_password'
    host = 'host'
    try:
        conn = mysql.connector.connect(
            database = db_name,
            user = user,
            password=password,
            host=host
        )
        print("Connected to MySQL database!")
        return conn
    
    except Exception as e:
        print(f'error: {e}')
        return None
    
class WorkoutSchema(ma.Schema):
    class Meta:
        fields = (
            'id',
            'member_id',
            'workout_date',
            'workout_type',
            'duration',
            'intensity',
            'notes'
        )

class MemberSchema(ma.Schema):
    class Meta:
        fields = ('id', 
                  'name', 
                  'email'
        )


workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

@app.route('/workouts', methods=['POST'])
def add_member():
    data = request.get_json()

    errors = member_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    try:
        name = data['name']
        email = data['email']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Members (name, email) VALUES (%s, %s)", (name, email))
        conn.commit()

        member_id = cursor.lastrowid
        conn.close()

        member_data = {
            "id": member_id,
            "name": name,
            "email": email
        }
        return member_schema.jsonify(member_data), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/workouts', methods=['POST'])   
def schedule_workout():
    data = request.get_json()

    errors = workout_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    try:
        member_id = data['member_id']
        workout_date = data['workout_date']
        workout_type = data['workout_type']
        duration = data['duration']
        intensity = data.get('intensity')
        notes = data.get('notes')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Workouts (member_id, workout_date, workout_type, duration, intensity, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (member_id, workout_date, workout_type, duration, intensity, notes))
        conn.commit()

        workout_id = cursor.lastrowid
        conn.close()

        workout_data = {
            "id": workout_id,
            "member_id": member_id,
            "workout_date": workout_date,
            "workout_type": workout_type,
            "duration": duration,
            "intensity": intensity,
            "notes": notes
        }
        return workout_schema.jsonify(workout_data), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/workouts/<int:id>', methods=['PUT'])
def update_workout(id):
    data = request.get_json()

    errors = workout_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    try:
        workout_date = data['workout_date']
        workout_type = data['workout_type']
        duration = data['duration']
        intensity = data.get('intensity')
        notes = data.get('notes')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Workouts
            SET workout_date = %s, workout_type = %s, duration = %s, intensity = %s, notes = %s
            WHERE id = %s
        """, (workout_date, workout_type, duration, intensity, notes, id))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Workout not found"}), 404

        conn.close()

        updated_workout = {
            "id": id,
            "workout_date": workout_date,
            "workout_type": workout_type,
            "duration": duration,
            "intensity": intensity,
            "notes": notes
        }
        return workout_schema.jsonify(updated_workout), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Workouts WHERE id = %s", (id,))
        workout = cursor.fetchone()

        if not workout:
            return jsonify({"error": "Workout not found"}), 404

        conn.close()
        return workout_schema.jsonify(workout), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/members/<int:member_id>/workouts', methods=['GET'])
def get_member_workouts(member_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Workouts WHERE member_id = %s ORDER BY workout_date", (member_id,))
        workouts = cursor.fetchall()

        if not workouts:
            return jsonify({"message": "No workouts found for this member"}), 404

        conn.close()
        return workouts_schema.jsonify(workouts), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_member(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Members WHERE id = %s", (id,))
        member = cursor.fetchone()
        if not member:
            return jsonify({"error": "Member not found"}), 404

        cursor.execute("DELETE FROM Members WHERE id = %s", (id,))
        conn.commit()
        conn.close()

        return jsonify({"message": "Member deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Workouts WHERE id = %s", (id,))
        workout = cursor.fetchone()
        if not workout:
            return jsonify({"error": "Workout not found"}), 404

        cursor.execute("DELETE FROM Workouts WHERE id = %s", (id,))
        conn.commit()
        conn.close()

        return jsonify({"message": "Workout deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

