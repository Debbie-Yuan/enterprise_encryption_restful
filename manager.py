import os

from flask_migrate import MigrateCommand
from flask_script import Manager

from App import init_app
from App.Apis.api_utils import db_event_commit
from App.Models.User import User
from App.ext import get_session


env = os.environ.get('FLASK_ENV') or 'default'
app = init_app(env)

manager = Manager(app=app)
manager.add_command('db', MigrateCommand)


# Create Command
@manager.option('-n', '-name', dest='username')
@manager.option('-p', '-password', dest='password')
def createsuperuser(username, password):
    if not all([username, password]):
        print('请提供足够的参数。')
        return -1
    user = User.create_admin(
        username=username,
        password=password
    )
    session = get_session()
    session.add(user)
    admin_register_feedback = db_event_commit(session)

    if admin_register_feedback:
        print('Register Successfully.')
    else:
        print('Error occurred when write into the database.')
    return 0


if __name__ == '__main__':
    manager.run()
