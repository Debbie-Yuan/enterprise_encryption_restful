from flask_script import Command, Option


def handle(app, host, port, workers):
    from gunicorn.app.base import Application

    class FlaskApplication(Application):
        def init(self, parser, opts, args):
            return {
                'bind': '{0}:{1}'.format(host, port),
                'workers': workers
            }

        def load(self):
            return app

    FlaskApplication().run()


class Gunicorn(Command):

    description = 'Run Flask App in Gunicorn'

    def __init__(self, host='127.0.0.1', port=5688, workers=4):
        super(Gunicorn, self).__init__()
        self.port = port
        self.host = host
        self.workers = workers

    def get_options(self):
        return (
            Option('-H', '--host',
                   dest='host',
                   default=self.host),

            Option('-p', '--port',
                   dest='port',
                   type=int,
                   default=self.port),

            Option('-w', '--workers',
                   dest='workers',
                   type=int,
                   default=self.workers),
        )

    def run(self):
        pass