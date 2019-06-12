import Pyro4
import sys
sys.path.append('.')
from service import Service, message_type

@Pyro4.expose
class A(Service):
    @message_type('kaas-request')
    async def send_kaasje(self, msg):
        self._info('Kaasverzoek ontvangen!')
        self._send_message('kaas-response', {'kaas': 'Gouda'}, resp_uuid=msg['uuid'])
        self._info('Kaaskeuze verstuurd!')

A.start()
