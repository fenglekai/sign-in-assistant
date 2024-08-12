//util/ws.js
const WebSocket = require("ws");
const uuid = require("uuid");
const zlib = require("zlib");

/**
 * @typedef {{userClient: WebSocket; ip: string; roomKey: string }} UserValue
 * @type {Map<string, UserValue>}
 */
const userMap = new Map();

const roomList = [];

/**
 * @typedef {{pythonClient: WebSocket; ip: string; idle: boolean;}} roomValue
 * @type {Map<string, roomValue>}
 */
const roomMap = new Map();

const SERVICE_KEY = "[service]";

const handleBuffer = (rawData) => {
  let message;
  switch (true) {
    case rawData instanceof Blob:
      // 处理 Blob 数据
      const reader = new FileReader();
      reader.onload = function () {
        message = reader.result;
      };
      reader.readAsText(rawData);
      break;
    case rawData instanceof ArrayBuffer:
      // 处理 ArrayBuffer 数据
      message = new TextDecoder("utf-8").decode(rawData);
      break;
    case rawData instanceof Buffer:
      // 处理 ArrayBuffer 数据
      message = rawData.toString();
      break;
    default:
      // 处理字符串数据
      message = rawData;
  }
  if (message) {
    return message;
  }
  return "";
};

/**
 *
 * @param {WebSocket.Server} wss
 */
module.exports = (wss) => {
  wss.on("connection", (ws, request) => {
    if (!request.headers.origin || !ws._socket.remoteAddress) {
      ws.send("401");
      ws.close();
      return;
    }
    const userId = uuid.v4();
    userMap.set(userId, {
      userClient: ws,
      ip: ws._socket.remoteAddress,
      roomKey: "",
    });
    console.log("origin: %s", request.headers.origin);
    console.log("ip: %s", ws._socket.remoteAddress);
    console.log("userId: %s", userId);

    ws.on("message", (message, isBinary) => {
      console.log("[%s] %s", userId, message);
      if (message.includes("[python]::")) {
        roomMap.set(userId, {
          pythonClient: ws,
          ip: ws._socket.remoteAddress,
          idle: true,
          userList: [],
        });
        console.log("当前房间数量: %s", roomMap.size);
        return;
      }
      if (message.includes("[web]")) {
        roomSend(ws, message, isBinary, userId);
        return;
      }
      if (message.includes("[python]_")) {
        // [python] {'userId': 'id', 'data': 'xxx'}
        const replaceMsg = message.toString().replace("[python]_", "").replaceAll("'", '"');
        const postData = JSON.parse(replaceMsg);
        const buffer = Buffer.from(postData["data"], "base64");
        zlib.unzip(buffer, (err, result) => {
          if (err) {
            console.error("解析失败: ", err);
            return;
          }
          const decompressedData = result.toString("utf-8");
          postData["data"] = decompressedData
          if (userMap.has(postData["userId"])) {
            userMap.get(postData["userId"]).userClient.send(postData["data"]);
          }
        });
        return
      }
    });
    ws.on("error", console.error);
    ws.on("close", () => {
      console.log("用户退出: %s", userId);
      userMap.delete(userId);
      if (roomMap.has(userId)) {
        roomMap.delete(userId);
      }
    });
  });

  /**
   * 房间
   * @param {WebSocket} client
   * @param {WebSocket.RawData} RawData
   * @param {boolean} isBinary
   * @param {string} userId
   */
  const roomSend = (client, rawData, isBinary, userId) => {
    const data = handleBuffer(rawData);
    if (userMap.has(userId)) {
      let currentUser = userMap.get(userId);
      if (roomMap.has(currentUser.roomKey)) {
        pythonSend(
          {
            userId,
            ip: currentUser.ip,
            roomKey: currentUser.roomKey,
          },
          data,
          isBinary
        );
      } else {
        for (const [roomKey, roomValue] of roomMap.entries()) {
          if (roomValue.idle) {
            userMap.set(userId, {
              ...currentUser,
              roomKey,
            });
            break;
          }
        }
        currentUser = userMap.get(userId);
        if (!currentUser.roomKey) {
          client.send(`${SERVICE_KEY} 未找到空闲客户端`);
        } else {
          pythonSend(
            {
              userId,
              ip: currentUser.ip,
              roomKey: currentUser.roomKey,
            },
            data,
            isBinary
          );
        }
      }
    }
  };

  /**
   * 向python发送json数据
   * @param {UserValue} currentUser
   * @param {WebSocket.RawData} data
   * @param {boolean} isBinary
   */
  const pythonSend = (currentUser, data, isBinary) => {
    roomMap
      .get(currentUser.roomKey)
      .pythonClient.send(JSON.stringify({ data, currentUser }), {
        binary: isBinary,
      });
  };

  /**
   * 转发给其他人
   * @param {WebSocket} ws
   * @param {WebSocket.RawData} data
   * @param {boolean} isBinary
   */
  const sendAll = (ws, data, isBinary) => {
    wss.clients.forEach(function each(client) {
      if (client !== ws && client.readyState === WebSocket.WebSocket.OPEN) {
        client.send(data, { binary: isBinary });
      }
    });
  };
};
