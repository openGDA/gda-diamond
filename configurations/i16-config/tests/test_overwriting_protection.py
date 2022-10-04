import pytest
from gda.jython import InterfaceProvider
from gda.device import Scannable

def test_overwriting_protection_enabled_on_all_scannables():
	unprotected_scannables = [i for i in InterfaceProvider.getJythonNamespace().getAllNamesForType(Scannable) if not overwriting.isProtected(i)]
	assert len(unprotected_scannables) == 0
