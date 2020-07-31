import flask
from flask import request, jsonify
from scheduler import ProblemDef as PD

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/scheduler', methods=['POST'])
def scheduler():
	data = request.get_json()
	Pro = PD.Problem(data,'raw')
	Pro.Scheduler()

	return Pro.Return_json()


if __name__ == '__main__':
    app.run()