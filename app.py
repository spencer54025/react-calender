from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')

db = SQLAlchemy(app) #database
ma = Marshmallow(app)


# reminder class and schema
class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.string, nullable=False)
    date = db.Column(db.Integer, nullable=False)
    month_id = db.Column(db.Integer, db.ForeignKey('month.id'), nullable=False)

    def __init__(self, text, date, month_id):
        self.text = text
        self.date = date
        self.month_id = month_id

class ReminderSchema(ma.Schema):
    class Meta:
        fields = ('id', 'date', 'month_id')

reminder_schema = ReminderSchema()
multi_reminder_schema = ReminderSchema(many=True)


# month class and schema
class Month(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    start_day = db.Column(db.Integer, nullable=False)
    days_in_month = db.Column(db.Integer, nullable=False)
    previous_days = db.Column(db.Integer, nullable=False)
    reminders = db.Column(db.relationship('Reminder', backref='month', cascade='all, delete, delete-orphan'))


    def __init__(self, name, year, start_day, days_in_month, previous_days, reminders):
        self.name = name
        self.year = year
        self.start_day = start_day
        self.days_in_month = days_in_month
        self.previous_days = previous_days
        self.reminders = reminders

class MonthSchema(ma.Schema):
    class Meta:
        fields = ('id', 'year', 'start_day', 'days_in_month', 'previous_days', 'reminders')
    reminders = ma.Nested(multi_reminder_schema)

month_schema = MonthSchema()
multi_month_schema = MonthSchema(many=True)


# endpoints
@app.route('/month', methods=["GET"])
def get_month(id):
    one_month = db.session.query(Month).filter(Month.id == id).first()
    return jsonify(month_schema.dump(one_month))

@app.route('/months', methods=["GET"])
def get_all_months():
    all_months = db.session.query(Month).all()
    return jsonify(multi_month_schema.dump(all_months))

@app.route('/month/add', methods=["POST"])
def add_month():
    if request.content_type != 'application/json':
        return jsonify('content must be json')
    post_data = request.get_json()

    name = post_data.get('name')
    year = post_data.get('year')
    start_day = post_data.get('start_day')
    days_in_month = post_data.get('days_in_month')
    previous_days = post_data.get('previous_days')

    existing_month_check = db.session.query(Month).filter(Month.name == year).first()
    if existing_month_check is not None:
        return jsonify('that month is already in here')

    new_record = Month(name, year, start_day, days_in_month, previous_days)
    db.session.add(new_record)
    db.commit()

    return jsonify(month_schema.dump(new_record))


@app.route('/months/add', methods=["POST"])
def add_months():
    if request.content_type != 'application/json':
        return jsonify('content must be json')
    post_data = request.get_json()
    data = post_data.get("data")

    new_records = []

    for month in data:
        name = month.get('name')
        year = month.get('year')
        start_day = month.get('start_day')
        days_in_month = month.get('days_in_month')
        previous_days = month.get('previous_days')

        existing_month_check = db.session.query(Month).filter(Month.name == name).filter(Month.year == year).first()
        if existing_month_check is not None:
            return jsonify('that month is already in here')
        else:
            new_record = Month(name, year, start_day, days_in_month, previous_days)
            db.session.add(new_record)
            db.commit()
            new_records.append(new_record)

    return jsonify(multi_month_schema.dump(new_records))

@app.route('/reminders', methods=["GET"])
def get_reminders():
    all_reminders = db.session.query(Reminder).all()
    return jsonify(multi_reminder_schema.dump(all_reminders))
    


# run app
if __name__ == '__main__':
    app.run(debug=True)