from models.supported_intents import SupportedIntents


def test_eq():
    assert "LogActivity" == SupportedIntents.LogActivity


def test_summarize():
    a = SupportedIntents.summarize()
    assert isinstance(a, str)
    assert (
        "- *Log an activity*: I did yoga today, I did 10 pullups, I held plank for 30 seconds"  # noqa
        in a
    )
