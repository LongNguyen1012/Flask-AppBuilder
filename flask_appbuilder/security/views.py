from flask import render_template, flash, redirect, session, url_for, request, g, current_app
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.wtf import Required, Length, validators, EqualTo, PasswordField
from flask.ext.babel import gettext, lazy_gettext

from models import *
from forms import *
from flask.ext.appbuilder.views import BaseView, GeneralView, SimpleFormView, AdditionalLinkItem, expose
from ..forms import BS3PasswordFieldWidget
from flask.ext.appbuilder.models.datamodel import SQLAModel

#try:
#    from app import app, db, lm, oid
#except ImportError:
#    raise Exception('app,db,lm,oid not found please use required skeleton application see documentation')





#----------------------------- DEFS --------------------------------------
#-------------------------------------------------------------------------

class PermissionGeneralView(GeneralView):
    route_base = '/permissions'
    
    datamodel = SQLAModel(Permission, db.session)

    list_title = lazy_gettext('List Base Permissions')
    show_title = lazy_gettext('Show Base Permission')
    add_title = lazy_gettext('Add Base Permission')
    edit_title = lazy_gettext('Edit Base Permission')

    label_columns = {'name':lazy_gettext('Name')}
    list_columns = ['name']
    show_columns = ['name']
    order_columns = ['name']
    search_columns = ['name']

class ViewMenuGeneralView(GeneralView):
    route_base = '/viewmenus'
    
    datamodel = SQLAModel(ViewMenu, db.session)

    list_title = lazy_gettext('List View Menus')
    show_title = lazy_gettext('Show View Menu')
    add_title = lazy_gettext('Add View Menu')
    edit_title = lazy_gettext('Edit View Menu')

    label_columns = {'name':lazy_gettext('Name')}
    list_columns = ['name']
    show_columns = ['name']
    order_columns = ['name']
    search_columns = ['name']


class PermissionViewGeneralView(GeneralView):
    route_base = '/permissionviews'
    
    datamodel = SQLAModel(PermissionView , db.session)

    list_title = lazy_gettext('List Permissions on Views/Menus')
    show_title = lazy_gettext('Show Permission on Views/Menus')
    add_title = lazy_gettext('Add Permission on Views/Menus')
    edit_title = lazy_gettext('Edit Permission on Views/Menus')

    label_columns = {'permission':lazy_gettext('Permission'), 'view_menu': lazy_gettext('View/Menu')}
    list_columns = ['permission', 'view_menu']
    show_columns = ['permission', 'view_menu']
    search_columns = ['permission', 'view_menu']


class ResetMyPasswordView(SimpleFormView):
    """
    View for reseting own user password
    """
    route_base = '/resetmypassword'
    
    form = ResetPasswordForm
    form_title = lazy_gettext('Reset Password Form')
    form_columns = ['password','conf_password']
    redirect_url = '/'

    message = lazy_gettext('Password Changed')

    def form_post(self, form):
        pk = request.args.get('pk')
        user = db.session.query(User).get(pk)
        user.password = form.password.data
        db.session.commit()
        flash(unicode(self.message),'info')


class ResetPasswordView(SimpleFormView):
    """
    View for reseting all users password
    """
    
    route_base = '/resetpassword'
    
    form = ResetPasswordForm
    form_title = lazy_gettext('Reset Password Form')
    form_columns = ['password','conf_password']
    redirect_url = '/'

    message = lazy_gettext('Password Changed')

    def form_post(self, form):
        pk = request.args.get('pk')
        user = db.session.query(User).get(pk)
        user.password = form.password.data
        db.session.commit()
        flash(unicode(self.message),'info')


class UserGeneralView(GeneralView):
    route_base = '/users'
    datamodel = SQLAModel(User, db.session)
    

    list_title = lazy_gettext('List Users')
    show_title = lazy_gettext('Show User')
    add_title = lazy_gettext('Add User')
    edit_title = lazy_gettext('Edit User')

    label_columns = {'get_full_name':lazy_gettext('Full Name'),
                    'first_name':lazy_gettext('First Name'),
                    'last_name':lazy_gettext('Last Name'),
                    'username':lazy_gettext('User Name'),
                    'password':lazy_gettext('Password'),
                    'active':lazy_gettext('Is Active?'),
                    'email':lazy_gettext('EMail'),
                    'role':lazy_gettext('Role')}
    description_columns = {'first_name':lazy_gettext('Write the user first name or names'),
                    'last_name':lazy_gettext('Write the user last name'),
        'username':lazy_gettext('Username valid for authentication on DB or LDAP, unused for OID auth'),
                    'password':lazy_gettext('Please use a good password policy, this application does not check this for you'),
                    'active':lazy_gettext('Its not a good policy to remove a user, just make it inactive'),
                    'email':lazy_gettext('The users email, this will also be used for OID auth'),
                    'role':lazy_gettext('The user role on the application, this will associate with a list of permissions'),
                    'conf_password':lazy_gettext('Please rewrite the users password to confirm')}
    list_columns = ['get_full_name', 'username', 'email','active', 'role']
    show_columns = ['first_name','last_name','username', 'active', 'email','role']
    order_columns = ['username', 'email']
    search_columns = ['first_name','last_name', 'username', 'email']

    add_columns = ['first_name','last_name','username', 'active', 'email','role']
    edit_columns = ['first_name','last_name','username', 'active', 'email','role']

    user_info_title = lazy_gettext("Your user information")
    lnk_reset_password = lazy_gettext("Reset Password")

    show_additional_links = []


class UserOIDGeneralView(UserGeneralView):
    @expose('/userinfo/')
    def userinfo(self):
        widgets = self._get_show_widget(g.user.id)

        return render_template(self.show_template,
                           title = self.user_info_title,
                           widgets = widgets,
                           baseapp = self.baseapp,
                           )

    def _init_forms(self):
        super(UserGeneralView, self)._init_forms()
        self.add_form.password = None

class UserDBGeneralView(UserGeneralView):
    def __init__(self, **kwargs):
        self.show_additional_links = [(AdditionalLinkItem('resetpassword', self.lnk_reset_password,"/resetpassword/form","lock"))]
        super(UserDBGeneralView, self).__init__(**kwargs)

    @expose('/userinfo/')
    def userinfo(self):
        additional_links = None

        show_additional_links = [AdditionalLinkItem('resetmypassword', self.lnk_reset_password,"/resetmypassword/form","lock")]
        widgets = self._get_show_widget(g.user.id, show_additional_links = show_additional_links)
        return render_template(self.show_template,
                           title = self.user_info_title,
                           widgets = widgets,
                           baseapp = self.baseapp,
                           )


    def _init_forms(self):
        super(UserGeneralView, self)._init_forms()
        self.add_form.password = PasswordField('Password', 
                                 description=self.description_columns['password'],
                                 widget=BS3PasswordFieldWidget())
        self.add_form.conf_password = PasswordField('Confirm Password',
                                 default=self.add_form.password,
                                 description=self.description_columns['conf_password'],
                                 validators=[EqualTo('password',message=u'Passwords must match')],
                                 widget=BS3PasswordFieldWidget())
        if 'password' not in self.add_columns:
            self.add_columns = self.add_columns + ['password', 'conf_password']
        

class RoleGeneralView(GeneralView):
    route_base = '/roles'
    
    datamodel = SQLAModel(Role, db.session)

    list_title = lazy_gettext('List Roles')
    show_title = lazy_gettext('Show Role')
    add_title = lazy_gettext('Add Role')
    edit_title = lazy_gettext('Edit Role')

    label_columns = { 'name':lazy_gettext('Name'),'permissions':lazy_gettext('Permissions') }
    list_columns = ['name','permissions']
    show_columns = ['name','permissions']
    order_columns = ['name']
    search_columns = ['name']



class AuthView(BaseView):

    route_base = ''
    login_db_template = 'appbuilder/general/security/login_db.html'
    login_oid_template = 'appbuilder/general/security/login_oid.html'
    
    invalid_login_message = lazy_gettext('Invalid login. Please try again.')
    
    title = lazy_gettext('Sign In')

    @expose('/logout/')
    def logout(self):
        logout_user()
        return redirect('/')


class AuthDBView(AuthView):        

    @expose('/login/', methods = ['GET', 'POST'])
    def login(self):
        if g.user is not None and g.user.is_authenticated():
            return redirect('/')
        form = LoginForm_db()
        if form.validate_on_submit():
            user = self.baseapp.sm.auth_user_db(form.username.data, form.password.data)
            if not user:
                flash(unicode(self.invalid_login_message),'warning')
                return redirect('/login')
            login_user(user, remember = False)
            return redirect('/')
        return render_template(self.login_db_template,
                                                title = self.title,
                                                form = form,
                                                baseapp = self.baseapp
                                                )

class AuthOIDView(AuthView):
    

    @expose('/login/', methods = ['GET', 'POST'])
    def login(self):
        print "LOGIN.----------------------"
        if g.user is not None and g.user.is_authenticated():
            return redirect('/')
        form = LoginForm_oid()
        if form.validate_on_submit():
            session['remember_me'] = form.remember_me.data
            return oid.try_login(form.openid.data, ask_for = ['email'])
        return render_template(self.login_oid_template,
                title = self.title,
                form = form,
                providers = app.config['OPENID_PROVIDERS'],
                baseapp = self.baseapp
                )

    def after_login(self, resp):
        print "AFTERRRRR---------------------------------------"
        if resp.email is None or resp.email == "":
            flash(gettext('Invalid login. Please try again.'),'warning')
            return redirect('appbuilder/general/security/login_oid.html')
        user = User.query.filter_by(email = resp.email).first()
        if user is None:
            flash(gettext('Invalid login. Please try again.'),'warning')
            return redirect('appbuilder/general/security/login_oid.html')
        remember_me = False
        if 'remember_me' in session:
            remember_me = session['remember_me']
            session.pop('remember_me', None)

        login_user(user, remember = remember_me)
        return redirect('/')




