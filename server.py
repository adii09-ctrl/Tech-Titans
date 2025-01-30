from networkx import spanner  # type: ignore
from flask_mail import Mail, Message  # type: ignore
from flask import Flask, jsonify  # type: ignore

app = Flask(__name__)

# Configure SMTP Email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # type: ignore
app.config['MAIL_PORT'] = 587  # type: ignore
app.config['MAIL_USE_TLS'] = True  # type: ignore
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  # type: ignore
app.config['MAIL_PASSWORD'] = 'your-app-password'  # type: ignore # Use App Password
mail = Mail(app)  # type: ignore

def send_email(candidate_email, candidate_name, rank):
    """Send ranking notification to candidates"""
    subject = f"Congratulations, {candidate_name}! Your Resume is Ranked #{rank}"
    body = f"""
    Hi {candidate_name},

    Your resume has been ranked #{rank} for the position you applied for.
    
    Best of luck!
    """

    msg = Message(subject, sender="your-email@gmail.com", recipients=[candidate_email])
    msg.body = body
    mail.send(msg)

@app.route("/notify", methods=["POST"])  # type: ignore
def notify_candidates():
    rankings = spanner.rank_candidates()
    
    # Send email to top-ranked candidates
    for i, (index, score) in enumerate(rankings[0]):
        candidate = spanner.candidates[index]
        send_email(candidate["email"], candidate["name"], i + 1)

    return jsonify({"message": "Emails sent successfully!"}), 200  # type: ignore
