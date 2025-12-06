from datetime import datetime, date, timedelta
from functools import wraps

from flask import (
    Flask, render_template, redirect, url_for,
    request, flash, session, make_response
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_mail import Mail, Message
from wtforms import (
    StringField, TextAreaField, BooleanField,
    DateField, TimeField, PasswordField, SubmitField, IntegerField
)
from wtforms.validators import (
    DataRequired, Optional, Email, Length, NumberRange
)
from werkzeug.security import generate_password_hash, check_password_hash
from icalendar import Calendar, Event
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import os
from dotenv import load_dotenv

# Load environment variables from .env file BEFORE importing Config so it can read envs
load_dotenv()

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
mail = Mail(app)

# Only start scheduler in development/local environment
# On Heroku, this runs in a separate worker process
if os.getenv('FLASK_ENV') != 'production':
    scheduler = BackgroundScheduler()
    scheduler.start()
else:
    scheduler = None

# Flask 3 removed before_first_request; database initialization is handled
# via Heroku release phase (see Procfile) and CLI command `flask --app app.py init-db`.

# ==========================
# MODELS
# ==========================

class User(db.Model):
    """
    Both admins and chairpersons.
    - is_admin = True: full access to manage meetings.
    - is_admin = False: regular chairperson account.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(80), nullable=False)  # e.g. "Jeff A."
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    sobriety_days = db.Column(db.Integer, nullable=True)
    agreed_guidelines = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    chair_signups = db.relationship("ChairSignup", back_populates="user")

    @property
    def bp_id(self):
        """Generate Back Porch ID like BP-1001, BP-1002, etc."""
        return f"BP-{1000 + self.id}"

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Meeting(db.Model):
    """
    A single Back Porch online meeting occurrence.
    Example: 'Back Porch Noon Meeting', 2025-12-08, 12:00 PM.
    """
    __tablename__ = "meetings"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)           # format / focus
    zoom_link = db.Column(db.String(500), nullable=True)      # meeting URL
    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=True)
    is_open = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    chair_signup = db.relationship(
        "ChairSignup",
        back_populates="meeting",
        uselist=False,
        cascade="all, delete-orphan"
    )

    @property
    def has_chair(self) -> bool:
        return self.chair_signup is not None


class ChairSignup(db.Model):
    """
    The record representing that a user has committed to chair a meeting.
    """
    __tablename__ = "chair_signups"

    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(
        db.Integer,
        db.ForeignKey("meetings.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    display_name_snapshot = db.Column(db.String(80), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    meeting = db.relationship("Meeting", back_populates="chair_signup")
    user = db.relationship("User", back_populates="chair_signups")


# ==========================
# FORMS
# ==========================

class RegisterForm(FlaskForm):
    display_name = StringField(
        "Name to display (first name & last initial or alias)",
        validators=[DataRequired(), Length(max=80)]
    )
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=6, message="At least 6 characters")]
    )
    sobriety_days = IntegerField(
        "Approx. days sober (optional)",
        validators=[Optional(), NumberRange(min=0, max=100000)]
    )
    agreed_guidelines = BooleanField(
        "I have at least ~90 days sober and am working with a sponsor (suggested), and I have read the chairperson guidelines.",
        validators=[DataRequired(message="Please confirm you have read and agree to the guidelines.")]
    )
    submit = SubmitField("Create Chairperson Account")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class MeetingForm(FlaskForm):
    title = StringField("Meeting Name", validators=[DataRequired(), Length(max=255)])
    description = TextAreaField("Description / Format", validators=[Optional()])
    zoom_link = StringField("Online Meeting Link", validators=[Optional(), Length(max=500)])
    event_date = DateField("Date", validators=[DataRequired()], format="%Y-%m-%d")
    start_time = TimeField("Start Time", validators=[DataRequired()], format="%H:%M")
    end_time = TimeField("End Time (optional)", validators=[Optional()], format="%H:%M")
    is_open = BooleanField("Open for chair sign-ups?", default=True)
    submit = SubmitField("Save Meeting")


class ChairSignupForm(FlaskForm):
    notes = TextAreaField(
        "Notes (optional)",
        validators=[Optional(), Length(max=500)]
    )
    submit = SubmitField("Sign Up to Chair This Meeting")


# ==========================
# AUTH HELPERS
# ==========================

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not get_current_user():
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user or not user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for("index"))
        return view_func(*args, **kwargs)
    return wrapper


# ==========================
# PUBLIC ROUTES
# ==========================

@app.context_processor
def inject_globals():
    return {"current_user": get_current_user()}

@app.route("/")
def index():
    """List upcoming meetings grouped by date for calendar view."""
    today = date.today()
    meetings = (
        Meeting.query
        .filter(Meeting.event_date >= today)
        .order_by(Meeting.event_date.asc(), Meeting.start_time.asc())
        .options(db.joinedload(Meeting.chair_signup).joinedload(ChairSignup.user))
        .all()
    )
    # Group meetings by date
    meetings_by_date = {}
    for m in meetings:
        date_str = m.event_date.strftime('%Y-%m-%d')
        if date_str not in meetings_by_date:
            meetings_by_date[date_str] = []
        meetings_by_date[date_str].append(m)
    return render_template("index.html", meetings_by_date=meetings_by_date)


@app.route("/meeting/<int:meeting_id>", methods=["GET", "POST"])
def meeting_detail(meeting_id):
    """Show a single meeting and allow chair sign-up if open & unclaimed."""
    meeting = Meeting.query.options(db.joinedload(Meeting.chair_signup).joinedload(ChairSignup.user)).get_or_404(meeting_id)
    user = get_current_user()
    form = ChairSignupForm()

    if request.method == "POST" and form.validate_on_submit():
        if not user:
            flash("Please log in or create a chairperson account first.", "warning")
            return redirect(url_for("login", next=request.path))

        if not meeting.is_open:
            flash("This meeting is not currently open for chair sign-ups.", "danger")
        elif meeting.has_chair:
            flash("This meeting already has a chair. Thank you for your willingness!", "danger")
        else:
            signup = ChairSignup(
                meeting_id=meeting.id,
                user_id=user.id,
                display_name_snapshot=user.display_name,
                notes=form.notes.data.strip() if form.notes.data else None,
            )
            db.session.add(signup)
            db.session.commit()
            
            # Schedule reminder email 24 hours before meeting (only in development)
            if scheduler:
                reminder_time = datetime.combine(meeting.event_date, meeting.start_time) - timedelta(hours=24)
                if reminder_time > datetime.now():
                    scheduler.add_job(
                        send_chair_reminder,
                        'date',
                        run_date=reminder_time,
                        args=[meeting.id],
                        id=f"reminder-{meeting.id}",
                        replace_existing=True
                    )
            
            flash("Thank you for chairing this Back Porch meeting!", "success")
            return redirect(url_for("meeting_detail", meeting_id=meeting.id))

    return render_template("meeting_detail.html", meeting=meeting, form=form, user=user)


@app.route("/calendar.ics")
def calendar_ics():
    """Export meetings as iCal calendar feed."""
    meetings = (
        Meeting.query
        .filter(Meeting.event_date >= date.today())
        .order_by(Meeting.event_date.asc(), Meeting.start_time.asc())
        .options(db.joinedload(Meeting.chair_signup).joinedload(ChairSignup.user))
        .all()
    )
    
    cal = Calendar()
    cal.add('prodid', '-//Back Porch Meetings//backporchmeetings.org//')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Back Porch Chairperson Calendar')
    
    for m in meetings:
        event = Event()
        start_dt = datetime.combine(m.event_date, m.start_time)
        end_dt = datetime.combine(m.event_date, m.end_time) if m.end_time else start_dt + timedelta(hours=1)
        
        event.add('summary', m.title)
        event.add('dtstart', start_dt)
        event.add('dtend', end_dt)
        event.add('location', m.zoom_link or 'Online')
        event.add('description', f"{m.description or ''}\n\nChair: {m.chair_signup.display_name_snapshot + ' (' + m.chair_signup.user.bp_id + ')' if m.chair_signup else 'No chair yet'}")
        event.add('url', url_for('meeting_detail', meeting_id=m.id, _external=True))
        event.add('uid', f"meeting-{m.id}@backporchmeetings.org")
        
        cal.add_component(event)
    
    response = make_response(cal.to_ical())
    response.headers['Content-Type'] = 'text/calendar; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=backporch-calendar.ics'
    return response


# ==========================
# AUTH ROUTES
# ==========================

@app.route("/register", methods=["GET", "POST"])
def register():
    if get_current_user():
        flash("You are already logged in.", "info")
        return redirect(url_for("index"))

    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if existing:
            flash("An account with that email already exists.", "danger")
        else:
            user = User(
                display_name=form.display_name.data.strip(),
                email=form.email.data.lower().strip(),
                is_admin=False,
                sobriety_days=form.sobriety_days.data,
                agreed_guidelines=form.agreed_guidelines.data,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            flash("Chairperson account created. Thank you for your service!", "success")
            next_url = request.args.get("next") or url_for("index")
            return redirect(next_url)
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if get_current_user():
        flash("You are already logged in.", "info")
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data):
            session["user_id"] = user.id
            flash("Logged in successfully.", "success")
            next_url = request.args.get("next") or url_for("index")
            return redirect(next_url)
        flash("Invalid email or password.", "danger")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out.", "info")
    return redirect(url_for("index"))


# ==========================
# EMAIL FUNCTIONS
# ==========================

def send_email(to, subject, body):
    """Send an email using Flask-Mail."""
    msg = Message(subject, recipients=[to], body=body)
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False

def send_chair_reminder(meeting_id):
    """Send reminder email to chair 24 hours before meeting."""
    meeting = Meeting.query.get(meeting_id)
    if not meeting or not meeting.chair_signup:
        return
    
    chair = meeting.chair_signup.user
    subject = f"Back Porch Chair Reminder: {meeting.title}"
    body = f"""Dear {chair.display_name},

This is a reminder that you are scheduled to chair the {meeting.title} on {meeting.event_date.strftime('%A, %B %d, %Y')} at {meeting.start_time.strftime('%I:%M %p')}.

Meeting details:
- Date: {meeting.event_date.strftime('%A, %B %d, %Y')}
- Time: {meeting.start_time.strftime('%I:%M %p')}
- Description: {meeting.description or 'N/A'}
- Zoom Link: {meeting.zoom_link or 'Contact group for link'}

Thank you for your service to the Back Porch community!

Back Porch Meetings
"""
    
    send_email(chair.email, subject, body)

def send_open_slot_reminder():
    """Send weekly reminder about open chair slots."""
    tomorrow = date.today() + timedelta(days=1)
    meetings = (
        Meeting.query
        .filter(Meeting.event_date >= tomorrow, Meeting.event_date <= tomorrow + timedelta(days=7))
        .filter(Meeting.is_open == True)
        .filter(Meeting.chair_signup == None)
        .all()
    )
    
    if not meetings:
        return
    
    # Send to all users (or admins could send manually)
    users = User.query.filter_by(is_admin=False).all()
    subject = "Back Porch: Open Chair Positions This Week"
    body = """Dear Back Porch Chairperson,

There are open chair positions available this week. Please visit the chairperson portal to sign up:

"""
    for m in meetings:
        body += f"- {m.title} on {m.event_date.strftime('%A, %B %d')} at {m.start_time.strftime('%I:%M %p')}\n"
    
    body += "\nThank you for your service!\n\nBack Porch Meetings"
    
    for user in users:
        send_email(user.email, subject, body)


# ==========================
# ADMIN ROUTES
# ==========================

@app.route("/admin/meetings")
@admin_required
def admin_meetings():
    meetings = (
        Meeting.query
        .order_by(Meeting.event_date.desc(), Meeting.start_time.desc())
        .all()
    )
    return render_template("admin_meetings.html", meetings=meetings)


@app.route("/admin/diagnostics")
@admin_required
def admin_diagnostics():
    """Quick health diagnostics for DB and mail configuration."""
    engine_url = str(db.engine.url)
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    counts = {}
    for t in tables:
        try:
            counts[t] = db.session.execute(db.text(f"SELECT COUNT(*) AS c FROM `{t}`")).scalar()
        except Exception:
            counts[t] = None

    mail_settings = {
        "MAIL_SERVER": app.config.get("MAIL_SERVER"),
        "MAIL_PORT": app.config.get("MAIL_PORT"),
        "MAIL_USE_TLS": app.config.get("MAIL_USE_TLS"),
        "MAIL_USE_SSL": app.config.get("MAIL_USE_SSL"),
        "MAIL_DEFAULT_SENDER": app.config.get("MAIL_DEFAULT_SENDER"),
        "MAIL_USERNAME_set": bool(app.config.get("MAIL_USERNAME")),
        "MAIL_PASSWORD_set": bool(app.config.get("MAIL_PASSWORD")),
    }

    return render_template(
        "admin_diagnostics.html",
        engine_url=engine_url,
        tables=tables,
        counts=counts,
        mail_settings=mail_settings,
    )


@app.route("/admin/reports/chair-schedule")
@admin_required
def admin_report_chair_schedule():
    """Report: Chair Schedule by date/time with registered name and BP-ID.
    Optional CSV export with ?format=csv
    """
    fmt = request.args.get("format", "html").lower()
    meetings = (
        Meeting.query
        .order_by(Meeting.event_date.asc(), Meeting.start_time.asc())
        .options(db.joinedload(Meeting.chair_signup).joinedload(ChairSignup.user))
        .all()
    )

    # Build rows
    rows = []
    for m in meetings:
        chair_name = m.chair_signup.display_name_snapshot if m.chair_signup else None
        bp_id = m.chair_signup.user.bp_id if (m.chair_signup and m.chair_signup.user) else None
        rows.append({
            "date": m.event_date.strftime('%Y-%m-%d'),
            "weekday": m.event_date.strftime('%A'),
            "start": m.start_time.strftime('%H:%M'),
            "title": m.title,
            "chair_name": chair_name,
            "bp_id": bp_id,
            "is_open": m.is_open and not m.has_chair,
        })

    if fmt == "csv":
        import csv
        from io import StringIO
        si = StringIO()
        writer = csv.DictWriter(si, fieldnames=[
            "date","weekday","start","title","chair_name","bp_id","is_open"
        ])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
        resp = make_response(si.getvalue())
        resp.headers['Content-Type'] = 'text/csv; charset=utf-8'
        resp.headers['Content-Disposition'] = 'attachment; filename=chair_schedule.csv'
        return resp

    # Group by date for HTML
    grouped = {}
    for r in rows:
        grouped.setdefault(r["date"], []).append(r)

    return render_template("admin_chair_schedule.html", grouped=grouped)


@app.route("/admin/meetings/new", methods=["GET", "POST"])
@admin_required
def admin_meeting_new():
    form = MeetingForm()
    if form.validate_on_submit():
        meeting = Meeting(
            title=form.title.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            zoom_link=form.zoom_link.data.strip() if form.zoom_link.data else None,
            event_date=form.event_date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            is_open=form.is_open.data,
        )
        db.session.add(meeting)
        db.session.commit()
        flash("Meeting created.", "success")
        return redirect(url_for("admin_meetings"))
    return render_template("admin_meeting_form.html", form=form, mode="new")


@app.route("/admin/meetings/<int:meeting_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_meeting_edit(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    form = MeetingForm(obj=meeting)

    if form.validate_on_submit():
        meeting.title = form.title.data.strip()
        meeting.description = form.description.data.strip() if form.description.data else None
        meeting.zoom_link = form.zoom_link.data.strip() if form.zoom_link.data else None
        meeting.event_date = form.event_date.data
        meeting.start_time = form.start_time.data
        meeting.end_time = form.end_time.data
        meeting.is_open = form.is_open.data
        db.session.commit()
        flash("Meeting updated.", "success")
        return redirect(url_for("admin_meetings"))

    return render_template("admin_meeting_form.html", form=form, mode="edit", meeting=meeting)


@app.route("/admin/meetings/<int:meeting_id>/delete", methods=["POST"])
@admin_required
def admin_meeting_delete(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    db.session.delete(meeting)
    db.session.commit()
    flash("Meeting deleted.", "info")
    return redirect(url_for("admin_meetings"))


@app.route("/admin/meetings/<int:meeting_id>/clear-chair", methods=["POST"])
@admin_required
def admin_meeting_clear_chair(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    if meeting.chair_signup:
        db.session.delete(meeting.chair_signup)
        db.session.commit()
        flash("Chair signup cleared.", "info")
    else:
        flash("This meeting currently has no chair to clear.", "warning")
    return redirect(url_for("admin_meetings"))


# ==========================
# CLI: init DB + default admin
# ==========================

@app.cli.command("init-db")
def init_db_command():
    """
    Initialize the database and create a default admin user.
    Run with: flask --app app.py init-db
    """
    db.create_all()

    if not User.query.filter_by(email="chair.admin@backporchmeetings.org").first():
        admin = User(
            display_name="Back Porch Admin",
            email="chair.admin@backporchmeetings.org",
            is_admin=True,
            agreed_guidelines=True
        )
        admin.set_password("changeme123")
        db.session.add(admin)
        db.session.commit()
        print("Created default admin: chair.admin@backporchmeetings.org / changeme123")
    else:
        print("Admin already exists.")

    # Schedule weekly open slots reminder (only in development)
    if scheduler:
        scheduler.add_job(
            send_open_slot_reminder,
            CronTrigger(day_of_week='sun', hour=10),
            id='weekly-open-slots',
            replace_existing=True
        )
        print("Scheduled weekly open slots reminder.")

    print("Database initialized.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
