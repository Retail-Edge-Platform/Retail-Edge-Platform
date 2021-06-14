var path = '/services/ws';

function ws_send_message(data, ws_socket) {
    if(ws_socket){
        const msg = JSON.stringify(data);
        ws_socket.send(msg);
    }
}

function ws_close(ws_socket){
    if(ws_socket){
        ws_socket.close();
    }
}

// TODO: Add a message that the web socket is no longer connected to the UI
//       in the case where connectivity to the server is lost
// TODO: Attempt to reconnect to the server.

function ws_setup(path, on_message_callback){
    // Note: You have to change the host var
    // if your client runs on a different machine than the websocket server
    var host = "ws://" + location.host + path;
    var ws_socket = new WebSocket(host);
    // console.log("socket status: " + ws_socket.readyState);
    // event handlers for websocket
    if(ws_socket){
        ws_socket.onopen = function(){
            //alert("connection opened....");
        }
        ws_socket.onmessage = function(msg){
            jsonString = msg.data;
            robj = JSON.parse(jsonString);
            on_message_callback(robj);
        }
        ws_socket.onclose = function(){
            //alert("connection closed....");
        }
    }else{
        console.log("invalid socket");
    }
    return ws_socket;
}