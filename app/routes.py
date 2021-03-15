import os 
from flask import render_template, redirect, url_for, flash, request, session
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import and_
import secrets
from PIL import Image

from app import app, db, bcrypt
from app.forms import Formname, formCreateEvent, LoginForm, confirmParticipation, deleteParticipation, UploadForm, UpdateAccount, EmptyForm, EditProfileForm
from app.models import Student, Event, BusinessPartner, partecipation
import forms

@app.before_first_request
def setup_all():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():

    confirmParticipation = forms.confirmParticipation()
    deleteParticipation = forms.deleteParticipation()

    if "submitD" in request.form and deleteParticipation.validate_on_submit():
        event_id = deleteParticipation.event_id.data
        event = Event.query.filter_by(id=event_id).first()
        student = Student.query.filter_by(id=session.get('id')).first()
        event.numofPeople += -1
        student.partecipations.remove(event)
        db.session.commit()

        return redirect('home')
    elif "submitC" in request.form and confirmParticipation.validate_on_submit():
        # add user to the list of participants
        event_id = confirmParticipation.event_id.data
        event = Event.query.filter_by(id=event_id).first()
        student = Student.query.filter_by(id=session.get('id')).first()

        if not Student.query.join(partecipation).join(Event).filter( (partecipation.c.student_id == student.id) & (partecipation.c.event_id == event.id)).first():
            event.numofPeople += 1

        student.partecipations.append(event)
        db.session.add(student)
        db.session.add(event)
        db.session.commit()

        return redirect('home')

    if current_user.is_authenticated:
        #events=Event.query.filter_by().all()
        #return render_template('index.html', events=events, confirmParticipation=confirmParticipation, deleteParticipation=deleteParticipation, partecipation=partecipation, Student = Student, Event=Event, BPs = BusinessPartner, and_=and_)
        if Student.query.filter_by(email=current_user.email).first():  ## if student then show the wall
            events=Event.query.all()
            return render_template('index.html', events=events, confirmParticipation=confirmParticipation, deleteParticipation=deleteParticipation, partecipation=partecipation, Student = Student, Event=Event, BPs = BusinessPartner, and_=and_)
        else: # if bp show its own events
            events = Event.query.filter_by(bp_id=session.get('id'))
            return render_template('index.html', events=events, BPs = BusinessPartner)
          
    else:
        return redirect('login')


@app.route("/upload",methods=["GET","POST"])
def upload():
    if session.get('id'):
        if not os.path.exists('static/'+ str(session.get('id'))):
            os.makedirs('static/'+ str(session.get('id')))
        file_url = os.listdir('static/'+ str(session.get('id')))
        file_url = [ str(session.get('id')) +"/"+ file for file in file_url]
        formupload = UploadForm()
        print session.get('email')
        if formupload.validate_on_submit():
            filename = photos.save(formupload.file.data,name=str(session.get('id'))+'.jpg',folder=str(session.get('id')))
            file_url.append(filename)
        return render_template("upload.html",formupload=formupload,filelist=file_url) # ,filelist=file_url
    else:
       return redirect('login')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register",methods=['GET','POST'])
def register():
    formpage=Formname()

    if formpage.validate_on_submit():
        password_1 = bcrypt.generate_password_hash(formpage.password.data).encode('utf-8')

        if formpage.usertype.data=="Student":
             reg=Student(name=formpage.name.data,
                email=formpage.email.data,
                password=password_1,
                university=formpage.university.data ) #role=Role.query.filter_by(name='Student'))
        elif formpage.usertype.data=="Activity Owner":
            reg=BusinessPartner(
                name=formpage.name.data,
                email=formpage.email.data,
                password=password_1
            )
        db.session.add(reg)
        db.session.commit()
        try:
            sendmail(email=formpage.email.data, subject='Welcome onboard!', user=formpage.name.data)
        except:
            print "Some error with the given mail"
        return redirect(url_for('home'))  #TODO create an html page informing the user about success of his registration to render after it
    return render_template('register.html', formpage = formpage , title='Register Page')

@app.route("/login",methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    formpage=LoginForm()
    if formpage.validate_on_submit():
        # TODO make login possible also for BPs
        st=Student.query.filter_by(email=formpage.email.data).first()
        login_user(st)
        bp = BusinessPartner.query.filter_by(email=formpage.email.data).first()
        if st and bcrypt.check_password_hash(st.password,formpage.password.data):
            session['email']=st.email
            session['name']=st.name
            session['uni']=st.university
            session['id']=st.id
            session['student']=True
        elif bp and bcrypt.check_password_hash(bp.password,formpage.password.data):
            session['email']=bp.email
            session['name']=bp.name
            session['id']=bp.id
            session['student'] = False

    return render_template('login.html', formpage = formpage,
                           email=session.get('email',False) ,
                           title='Login Page')



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route("/createevent",methods=['GET','POST'])
def createEvent():
    formpage=formCreateEvent()

    if formpage.validate_on_submit():
        reg = Event(
            name=formpage.name.data,
            date=formpage.date.data,
            bp_id=session.get('id'),
            description=formpage.description.data,
            numofPeople=0,
            location=formpage.location.data
        )

        db.session.add(reg)
        db.session.commit()
        # sendmail(email=formpage.email.data, user=formpage.name.data, subject='Welcome onboard!') #if u want TODO send a mail when event is created successfully
        return redirect(url_for('home'))  # btw the BP should see the new event on its wall
    #if BP then ok
    if session.get('student') == False:
        return render_template('createevent.html', formpage = formpage , title='Create new Event')
    elif session.get('student') == True:
        return render_template('youcannot.html')
    else:
        return redirect('login')
    #if a student then you can't

def save_picture(form_picture):
    random_hex = secrets.token_hex(16)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateAccount()
    eform=EmptyForm()
    if current_user.is_authenticated:
        st = Student.query.filter_by(email=current_user.email).first_or_404()
        if form.validate_on_submit():
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.image_file = picture_file
            current_user.name = form.name.data 
            db.session.commit()
            flash('Your account has been updated', 'success')
            return redirect(url_for('profile'))
        elif request.method =='GET':
            form.name.data = current_user.name
        image_file = url_for('static', filename='profilepics/' + current_user.image_file)
        return render_template('profile.html',student=st, form=form, image_file=image_file, eform=eform)
    else:
        return redirect('login')


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.name = form.name.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/follow/<name>', methods=['POST'])
@login_required
def follow(name):
    form = EmptyForm()
    if form.validate_on_submit():
        user = Student.query.filter_by(name=name).first()
        if user is None:
            flash('User {} not found.'.format(name))
            return redirect(url_for('profile'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('profile'))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(name))
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('profile'))


@app.route('/unfollow/<name>', methods=['POST'])
@login_required
def unfollow(name):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=name).first()
        if user is None:
            flash('User {} not found.'.format(name))
            return redirect(url_for('profile'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('profile'))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(name))
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('profile'))


@app.route("/map")
def map():
    return render_template("map.html")




########


def send_mail(to,subject,template,**kwargs):
    msg=Message(subject,recipients=[to],sender=app.config['MAIL_USERNAME'])
    msg.body= render_template(template + '.txt',**kwargs)
    msg.html= render_template(template + '.html',**kwargs)
    mailobject.send(msg)


class mailClass():

    template = "mail.html"
    sender = app.config['MAIL_USERNAME']
    subject = ""
    toList = []
    def send(self,**kwargs):
        msg=Message(subject=self.subject,recipients=self.toList,sender=self.sender)
        msg.html=render_template(self.template,**kwargs)
        mailobject.send(msg)


def sendmail(**kwargs):

    mailc=mailClass()
    mailc.toList=[kwargs['email']]
    mailc.subject=[kwargs['subject']]
    mailc.send(user=kwargs['user'])

    #print "mail has been send"
    return True

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

'''
if __name__ == '__main__':
    app.run(debug=True)
'''