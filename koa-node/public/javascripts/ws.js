//util/ws.js
var WebSocket = require('ws');
module.exports = wss => {
    wss.on('connection', function connection(ws) {
        ws.on('message', function incoming(message,isBinary) {
            console.log('%s', message);
            sendAll(ws,message,isBinary)

        });
        ws.on('error', console.error);
        // setInterval(() => {
        //     ws.send('heatbeat')
        // }, 2000);
        ws.on("close", () => {
            console.log("用户退出连接");
        });
    });
    const sendAll = (ws,data,isBinary) => {
        //转发给其他人
        wss.clients.forEach(function each(client) {
            if (client !== ws && client.readyState === WebSocket.WebSocket.OPEN) {
                client.send(data, { binary: isBinary });
            }
        });
    }
}
