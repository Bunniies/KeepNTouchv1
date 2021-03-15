from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,ValidationError,FileField,RadioField, DateField, IntegerField,TextAreaField, HiddenField
from wtforms.validators import Length,Email,EqualTo,DataRequired,regexp
from models import Student, BusinessPartner, Event
from datetime import date
from flask_wtf.file import FileAllowed
from flask_login import current_user

class Formname(FlaskForm):
    name = StringField('Name:', validators=[DataRequired(), Length(min=2, max=100)])
    usertype = RadioField('You are', choices=[('Student', 'Student'), ('Activity Owner', 'Activity Owner')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    university = StringField('University', validators=[Length(max=50)])

    password = PasswordField('Password', validators=[DataRequired()])
    password_con = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_email(self,email):
        st = Student.query.filter_by(email=email.data).first()
        bp = BusinessPartner.query.filter_by(email=email.data).first()
        if st or bp:
            raise ValidationError('You have been already registerd with this email !')

class formCreateEvent(FlaskForm):
    name = StringField('Name:', validators=[DataRequired(), Length(min=2, max=100)])
    date = DateField('Date: ', default=date.today, validators=[DataRequired()], )
    description = TextAreaField('Description:', validators=[DataRequired(), Length(min=50, max=500)])
    location = StringField('Location:', validators=[DataRequired(), Length(min=3, max=100)])

    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(),Length(min=4,max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class confirmParticipation(FlaskForm):
    event_id = IntegerField('event_id',render_kw={'readonly': True})
    submitC = SubmitField('Confirm Participation')

class deleteParticipation(FlaskForm):
    event_id = IntegerField('event_id', render_kw={'readonly': True})
    submitD = SubmitField('Delete Participation')

class UploadForm(FlaskForm):
    file = FileField('file',validators=[DataRequired()])
    upload=SubmitField('upload')

class UpdateAccount(FlaskForm):
    name = StringField('Name:', validators=[DataRequired(), Length(min=2, max=100)])
    usertype = RadioField('You are', choices=[('Student', 'Student'), ('Activity Owner', 'Activity Owner')])
    university = StringField('University', validators=[Length(max=50)])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    def validate_username(self, name):
        if name.data != current_user.name:
            user = Student.query.filter_by(name=name.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')


    def validate_email(self,email):
        #if email.data != current_user.email:
        st = Student.query.filter_by(email=email.data).first()
        bp = BusinessPartner.query.filter_by(email=email.data).first()
        if st or bp:
            raise ValidationError('You have been already registerd with this email !')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class EditProfileForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
