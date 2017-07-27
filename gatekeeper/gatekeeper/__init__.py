from flask import Flask
app = Flask(__name__)

import gatekeeper.views

# cannot run using python __init__.py, have to use flask run
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)





