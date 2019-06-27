This page gives an overview of using the Connector API in the client. This page is intended for developers only.

# Use and examples
First, import Connector:
```javascript
import connector from 'path/to/connector' 
```

Then, you have to wait until the connection is open:

```javascript
function doStuff () { ... }
connector.addEventListener('open', doStuff)
// or
connector.addEventListener('open', () => {...})
```

In or after this event you can listen to or send messages.
* If you want to constantly listen to a specific message type:
```javascript
connector.listenToMsg('message-type', (content) => { ... })
```
* If you want to constantly listen to a all messages:
```javascript
connector.addEventListener('message', (response) => { ... })
```
* If you want to stop listening with that function:
```javascript
connector.addEventListener('message', doStuff)
// or connector.listenToMsg('type', doStuff)
connector.removeEventListener('message', doStuff)
```
* If you want to do a single request (for messages with request-response structure):
```javascript
connector.request(
  'message-type-request',
  'message-type-response',
  {payload}
).then((response) => {
    ...
  })
```

* If you want to send a message:
```javascript
connector.send(
  'file-content-request',
  {payload}
)
```
# JSdoc

## Classes

<dl>
<dt><a href="#Connector">Connector</a></dt>
<dd></dd>
</dl>

## Typedefs

<dl>
<dt><a href="#Message">Message</a> : <code>Object</code></dt>
<dd></dd>
<dt><a href="#connectorCallback">connectorCallback</a> : <code>function</code></dt>
<dd></dd>
</dl>

<a name="Connector"></a>

## Connector
**Kind**: global class  

* [Connector](#Connector)
    * [new Connector(path)](#new_Connector_new)
    * [.ws](#Connector+ws) : <code>WebSocket</code>
    * [.close(code, reason)](#Connector+close)
    * [.addEventListener(type, callback)](#Connector+addEventListener)
    * [.removeEventListener(type, callback)](#Connector+removeEventListener)
    * [.send(type, content, [sender], [prefDest])](#Connector+send)
    * [.request(requestType, responseType, content)](#Connector+request) ⇒ <code>Promise.&lt;Object&gt;</code>
    * [.listenToMsg(type, listener)](#Connector+listenToMsg)

<a name="new_Connector_new"></a>

### new Connector(path)
Creates a connection and setups listeners.


| Param | Type | Description |
| --- | --- | --- |
| path | <code>string</code> \| <code>URL</code> | The path to the websocket server. |

<a name="Connector+ws"></a>

### connector.ws : <code>WebSocket</code>
The websocket interface.

**Kind**: instance property of [<code>Connector</code>](#Connector)  
<a name="Connector+close"></a>

### connector.close(code, reason)
Closes connection to websocket server

**Kind**: instance method of [<code>Connector</code>](#Connector)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| code | <code>number</code> | <code>0</code> | Status code of why the connection is closing. |
| reason | <code>string</code> | <code>&quot;I am done.&quot;</code> | A human readable reason of why the connection is closing. |

<a name="Connector+addEventListener"></a>

### connector.addEventListener(type, callback)
Add event listener to the websocket interface.

**Kind**: instance method of [<code>Connector</code>](#Connector)  
**See**: https://github.com/websockets/ws/blob/HEAD/doc/ws.md#event-close-1  

| Param | Type | Description |
| --- | --- | --- |
| type | <code>string</code> | A websocket event type. |
| callback | [<code>connectorCallback</code>](#connectorCallback) | The listener that is called when the specified event happens. |

<a name="Connector+removeEventListener"></a>

### connector.removeEventListener(type, callback)
Removes a listener.

**Kind**: instance method of [<code>Connector</code>](#Connector)  

| Param | Type | Description |
| --- | --- | --- |
| type | <code>string</code> | The type of the event. |
| callback | [<code>connectorCallback</code>](#connectorCallback) | The function to stop listening to the specific event. |

<a name="Connector+send"></a>

### connector.send(type, content, [sender], [prefDest])
Send some content to the websocket server.

**Kind**: instance method of [<code>Connector</code>](#Connector)  

| Param | Type | Default | Description |
| --- | --- | --- | --- |
| type | <code>string</code> |  | The type of the message. |
| content | <code>Object</code> |  | The payload of the message. |
| [sender] | <code>string</code> | <code>&quot;CLIENT&quot;</code> | The identifier of the sender. |
| [prefDest] | <code>string</code> | <code>null</code> | The destination where the message should preferable go. |

<a name="Connector+request"></a>

### connector.request(requestType, responseType, content) ⇒ <code>Promise.&lt;Object&gt;</code>
Sends a message and listens for the response.
A helper method for messages with a request-response structure.

**Kind**: instance method of [<code>Connector</code>](#Connector)  
**Returns**: <code>Promise.&lt;Object&gt;</code> - - A promise with the response content/  

| Param | Type | Description |
| --- | --- | --- |
| requestType | <code>string</code> | The type of the message send. |
| responseType | <code>string</code> | The type of the message to receive. |
| content | <code>Object</code> | The payload to send. |

<a name="Connector+listenToMsg"></a>

### connector.listenToMsg(type, listener)
A method to listen to a specific message type.

**Kind**: instance method of [<code>Connector</code>](#Connector)  

| Param | Type | Description |
| --- | --- | --- |
| type | <code>string</code> | The message type to listen to. |
| listener | [<code>connectorCallback</code>](#connectorCallback) | The function to call. |

<a name="Message"></a>

## Message : <code>Object</code>
**Kind**: global typedef  
**See**: https://github.com/psedit/cte/wiki/Server-service-messages  
**Properties**

| Name | Type | Description |
| --- | --- | --- |
| type | <code>string</code> | The type of message |
| uuid | <code>string</code> | The unique id of the message |
| sender | <code>string</code> | sender service or sender client address |
| pref_dest | <code>string</code> | sender service or sender client address |
| content | <code>Object</code> | the payload of the message |

<a name="connectorCallback"></a>

## connectorCallback : <code>function</code>
**Kind**: global typedef  

| Param | Type | Description |
| --- | --- | --- |
| The | [<code>Message</code>](#Message) | message response. |