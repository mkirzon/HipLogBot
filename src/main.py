import traceback
import logging
import firebase_admin

from flask import Flask, request
from flask_ngrok import run_with_ngrok
from firebase_admin import credentials

from services.db_logs import DBLogs
from services.intent_handler import Intent

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
run_with_ngrok(app)  # Initialize ngrok when the app is run

# Initialize the firebase components
fb_app = firebase_admin.initialize_app(
    credential=credentials.Certificate("/content/hip-log-bot-firebase.json")
)


@app.route("/")
def hello():
    return "Hello"


@app.route("/webhook", methods=["POST"])
def webhook():
    # Get dialog flow request
    req = request.get_json(force=True)

    try:
        # Initialize handlers
        db_logs = DBLogs()
        intent = Intent(req)
        print("The intent request was parsed into this log input info:")
        print(intent)

        # First handle generic requests, that don't require specific log queries.
        # Otherwise do log-based actions
        if intent.type == "GetNumLogs":
            print("Intent = GetNumLogs ")
            num_logs = db_logs.num_logs
            res = f"There are {num_logs} logs"

        else:
            print("Handling log-based intent")
            # Get the corresponding log for requested date
            log = db_logs.get_log(intent.date)

            if intent.type == "LogActivity":
                print("Handling intent: LogActivity")
                log.add_activity(**intent.log_input)

            elif intent.type == "LogPain":
                print("Handling intent: LogPain")
                log.add_pain(**intent.log_input)

            res = log.__str__()

            # Push the log back
            print(f"Log object that's getting uploaded:\n{log}")
            db_logs.upload_log(log)
            print("Upload complete")

    finally:
        print(f"Failed logging, here's the input request:\n{req}")
        res = "FAILED"
        print("\n")
        traceback.print_exc()

    # Send response back to DialogFlow
    response = {"fulfillmentText": res}

    return response


if __name__ == "__main__":
    # app.run()
    app.run(port=443, host="0.0.0.0", ssl_context="adhoc")
