import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class DBLogs:

  def __init__(self):
    self._db = firestore.client()
    self._collection_ref = self._db.collection('activityLogs')
    self._num_logs = self._get_num_logs()

  def get_log(self, date):
    x = self._collection_ref.document(date).get()

    if x.exists:
      x = x.to_dict()
      print('Log retrieved successfully. Preview of the returned dict from Firestore:')
      print(x)

      # Map the Firestore dict to the DailyLog object
      log = DailyLog.from_dict(x)
      print('Log converted to Python log object successfully')

    else:
      print(f"Log for date '{date}' doesn't exist. Initiating DailyLog instance")
      log = DailyLog(date)

    return log


  def upload_log(self, log):
    self._collection_ref.document(log.date).set(log.to_dict())

    # In case this was a new one, update the count
    # TODO: run this only if log was new
    self._num_logs = self._get_num_logs()

  def _get_num_logs(self):
    documents = self._collection_ref.stream()
    doc_count = sum(1 for _ in documents)
    return doc_count

  @property
  def num_logs(self):
    return self._num_logs
