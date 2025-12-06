from datetime import datetime, date, timedelta
from functools import wraps

from flask import (
    Flask, render_template, redirect, url_for,
    request, flash, session, make_response, jsonify
)
from flask import send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_mail import Mail, Message
from wtforms import (
    StringField, TextAreaField, BooleanField,
    DateField, TimeField, PasswordField, SubmitField, IntegerField, RadioField
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
import calendar
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

# Load environment variables from .env file BEFORE importing Config so it can read envs
load_dotenv()

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
mail = Mail(app)

# Expose a simple asset version for cache-busting static resources
@app.context_processor
def inject_asset_version():
    ver = os.environ.get("ASSET_VERSION", "20251206")
    return {"asset_version": ver}

# Only start scheduler in development/local environment
# On Heroku, this runs in a separate worker process
if os.getenv('FLASK_ENV') != 'production':
    scheduler = BackgroundScheduler()
    scheduler.start()
else:
    scheduler = None
# External resources directory for chairing PDFs (configurable)
EXTERNAL_PDFS_DIR = os.environ.get(
    "EXTERNAL_PDFS_DIR",
    r"C:\\Users\\JefferyAlexander\\Dropbox\\chatbot\\FullSiteNewPages\\assets\\pdfs"
)
SOURCE_MEETINGS_ICS_URL = os.environ.get("SOURCE_MEETINGS_ICS_URL")

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
    gender = db.Column(db.String(10), nullable=True)  # 'male' or 'female'

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
    gender_restriction = db.Column(db.String(10), nullable=True)  # None, 'male', 'female'

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
# IMPORTERS / SYNC
# ==========================

def import_meetings_from_ics(ics_url: str, replace_future: bool = True) -> int:
    """Import meetings from an external iCal URL into our Meeting table.
    If replace_future is True, existing future meetings are removed before import.
    Returns number of meetings imported.
    """
    if not ics_url:
        raise ValueError("ICS URL not provided")
    # Support local filesystem paths in addition to URLs
    data = None
    if ics_url.lower().startswith('file://'):
        try:
            with urlopen(ics_url) as resp:
                data = resp.read()
        except (URLError, HTTPError) as e:
            raise RuntimeError(f"Failed to fetch ICS (file URL): {e}")
    elif os.path.exists(ics_url):
        try:
            with open(ics_url, 'rb') as f:
                data = f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read local ICS file: {e}")
    else:
        try:
            with urlopen(ics_url) as resp:
                data = resp.read()
        except (URLError, HTTPError) as e:
            raise RuntimeError(f"Failed to fetch ICS: {e}")

    try:
        cal = Calendar.from_ical(data)
    except Exception as e:
        raise RuntimeError(f"Invalid ICS content: {e}")

    imported = 0
    if replace_future:
        db.session.query(Meeting).filter(Meeting.event_date >= date.today()).delete()
        db.session.commit()

    for component in cal.walk():
        if component.name != 'VEVENT':
            continue

        # Dates
        dtstart = component.get('dtstart')
        dtend = component.get('dtend')
        if not dtstart:
            continue
        start_val = dtstart.dt
        end_val = dtend.dt if dtend else None
        # Normalize to date + time
        if hasattr(start_val, 'date') and hasattr(start_val, 'time'):
            event_date_val = start_val.date()
            start_time_val = start_val.time()
        else:
            # start_val may be a date
            event_date_val = start_val
            start_time_val = None
        end_time_val = None
        if end_val:
            if hasattr(end_val, 'time'):
                end_time_val = end_val.time()

        title = str(component.get('summary') or 'Back Porch Meeting')
        location = str(component.get('location') or '')
        description = str(component.get('description') or '')

        m = Meeting(
            title=title,
            description=description or None,
            zoom_link=location or None,
            event_date=event_date_val,
            start_time=start_time_val or (datetime.min + timedelta(hours=12)).time(),
            end_time=end_time_val,
            is_open=True,
            gender_restriction=None,
        )
        db.session.add(m)
        imported += 1

    db.session.commit()
    return imported


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
    # Change from approx. days to sobriety date; we'll auto-calc days server-side
    sobriety_date = DateField(
        "Sobriety Date (optional)",
        validators=[Optional()],
        format="%Y-%m-%d"
    )
    agreed_guidelines = BooleanField(
        "I have at least ~90 days sober and am working with a sponsor (suggested), and I have read the chairperson guidelines.",
        validators=[DataRequired(message="Please confirm you have read and agree to the guidelines.")]
    )
    # Gender selection for meeting restrictions
    gender = RadioField(
        "Gender",
        choices=[('male','Male'),('female','Female')],
        validators=[DataRequired(message="Please select your gender for meeting eligibility.")]
    )
    submit = SubmitField("Create Chairperson Account")

class AccessCodeFormMixin:
    from wtforms import StringField
    access_code = StringField("Access Code", validators=[Optional(), Length(max=64)])


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
    from wtforms import SelectField
    gender_restriction = SelectField(
        "Gender Restriction",
        choices=[('','None'),('male','Men only'),('female','Women only')],
        validators=[Optional()],
        default=''
    )
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


@app.route("/chair-resources")
def chair_resources():
    """Chairperson resources page including external PDF references."""
    pdfs = []
    try:
        if os.path.isdir(EXTERNAL_PDFS_DIR):
            for name in sorted(os.listdir(EXTERNAL_PDFS_DIR)):
                if name.lower().endswith('.pdf') and not name.startswith('.'):
                    pdfs.append({
                        'name': name,
                        'url': url_for('serve_pdf', filename=name)
                    })
    except Exception:
        pdfs = []
    return render_template("chair_resources.html", pdfs=pdfs)

@app.route('/resources/pdfs/<path:filename>')
def serve_pdf(filename):
    # Only allow .pdf files from the configured directory
    if not filename.lower().endswith('.pdf'):
        return "Not allowed", 403
    if not os.path.isdir(EXTERNAL_PDFS_DIR):
        return "Resources folder not found", 404
    return send_from_directory(EXTERNAL_PDFS_DIR, filename, as_attachment=False)


@app.route("/meetings/today")
def meetings_today():
    """Public page listing today's meetings with time, title, and chair name."""
    today = date.today()
    meetings = (
        Meeting.query
        .filter(Meeting.event_date == today)
        .order_by(Meeting.start_time.asc())
        .options(db.joinedload(Meeting.chair_signup).joinedload(ChairSignup.user))
        .all()
    )
    return render_template("today_meetings.html", meetings=meetings, today=today)


@app.route("/calendar")
def calendar_view():
    """Monthly calendar view showing meeting title, host, and time per day."""
    # Determine month to show from query params, default to current month
    today = date.today()
    year = int(request.args.get("year", today.year))
    month = int(request.args.get("month", today.month))
    q = (request.args.get("q", "") or "").strip().lower()

    # Get all meetings for the month
    start_date = date(year, month, 1)
    # Compute last day of month
    _, last_day = calendar.monthrange(year, month)
    end_date = date(year, month, last_day)

    meetings = (
        Meeting.query
        .filter(Meeting.event_date >= start_date, Meeting.event_date <= end_date)
        .order_by(Meeting.event_date.asc(), Meeting.start_time.asc())
        .options(db.joinedload(Meeting.chair_signup).joinedload(ChairSignup.user))
        .all()
    )

    # Apply simple search filter (title or chair name)
    if q:
        def _matches(m):
            title_match = q in (m.title or "").lower()
            chair_name = (
                m.chair_signup.display_name_snapshot if m.chair_signup else ""
            )
            chair_match = q in chair_name.lower()
            return title_match or chair_match
        meetings = [m for m in meetings if _matches(m)]

    # Map meetings by date
    meetings_by_date = {}
    for m in meetings:
        meetings_by_date.setdefault(m.event_date, []).append(m)

    # Build weeks for the month
    cal = calendar.Calendar(firstweekday=6)  # Sunday start
    weeks = []
    for week in cal.monthdatescalendar(year, month):
        week_cells = []
        for d in week:
            in_month = d.month == month
            week_cells.append({
                "date": d if in_month else None,  # hide out-of-month day number
                "in_month": in_month,
                "meetings": meetings_by_date.get(d, []) if in_month else [],
            })
        weeks.append(week_cells)

    # Previous/next month links
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1
    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_month = 1
        next_year += 1

    return render_template(
        "calendar.html",
        year=year,
        month=month,
        month_name=calendar.month_name[month],
        weeks=weeks,
        prev_year=prev_year,
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month,
        today=today,
        q=(request.args.get("q", "") or ""),
        allow_nav=bool(get_current_user()),
    )


@app.route("/calendar/display")
def calendar_display():
    """Read-only display calendar: always shows current month, no navigation."""
    today = date.today()
    year = today.year
    month = today.month

    # Build month data (reuse logic from calendar_view)
    start_date = date(year, month, 1)
    _, last_day = calendar.monthrange(year, month)
    end_date = date(year, month, last_day)

    meetings = (
        Meeting.query
        .filter(Meeting.event_date >= start_date, Meeting.event_date <= end_date)
        .order_by(Meeting.event_date.asc(), Meeting.start_time.asc())
        .options(db.joinedload(Meeting.chair_signup).joinedload(ChairSignup.user))
        .all()
    )

    meetings_by_date = {}
    for m in meetings:
        meetings_by_date.setdefault(m.event_date, []).append(m)

    cal = calendar.Calendar(firstweekday=6)
    weeks = []
    for week in cal.monthdatescalendar(year, month):
        week_cells = []
        for d in week:
            in_month = d.month == month
            week_cells.append({
                "date": d if in_month else None,
                "in_month": in_month,
                "meetings": meetings_by_date.get(d, []) if in_month else [],
            })
        weeks.append(week_cells)

    # prev/next computed but not shown
    prev_month = month - 1
    prev_year = year if prev_month != 0 else year - 1
    if prev_month == 0:
        prev_month = 12
    next_month = month + 1
    next_year = year if next_month != 13 else year + 1
    if next_month == 13:
        next_month = 1

    return render_template(
        "calendar.html",
        year=year,
        month=month,
        month_name=calendar.month_name[month],
        weeks=weeks,
        prev_year=prev_year,
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month,
        today=today,
        q="",
        allow_nav=False,
    )


@app.route("/calendar/ics")
def calendar_month_ics():
    """Export meetings for a specific month as iCal (.ics) file."""
    today = date.today()
    year = int(request.args.get("year", today.year))
    month = int(request.args.get("month", today.month))

    start_date = date(year, month, 1)
    _, last_day = calendar.monthrange(year, month)
    end_date = date(year, month, last_day)

    meetings = (
        Meeting.query
        .filter(Meeting.event_date >= start_date, Meeting.event_date <= end_date)
        .order_by(Meeting.event_date.asc(), Meeting.start_time.asc())
        .options(db.joinedload(Meeting.chair_signup).joinedload(ChairSignup.user))
        .all()
    )

    cal = Calendar()
    cal.add('prodid', '-//Back Porch Meetings//backporchmeetings.org//')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', f'Back Porch Chairperson Calendar - {calendar.month_name[month]} {year}')

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
    response.headers['Content-Disposition'] = f'attachment; filename=backporch-calendar-{year}-{month}.ics'
    return response


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
    # Registration feature gate
    if not app.config.get('REGISTRATION_ENABLED', True):
        flash("Registration is currently disabled. Please contact the admin.", "warning")
        return redirect(url_for("index"))
    if get_current_user():
        flash("You are already logged in.", "info")
        return redirect(url_for("index"))

    form = RegisterForm()
    if form.validate_on_submit():
        # Enforce access code(s) if configured
        provided_code = (request.form.get('access_code') or '').strip()
        required_code = app.config.get('REGISTRATION_ACCESS_CODE')
        codes_list_raw = app.config.get('REGISTRATION_ACCESS_CODES')  # optional comma-separated list
        if required_code or codes_list_raw:
            valid_codes = set()
            if required_code:
                valid_codes.add(required_code.strip())
            if codes_list_raw:
                for c in str(codes_list_raw).split(','):
                    c = c.strip()
                    if c:
                        valid_codes.add(c)
            if provided_code not in valid_codes:
                flash("Invalid access code.", "danger")
                access_codes_configured = True
                return render_template("register.html", form=form, access_codes_configured=access_codes_configured)
        existing = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if existing:
            flash("An account with that email already exists.", "danger")
        else:
            # Compute sobriety days from provided sobriety_date (optional)
            sob_days = None
            if form.sobriety_date.data:
                try:
                    d0 = form.sobriety_date.data
                    delta = (date.today() - d0).days
                    sob_days = max(0, delta)
                except Exception:
                    sob_days = None
            user = User(
                display_name=form.display_name.data.strip(),
                email=form.email.data.lower().strip(),
                is_admin=False,
                sobriety_days=sob_days,
                agreed_guidelines=form.agreed_guidelines.data,
                gender=form.gender.data,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            flash("Chairperson account created. Thank you for your service!", "success")
            next_url = request.args.get("next") or url_for("index")
            return redirect(next_url)
    # Provide flag to template so it can lock inputs until a code is entered
    access_codes_configured = bool(app.config.get('REGISTRATION_ACCESS_CODE') or app.config.get('REGISTRATION_ACCESS_CODES'))
    # Pass optional PDF names for responsibilities and protocol
    responsibilities_pdf = os.environ.get('CHAIR_RESPONSIBILITIES_PDF', 'Chairperson Responsibilities.pdf')
    protocol_pdf = os.environ.get('MEETING_PROTOCOL_PDF', 'Meeting Protocol.pdf')
    try:
        return render_template(
            "register.html",
            form=form,
            access_codes_configured=access_codes_configured,
            responsibilities_pdf=responsibilities_pdf,
            protocol_pdf=protocol_pdf,
        )
    except Exception as e:
        import traceback
        print("Register page render error:")
        print(traceback.format_exc())
        return f"Register page error: {e}", 500


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
# USER PAGES (secured)
# ==========================

@app.route("/dashboard")
@login_required
def dashboard():
    user = get_current_user()
    # Meetings user has claimed
    my_meetings = (
        Meeting.query
        .join(ChairSignup, ChairSignup.meeting_id == Meeting.id)
        .filter(ChairSignup.user_id == user.id)
        .order_by(Meeting.event_date.asc(), Meeting.start_time.asc())
        .all()
    )
    return render_template("dashboard.html", user=user, my_meetings=my_meetings)


class ProfileForm(FlaskForm):
    display_name = StringField("Display Name", validators=[DataRequired(), Length(max=80)])
    from wtforms import RadioField
    gender = RadioField(
        "Gender",
        choices=[('male','Male'),('female','Female')],
        validators=[Optional()]
    )
    submit = SubmitField("Save Changes")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = get_current_user()
    form = ProfileForm(obj=user)
    if form.validate_on_submit():
        user.display_name = form.display_name.data.strip()
        user.gender = form.gender.data or None
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("dashboard"))
    return render_template("profile.html", form=form)


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
    subject = f"Heads up! You're hosting tomorrow — {meeting.title}"
    body = f"""Hi {chair.display_name},

Heads up — you're scheduled to host tomorrow. Here are the details:

• Meeting: {meeting.title}
• Date: {meeting.event_date.strftime('%A, %B %d, %Y')}
• Time: {meeting.start_time.strftime('%I:%M %p')}
• Description: {meeting.description or 'N/A'}
• Zoom Link: {meeting.zoom_link or 'Contact group for link'}

Thanks for serving the Back Porch community!

— Back Porch Meetings
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

def send_day_of_chair_reminders(run_date: date = None):
    """Send reminder emails to chairs on the morning of their scheduled meeting day.
    If run_date is provided, use it; otherwise, use today's date.
    """
    target_day = run_date or date.today()
    meetings = (
        Meeting.query
        .filter(Meeting.event_date == target_day)
        .options(db.joinedload(Meeting.chair_signup).joinedload(ChairSignup.user))
        .all()
    )

    sent = 0
    for m in meetings:
        if not m.chair_signup or not m.chair_signup.user:
            continue
        chair = m.chair_signup.user
        subject = f"Heads up! You're hosting today — {m.title}"
        body = f"""Hi {chair.display_name},

    Heads up — you're scheduled to host today! Here are the details:

    • Meeting: {m.title}
    • Date: {m.event_date.strftime('%A, %B %d, %Y')}
    • Time: {m.start_time.strftime('%I:%M %p')}
    • Description: {m.description or 'N/A'}
    • Zoom Link: {m.zoom_link or 'Contact group for link'}

    Thanks for stepping up to serve the Back Porch community!

    — Back Porch Meetings
    """
        if send_email(chair.email, subject, body):
            sent += 1

    return sent


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
    return render_template("admin_meetings.html", meetings=meetings, ics_source=SOURCE_MEETINGS_ICS_URL)


@app.route("/admin/import-ics")
@admin_required
def admin_import_ics():
    """Admin endpoint to import meetings from configured ICS URL."""
    url = SOURCE_MEETINGS_ICS_URL
    if not url:
        flash("ICS source URL is not configured.", "warning")
        return redirect(url_for('admin_meetings'))
    try:
        count = import_meetings_from_ics(url, replace_future=True)
        flash(f"Imported {count} meetings from ICS.", "success")
    except Exception as e:
        flash(f"ICS import failed: {e}", "danger")
    return redirect(url_for('admin_meetings'))


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
        ics_source=SOURCE_MEETINGS_ICS_URL,
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


@app.route("/admin/reports/monthly-pdf")
@admin_required
def admin_monthly_pdf():
    """Generate a monthly PDF report listing meetings chronologically with date, time, chair name, and title."""
    today = date.today()
    year = int(request.args.get("year", today.year))
    month = int(request.args.get("month", today.month))

    # Get all meetings in month
    start_date = date(year, month, 1)
    _, last_day = calendar.monthrange(year, month)
    end_date = date(year, month, last_day)
    meetings = (
        Meeting.query
        .filter(Meeting.event_date >= start_date, Meeting.event_date <= end_date)
        .order_by(Meeting.event_date.asc(), Meeting.start_time.asc())
        .options(db.joinedload(Meeting.chair_signup).joinedload(ChairSignup.user))
        .all()
    )

    # Build PDF in memory
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    title = f"Back Porch Monthly Report - {calendar.month_name[month]} {year}"
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 1*inch, title)
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, height - 1.25*inch, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} ")

    y = height - 1.6*inch
    line_height = 0.22 * inch

    # Table header
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, y, "Date")
    c.drawString(2.5*inch, y, "Time")
    c.drawString(4*inch, y, "Chair")
    c.drawString(6*inch, y, "Meeting")
    y -= line_height
    c.setFont("Helvetica", 10)

    if not meetings:
        c.drawString(1*inch, y, "No meetings scheduled for this month.")
    else:
        for m in meetings:
            # Check page break
            if y < 1*inch:
                c.showPage()
                y = height - 1*inch
                c.setFont("Helvetica-Bold", 11)
                c.drawString(1*inch, y, "Date")
                c.drawString(2.5*inch, y, "Time")
                c.drawString(4*inch, y, "Chair")
                c.drawString(6*inch, y, "Meeting")
                y -= line_height
                c.setFont("Helvetica", 10)

            date_str = m.event_date.strftime('%Y-%m-%d (%a)')
            time_str = m.start_time.strftime('%I:%M %p') + (f" - {m.end_time.strftime('%I:%M %p')}" if m.end_time else "")
            chair_str = (
                f"{m.chair_signup.display_name_snapshot} ({m.chair_signup.user.bp_id})"
                if m.chair_signup and m.chair_signup.user else "No chair yet"
            )
            title_str = m.title

            c.drawString(1*inch, y, date_str)
            c.drawString(2.5*inch, y, time_str)
            c.drawString(4*inch, y, chair_str[:28])  # prevent overflow
            c.drawString(6*inch, y, title_str[:28])
            y -= line_height

    c.showPage()
    c.save()
    pdf = buf.getvalue()
    buf.close()

    resp = make_response(pdf)
    resp.headers['Content-Type'] = 'application/pdf'
    resp.headers['Content-Disposition'] = (
        f"attachment; filename=monthly_report_{year}_{month}.pdf"
    )
    return resp


@app.route("/admin/reports/monthly")
@admin_required
def admin_monthly_html():
    """Printable HTML monthly report mirroring the PDF contents."""
    today = date.today()
    year = int(request.args.get("year", today.year))
    month = int(request.args.get("month", today.month))

    start_date = date(year, month, 1)
    _, last_day = calendar.monthrange(year, month)
    end_date = date(year, month, last_day)

    meetings = (
        Meeting.query
        .filter(Meeting.event_date >= start_date, Meeting.event_date <= end_date)
        .order_by(Meeting.event_date.asc(), Meeting.start_time.asc())
        .options(db.joinedload(Meeting.chair_signup).joinedload(ChairSignup.user))
        .all()
    )

    return render_template(
        "admin_monthly.html",
        year=year,
        month=month,
        month_name=calendar.month_name[month],
        meetings=meetings,
        today=today,
    )


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
            gender_restriction=form.gender_restriction.data or None,
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
        meeting.gender_restriction = form.gender_restriction.data or None
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
# API: Interactive Calendar
# ==========================

@app.route("/api/day-meetings")
def api_day_meetings():
    """Return JSON list of meetings for a given date (YYYY-MM-DD)."""
    date_str = request.args.get("date")
    try:
        target = datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        return jsonify({"error": "Invalid date"}), 400

    meetings = (
        Meeting.query
        .filter(Meeting.event_date == target)
        .order_by(Meeting.start_time.asc())
        .options(db.joinedload(Meeting.chair_signup).joinedload(ChairSignup.user))
        .all()
    )
    user = get_current_user()
    data = []
    for m in meetings:
        eligible = True
        if m.gender_restriction in ('male','female'):
            eligible = bool(user and user.gender == m.gender_restriction)
        data.append({
            "id": m.id,
            "title": m.title,
            "time": m.start_time.strftime('%I:%M %p'),
            "has_chair": bool(m.chair_signup),
            "chair_name": m.chair_signup.user.display_name if (m.chair_signup and m.chair_signup.user) else None,
            "is_open": m.is_open and not m.chair_signup,
            "eligible": eligible,
            "detail_url": url_for('meeting_detail', meeting_id=m.id),
        })
    return jsonify({"date": date_str, "meetings": data})


@app.route("/api/meetings/<int:meeting_id>/claim", methods=["POST"])
def api_meeting_claim(meeting_id):
    """Claim chairing for an open meeting. Requires login."""
    user = get_current_user()
    if not user:
        return jsonify({"error": "login_required"}), 401

    meeting = Meeting.query.options(db.joinedload(Meeting.chair_signup)).get_or_404(meeting_id)
    if not meeting.is_open:
        return jsonify({"error": "not_open"}), 400
    if meeting.chair_signup:
        return jsonify({"error": "already_has_chair"}), 400

    # Enforce gender restriction if set
    if meeting.gender_restriction in ('male','female'):
        if not user.gender:
            return jsonify({"error": "gender_required"}), 400
        if user.gender != meeting.gender_restriction:
            return jsonify({"error": "not_eligible"}), 403

    signup = ChairSignup(
        meeting_id=meeting.id,
        user_id=user.id,
        display_name_snapshot=user.display_name,
        notes=None,
    )
    db.session.add(signup)
    db.session.commit()

    return jsonify({
        "ok": True,
        "meeting_id": meeting.id,
        "chair_name": user.display_name,
    })


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


@app.cli.command("upgrade-schema")
def upgrade_schema_command():
    """
    Upgrade DB schema to add gender columns if they don't exist.
    Intended for MySQL; uses ALTER TABLE guarded by information_schema checks.
    Run with: flask --app app.py upgrade-schema
    """
    engine = db.engine
    conn = engine.connect()
    inspector = db.inspect(engine)

    # Add users.gender if missing
    if 'users' in inspector.get_table_names():
        cols = [c['name'] if isinstance(c, dict) else c['name'] for c in inspector.get_columns('users')]
        if 'gender' not in cols:
            try:
                conn.execute(db.text("ALTER TABLE users ADD COLUMN gender VARCHAR(10) NULL"))
                print("Added users.gender")
            except Exception as e:
                print(f"Skipped adding users.gender: {e}")

    # Add meetings.gender_restriction if missing
    if 'meetings' in inspector.get_table_names():
        cols = [c['name'] if isinstance(c, dict) else c['name'] for c in inspector.get_columns('meetings')]
        if 'gender_restriction' not in cols:
            try:
                conn.execute(db.text("ALTER TABLE meetings ADD COLUMN gender_restriction VARCHAR(10) NULL"))
                print("Added meetings.gender_restriction")
            except Exception as e:
                print(f"Skipped adding meetings.gender_restriction: {e}")

    conn.close()
    print("Schema upgrade complete.")


@app.cli.command("import-ics")
def import_ics_command():
    """Import meetings from ICS URL defined in env var SOURCE_MEETINGS_ICS_URL.
    Run with: flask --app app.py import-ics
    """
    url = SOURCE_MEETINGS_ICS_URL
    if not url:
        print("SOURCE_MEETINGS_ICS_URL is not set.")
        return
    try:
        count = import_meetings_from_ics(url, replace_future=True)
        print(f"Imported {count} meetings from ICS.")
    except Exception as e:
        print(f"Import failed: {e}")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
