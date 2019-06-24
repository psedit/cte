import pytest
from contextlib import contextmanager
import Pyro4
from common import start_and_wait, MessageSink, kill_services


def setup_module(module):
    global message_sink
    start_and_wait('MessageBus')


@pytest.fixture(scope="module")
def message_sink():
    @contextmanager
    def _message_sink(*accepting_types):
        sink = MessageSink(accepting_types)
        yield sink
        sink.disconnect()
    return _message_sink


@pytest.fixture
def message_bus():
    p = Pyro4.Proxy("PYRONAME:service.MessageBus")
    p._pyroBind()
    return p


def test_send_receive_message(message_sink, message_bus):
    with message_sink('all') as ms:
        message_bus.put_message({"type": "test_send_message",
                                 "content": "kaas",
                                 "sender": "test"})
        received_msg = ms.wait_for("test_send_message")
        assert (received_msg)
        assert (received_msg['content'] == 'kaas')


def test_request_response(message_sink, message_bus):
    with message_sink() as ms:  # accepts nothing except responses
        message_bus.put_message({"type": "test-request",
                                 "content": "test",
                                 "uuid": "baap",
                                 "sender": ms.name})
        message_bus.put_message({"type": "test-response",
                                 "response_uuid": "baap",
                                 "content": "tset",
                                 "uuid": "rabarber",
                                 "sender": "service.TestResponder"})
        received_msg = ms.wait_for("test-response")
        assert received_msg
        assert received_msg['content'] == 'tset'


def teardown_module(module):
    kill_services()
