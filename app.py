# CRM Backend (Flask + Twilio + SQLite)
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import uuid
from twilio.rest import Client

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leads.db'
db = SQLAlchemy(app)

# Twilio Config (Set these in Railway Variables)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

class Lead(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    source = db.Column(db.String, nullable=False)
    notes = db.Column(db.String, nullable=True)
    follow_up_date = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "phone": self.phone, "source": self.source, "notes": self.notes, "follow_up_date": self.follow_up_date}

# Initialize database inside app context
with app.app_context():
    db.create_all()

@app.route('/leads', methods=['POST'])
def add_lead():
    data = request.json
    new_lead = Lead(id=str(uuid.uuid4()), name=data['name'], phone=data['phone'], source=data['source'], notes=data.get('notes', ''), follow_up_date=(datetime.utcnow() + timedelta(days=2)).isoformat())
    db.session.add(new_lead)
    db.session.commit()
    return jsonify(new_lead.to_dict()), 201

@app.route('/leads', methods=['GET'])
def get_leads():
    leads = Lead.query.all()
    return jsonify([lead.to_dict() for lead in leads])

@app.route('/send-text', methods=['POST'])
def send_text():
    data = request.json
    to_number = data['to']
    message_body = data['message']
    
    try:
        message = twilio_client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )
        return jsonify({"status": "success", "sid": message.sid})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
