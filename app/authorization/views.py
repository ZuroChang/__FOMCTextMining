from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required
from . import authorization
from .. import db
from ..models import User, Permission
from .forms import LoginForm, RegistrationForm, ManagementForm




@authorization.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next_ = request.args.get('next')
            if next_ is None or not next_.startswith('/'):
                next_ = url_for('main.index')
            return redirect(next_)
        flash('Invalid email or password.')
    return render_template('authorization/login.html', form=form)


@authorization.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@authorization.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    name=form.username.data,
                    password=form.password.data,
                    role_id=2)
        db.session.add(user)
        db.session.commit()

        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('authorization.login'))
    return render_template('authorization/register.html', form=form)

@authorization.route('/management', methods=['GET', 'POST'])
def manage():
    form = ManagementForm()
    users = User.query.all()
    
    if form.validate_on_submit():
        if form.function.data=='Pending':
            return redirect(url_for('authorization.manage'))
        
        user=User.query.filter_by(id=form.id_.data).first()
        if form.function.data=='Update':
            user.name=form.username.data
            user.email=form.email.data.lower()
            user.role_id=[entry[1] for entry in Permission 
                          if entry[0]==form.role.data][0]
            
            db.session.add(user)
        elif form.function.data=='Delete':
            db.session.delete(user)
        
        db.session.commit()
            
        return redirect(url_for('authorization.manage'))
        
    return render_template('authorization/Management.html', form=form,users=users)



