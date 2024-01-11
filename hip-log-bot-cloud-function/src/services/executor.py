import logging
import traceback
from models.intent import Intent
from models.supported_intents import SupportedIntents
from models.record import Activity, Pain
from services.hiplogdb import HipLogDB

logger = logging.getLogger(__name__)


class Executor:
    def __init__(self, request):
        self._intent = Intent(request)
        self._hiplogdb = HipLogDB()
        self._request = request

    def run(self) -> str:
        """Run the

        Returns:
            str: Returns the message passed back to users, or an error message as needed
        """
        try:
            res = self._decision_flow()

        # Known errors: return a polished error message for handled error types
        except ValueError as e:  # noqa
            # TODO: change
            if "Unsupported intent" in str(e):
                res = f"We don't support this yet (intent = {self._request['queryResult']['intent']['displayName']}))"  # noqa

            elif "Mismatched number of reps/weights/durations" in str(e):
                res = "It looks like you provided unmatched entries for reps/weights/durations (eg specified 2 sets of reps but only 1 weight). Check your log and try again"  # noqa
            else:
                raise

        # Unknown errors: Log full trace
        except Exception:
            logger.error(
                f"Failed logging, here's the input request:\n{self._request}\n"
            )
            traceback.print_exc()  # TODO: confirm this is printed to GCloud logs
            res = "FAILED"

        return res

    def _decision_flow(self):
        """Take 1+ action(s) based on the intent type and return a message

        Returns:
            str: The string passed back to end users (eg a daily log summary, a summary
            message, or a deletion confirmation)
        """

        # First handle generic requests, that don't require specific log queries.
        # Otherwise do log-based actions
        if self._intent.type == SupportedIntents.GetNumLogs:
            num_logs = self._hiplogdb.get_num_logs_by_user(self._intent.user)
            res = f"There are {num_logs} logs"

        elif self._intent.type == SupportedIntents.GetDailyLog:
            log = self._hiplogdb.get_log(
                self._intent.user, self._intent.date, initialize_empty=True
            )
            logger.info(f"Retrieved DailyLog (local object) generated:\n{log}")

        elif self._intent.type == SupportedIntents.LogActivity:
            log = self._hiplogdb.get_log(
                self._intent.user, self._intent.date, initialize_empty=True
            )
            log.add_activity(Activity.from_dict(self._intent._log_input))
            logger.info(f"DailyLog (local object) generated:\n{log}")

        elif self._intent.type == SupportedIntents.LogPain:
            log = self._hiplogdb.get_log(
                self._intent.user, self._intent.date, initialize_empty=True
            )
            log.add_pain(Pain(**self._intent.log_input))
            logger.info(f"DailyLog (local object) generated:\n{log}")

        elif self._intent.type == SupportedIntents.DeleteDailyLog:
            self._hiplogdb.delete_log(self._intent.user, self._intent.date)
            res = f"Your entry '{self._intent.date}' was deleted"

        elif self._intent.type == SupportedIntents.GetActivitySummary:
            activity_name = self._intent.log_input["name"]
            stats = self._hiplogdb.get_activity_summary(
                self._intent.user, activity_name
            )
            output = [f"**Summary Stats for '{activity_name}'**\n"]
            output += [f"{k}: {v}" for k, v in stats.items()]
            res = "\n".join(output)

        if self._intent.type in [
            SupportedIntents.LogActivity,
            SupportedIntents.LogPain,
        ]:
            # TODO add logic to bubble up new vs update status

            # TODO: retrieve into here too but tbd how cuz also need to handle
            # differently

            # Upload the new/modified log back
            logger.info("Uploading DailyLog")
            self._hiplogdb.upload_log(self._intent.user, log)
            logger.info("Completed upload")

        if self._intent.type in [
            SupportedIntents.LogActivity,
            SupportedIntents.LogPain,
            SupportedIntents.GetDailyLog,
        ]:
            res = log.__str__()

        if self._intent.type == SupportedIntents.GetCommandList:
            res = SupportedIntents.summarize()

        return res
