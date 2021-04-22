import os
from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'open_health.db'),
    )

from . import db
db.init_app(app)
from . import auth
app.register_blueprint(auth.bp)
from . import health
app.register_blueprint(health.bp)
app.add_url_rule('/', endpoint='index')


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
