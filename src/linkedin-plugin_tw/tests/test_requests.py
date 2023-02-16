from conftest import get_premade_plugin


class AlwaysFailingSession:
    def __init__(self, *args, **kwargs):
        pass

    def get(self, *args, **kwargs):
        raise Exception("Failing request")


def test_failing_requests():
    plugin = get_premade_plugin(import_data=False)
    plugin.session = AlwaysFailingSession()

    # This should not raise an exception
    plugin.sync()
    plugin.join()
