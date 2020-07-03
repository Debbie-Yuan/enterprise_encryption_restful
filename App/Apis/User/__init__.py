from flask_restful import Api
from .user_api import UserResource
from .user_attendance_api import UserAttendanceResource
from .user_protrait_api import UserPortraitResource

client_api = Api(prefix='/user')

client_api.add_resource(UserResource, '')
client_api.add_resource(UserAttendanceResource, '/att')
client_api.add_resource(UserPortraitResource, '/prt')
