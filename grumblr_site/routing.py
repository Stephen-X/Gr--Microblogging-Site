from channels import route
from global_resources.consumers import connect_global_stream, disconnect_global_stream

# The channel routing defines what channels get handled by what consumers,
# including optional matching on message attributes. WebSocket messages of all
# types have a 'path' attribute, so we're using that to route the socket.
channel_routing = [
    # called when incoming WebSockets connect
    route("websocket.connect", connect_global_stream, path=r'^/api/get-messages-stream/$'),
    # called when the client closes the socket
    route("websocket.disconnect", disconnect_global_stream, path=r'^/api/get-messages-stream/$')
]
