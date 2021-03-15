from app import app, db
from app.models import Student, BusinessPartner, Event

@app.shell_context_processor
def make_shell_context():
    return{'db':db, 'Student':Student, 'BusinessPartner':BusinessPartner, 'Event':Event}
    