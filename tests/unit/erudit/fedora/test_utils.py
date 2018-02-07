from erudit.fedora.utils import localidentifier_from_pid


def test_localidentifier_from_pid():
    assert localidentifier_from_pid('erudit:erudit.ae49.ae03128') == 'ae03128'
