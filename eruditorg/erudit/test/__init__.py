import pytest
import locale

try:
    locale.setlocale(locale.LC_COLLATE, "fr_CA.UTF-8")
except locale.Error:
    has_fr_ca = False
else:
    has_fr_ca = True

needs_fr_ca = pytest.mark.skipif(not has_fr_ca, reason="Needs fr_CA.UTF-8 locale")
