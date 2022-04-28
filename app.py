from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)

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




@app.route('month', methods=["GET"])
def get_month(id):
    one_month = db.session.query(Month).filter(Month.id == id).first()
    return jsonify(month_schema.dump(one_month))

@app.route('months', methods=["GET"])
def get_all_months():
    all_months = db.session.query(Month).all()
    return jsonify(multi_month_schema.dump(all_months))

@app.route('month/add', methods=["POST"])
def add_month():
    if request.content_type != 'application/json':
        return jsonify('content must be json')

@app.route('/reminders', methods=["GET"])
def get_reminders():
    all_reminders = db.session.query(Reminder).all()
    return jsonify(multi_reminder_schema.dump(all_reminders))
    



if __name__ == '__main__':
    app.run(debug=True)