from enum import Enum


class SupportedIntents(Enum):
    # Tuple (Intent name, description, examples)
    LogActivity = (
        "LogActivity",
        "Log an activity",
        "I did yoga today, I did 10 pullups, I held plank for 30 seconds",
    )
    LogPain = (
        "LogPain",
        "Log a pain (on a scale of 1 to 3)",
        "Left hip 1, Right knee high, Left leg none today",
    )
    GetDailyLog = (
        "GetDailyLog",
        "Get a daily log",
        "What did I do yesterday? Show me today",
    )
    GetNumLogs = (
        "GetNumLogs",
        "See how many days you’ve logged",
        "How many days have I logged",
    )
    GetActivitySummary = (
        "GetActivitySummary",
        "Get an activity's summary",
        "Show me my pushup stats, What’s my cycling history?",
    )
    DeleteDailyLog = (
        "DeleteDailyLog",
        "Delete a daily log",
        "Reset today’s log, Delete last Saturday’s log",
    )
    GetCommandList = (
        "GetCommandList",
        "Get a list of supported commands",
        "What can you do? What can I say? What features are there?",
    )

    def __str__(self):
        return self.value[0]

    def __eq__(self, other):
        return other == self.name

    @property
    def description(self):
        return self.value[1]

    @property
    def examples(self):
        return self.value[2]

    @classmethod
    def all(cls):
        return [intent.name for intent in cls]

    @classmethod
    def summarize(cls):
        output = ["The following are supported commands:", ""]
        for intent in cls:
            name, description, examples = intent.value
            output.append(f"- *{description}*: {examples}")

        return "\n".join(output)
