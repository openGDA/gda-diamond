from gda.util import Email
import pytest

# Note, support for marks was cherry picked from change/36289/1 onto the
#       GDA 9.27 release branch for i15-1, to enable testing.

@pytest.mark.email
def test_email_send():
	Email().to("mark.booth@diamond.ac.uk") \
		.subject("test_email_send") \
		.message("test message") \
		.send()

@pytest.mark.email
def test_email_sendAsync():
	Email().to("mark.booth@diamond.ac.uk") \
		.subject("test_email_sendAsync") \
		.message("test message") \
		.sendAsync()
