from gda.util import Email
import pytest

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
