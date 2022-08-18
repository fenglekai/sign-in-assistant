var mariadb = require("mariadb");

const config = require("./config");

var pool = mariadb.createPool({
  host: config.database.HOST,
  port: config.database.PORT,
  user: config.database.USERNAME,
  password: config.database.PASSWORD,
  database: config.database.DATABASE,
});

class Mariadb {
  constructor() {}
  async querySignIn(uId, time) {
    let conn;
    return new Promise(async (resolve, reject) => {
      try {
        conn = await pool.getConnection();
        let res;

        if (uId && time) {
          res = await conn.query(
            `SELECT * FROM sign_in WHERE uId LIKE '${uId}%' AND time>='${time} 00:00:00' AND time<='${time} 23:59:59'`
          );
        } else if (uId) {
          res = await conn.query(`SELECT * FROM sign_in WHERE uId LIKE '${uId}%'`);
        } else if (time) {
          res = await conn.query(`SELECT * FROM sign_in WHERE time>='${time} 00:00:00' AND time<='${time} 23:59:59'`);
        } else {
          res = await conn.query("SELECT * FROM sign_in");
        }
        resolve(res);
      } catch (error) {
        reject(error);
      } finally {
        if (conn) conn.release();
      }
    });
  }
  async insertSignIn(sqlArr) {
    return new Promise(async (resolve, reject) => {
      let conn;
      try {
        conn = await pool.getConnection();
        for (const key in sqlArr) {
          const res = await conn.query(
            `INSERT INTO sign_in (${sqlArr[key][0]}) VALUE (${sqlArr[key][1]});`
            );
            resolve(res);
        }
      } catch (error) {
        reject(error);
      } finally {
        if (conn) conn.release();
      }
    });
  }
}

module.exports = new Mariadb();
