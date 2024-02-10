from ansible_collections.jkasama.linux_ut.plugins.modules.get_locale import (
    get_available_locales,
    get_locale_details,
    gather_commands_coroutines,
)

import pytest
import asyncio
import locale


current_locale = locale.getlocale()[1]


@pytest.fixture
def event_loop():
    return asyncio.get_event_loop()


def test_method_get_available_locales_success(event_loop):
    list = event_loop.run_until_complete(get_available_locales(current_locale))

    if list is not None:
        assert len(list) > 0
    else:
        assert list is None


def test_method_get_locale_details_success(event_loop):
    dict = event_loop.run_until_complete(get_locale_details(current_locale))

    assert "LANG" in dict.keys()
    assert "LC_ALL" in dict.keys()


def test_gather_get_locale_details_and_available_locale(event_loop):
    list = event_loop.run_until_complete(gather_commands_coroutines(current_locale))

    assert len(list) == 2
