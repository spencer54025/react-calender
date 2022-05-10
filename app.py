from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
# import os

app = Flask(__name__)
CORS(app)

# basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://oixpyvaredcopq:c7874173fa292e513d5176bf8517529ba0b8b22906f72caa63db61961a65a10f@ec2-107-22-238-112.compute-1.amazonaws.com:5432/db393lvqkgtet0"

db = SQLAlchemy(app)
ma = Marshmallow(app)


# month class and schema
class Month(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    start_day = db.Column(db.Integer, nullable=False)
    days_in_month = db.Column(db.Integer, nullable=False)
    previous_days = db.Column(db.Integer, nullable=False)
    reminders = db.relationship('Reminder', backref='month', cascade='all, delete, delete-orphan')


    def __init__(self, name, year, start_day, days_in_month, previous_days):
        self.name = name
        self.year = year
        self.start_day = start_day
        self.days_in_month = days_in_month
        self.previous_days = previous_days


# reminder class and schema
class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    date = db.Column(db.Integer, nullable=False)
    month_id = db.Column(db.Integer, db.ForeignKey('month.id'), nullable=False)

    def __init__(self, text, date, month_id):
        self.text = text
        self.date = date
        self.month_id = month_id

class ReminderSchema(ma.Schema):
    class Meta:
        fields = ('id', 'date', 'month_id', 'text')

reminder_schema = ReminderSchema()
multi_reminder_schema = ReminderSchema(many=True)


class MonthSchema(ma.Schema):
    class Meta:
        fields = ('id', 'year', 'start_day', 'days_in_month', 'previous_days', 'reminders', 'name')
    reminders = ma.Nested(multi_reminder_schema)

month_schema = MonthSchema()
multi_month_schema = MonthSchema(many=True)


# reminder endpoints
@app.route('/reminder/add', methods=["POST"])
def add_reminder():
    if request.content_type != 'application/json':
        return jsonify('content must be json')
    post_data = request.get_json()

    text = post_data.get('text')
    date = post_data.get('date')
    month_id = post_data.get('month_id')

    existing_reminder_check = db.session.query(Reminder).filter(Reminder.date == date).filter(month_id == month_id).first()
    if existing_reminder_check is not None:
        return jsonify('that reminder is already in here')

    new_record = Reminder(text, date, month_id)
    db.session.add(new_record)
    db.session.commit()

    return jsonify(reminder_schema.dump(new_record))

@app.route('/reminders', methods=["GET"])
def get_reminders():
    all_reminders = db.session.query(Reminder).all()
    return jsonify(multi_reminder_schema.dump(all_reminders))

@app.route('/reminder/<month_id>/<date>', methods=["GET"])
def get_reminder(month_id, date):
    reminder = db.session.query(Reminder).filter(Reminder.month_id == month_id).filter(Reminder.date == date).first()
    return jsonify(reminder_schema.dump(reminder))

@app.route('/reminder/update/<month_id>/<date>', methods=["PUT"])
def update_reminder(month_id, date):
    if request.content_type != 'application/json':
        return jsonify('put that as json')
    put_data = request.get_json()
    text = put_data.get('text')
    
    reminder_to_update = db.session.query(Reminder).filter(Reminder.month_id == month_id).filter(Reminder.date == date).first()
    
    reminder_to_update.text = text
    db.session.commit()

    return jsonify(reminder_schema.dump(reminder_to_update))

@app.route('/reminder/delete/<month_id>/<date>', methods=["GET"])
def delete_reminder(month_id, date):
    reminder_delete = db.session.query(Reminder).filter(Reminder.month_id == month_id).filter(Reminder.date == date).first()
    db.session.delete(reminder_delete)
    db.session.commit()
    return jsonify('that reminder was deleted, try not to add useless info again')


# month endpoints
@app.route('/month/delete/<id>', methods=["DELETE"])
def delete_month(id):
    month_delete = db.session.query(Month).filter(Month.id == id).first()
    db.session.delete(month_delete)
    db.session.commit()
    return jsonify('that month was deleted, try not to add useless info again')
    

@app.route('/month/update/<id>', methods=["PUT"])
def update_month(id):
    if request.content_type != 'application/json':
        return jsonify('put that as json')
    put_data = request.get_json()
    name = put_data.get('name')
    year = put_data.get('year')
    start_day = put_data.get('start_day')
    days_in_month = put_data.get('days_in_month')
    previous_days = put_data.get('previous_days')
    reminders = put_data.get('reminders')
    
    month_to_update = db.session.query(Month).filter(Month.id == id).first()

    if name != None:
        month_to_update.name = name
    if year != None:
        month_to_update.year = year
    if start_day != None:
        month_to_update.start_day = start_day
    if days_in_month != None:
        month_to_update.days_in_month = days_in_month
    if previous_days != None:
        month_to_update.previous = previous_days
    if reminders != None:
        month_to_update.reminders = reminders
    
    db.session.commit()
    return jsonify(month_schema.dump(month_to_update))

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
# 
        existing_month_check = db.session.query(Month).filter(Month.name == name).filter(Month.year == year).first()
        if existing_month_check is not None:
            return jsonify('that month is already in here')
        else:
            new_record = Month(name, year, start_day, days_in_month, previous_days)
            db.session.add(new_record)
            db.session.commit()
            new_records.append(new_record)

    return jsonify(multi_month_schema.dump(new_records))


@app.route('/month/<id>', methods=["GET"])
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
    db.session.commit()

    return jsonify(month_schema.dump(new_record))

@app.route('/month/<year>/<name>', methods=["GET"])
def month_by_year(year, name):
     month = db.session.query(Month).filter(Month.year == year).filter(Month.name == name).first()
     return jsonify(month_schema.dump(month))



# run app
if __name__ == '__main__':
    app.run(debug=True)