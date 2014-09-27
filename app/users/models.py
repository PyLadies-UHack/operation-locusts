from flask.ext.user import UserManager, UserMixin, SQLAlchemyAdapter
from app import app, db

user_roles = db.Table('user_roles',
    db.Column('id', db.Integer(), primary_key=True),
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean(), nullable=False, default=False)
    password = db.Column(db.String(255), nullable=False, default='')
    email = db.Column(db.String(255), nullable=False, default='')
    name = db.Column(db.String(255), nullable=False, default='')
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))

class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter, app)

def init():

    if not User.query.filter(User.email=='andrew@clarkson.mn').first():
        admin = {
            "name": "Administrator",
            "email": "andrew@clarkson.mn",
            "active": True,
            "password": user_manager.hash_password("test")
        }

        admin = User(**admin)
        admin.roles.append(Role(name='superuser'))
        db.session.add(admin)
        db.session.commit()

app.before_first_request(init)
