import Pyro4
import sys
sys.path.append('.')
from service import Service, message_type

@Pyro4.expose
class B(Service):
    @message_type('geef-voedsel')
    async def geeft_voedsel(self, msg):
        self._info('Voedsel aan het samenstellen...')
        self._info('Kaasverzoek aan het sturen.')
        req = self._send_message('kaas-request', {'opties': 'Gouda'})

        resp = await self._wait_for_response(req['uuid'])

        self._info('Kaasreactie ontvangen (keuze: %s)', resp['content']['kaas'])

        self._send_message('voedsel-response', {'type': 'kaasplankje',
                                                'kaas': resp['content']['kaas']},
                                                resp_uuid=msg['uuid'])


B.start()
