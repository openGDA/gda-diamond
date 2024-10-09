from beamline_test.fixtures import *

def pytest_configure(config):
    # register markers to avoid warnings
    # See https://docs.pytest.org/en/latest/how-to/mark.html
    config.addinivalue_line("markers",
        "email: mark test as sending email, (deselect with 'marks=\"not email\"')")
    config.addinivalue_line("markers",
        "plotting: mark test as plotting demo, (select with 'marks=\"PLOTTING\"')")
