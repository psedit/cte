import os
import pytest
import Pyro4
from common import start_services, start_nameserver, \
                   wait_for_services, kill_services, \
                   MessageSink

def setup_module(module):
    global message_sink
    start_and_wait('MessageBus')

@pytest.fixture(scope="module")
def message_sink():
    sink = MessageSink()
    return sink

@pytest.fixture
def message_bus():
    p = Pyro4.Proxy("PYRONAME:service.MessageBus")
    p._pyroBind()
    return p

def test_send_message(message_sink, message_bus):
    message_bus.put_message({"type": "test_send_message", "content": "kaas")
    assert (msg := message_sink.wait_for("test_send_message"))
    assert (msg['content'] == 'kaas')


def teardown_module(module):
    kill_services()

