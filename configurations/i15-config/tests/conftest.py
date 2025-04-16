from beamline_test.fixtures import *

def pytest_configure(config):
    # register markers to avoid warnings
    config.addinivalue_line("markers",
        "email: mark test as sending email, (deselect with 'marks=\"not email\"')")
    config.addinivalue_line("markers",
        "plotting: mark test as plotting demo, (select with 'marks=\"plotting\"')")