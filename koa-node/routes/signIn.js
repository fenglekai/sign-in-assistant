const router = require("koa-router")();
const mariadb = require("../public/javascripts/mariadb");
const common = require("../public/javascripts/common");

router.prefix("/signIn");
// 获取签到信息
router.get("/", async function (ctx, next) {
  try {
    const params = ctx.request.query
    const data = await mariadb.querySignIn(params.uId,params.date);
    const resData = data.map((item) => {
      const { uId, name, time, machine, isEffective } = item;
      return {
        uId,
        name,
        time: new Date(time).toJSON(),
        machine,
        isEffective,
      };
    });
    ctx.body = common.responseBodyFormat(resData.reverse());
  } catch (error) {
    console.log(error);
    ctx.body = common.responseBodyFormat(error, "error", 500);
  }
});
// 新增签到记录
router.post("/", async function (ctx, next) {
  try {
    const { signInData } = ctx.request.body;
    const queryList = await mariadb.querySignIn();
    // 筛选时间数据
    let filterData = signInData.filter((item) => {
      let flag = true;
      // 接收时间
      const jsonDate = new Date(item.time).toJSON();
      for (const iterator of queryList) {
        // 后台时间
        const strTime = new Date(iterator.time).toJSON();
        // 判断时间和工号是否相同
        if (item.uId == iterator.uId && jsonDate == strTime) {
          flag = false;
          break;
        }
      }
      return flag;
    });
    if (!filterData.length) {
      return (ctx.body = common.responseBodyFormat(
        null,
        "已存在相同时间签到",
        500
      ));
    }
    let sqlArr = []
    filterData.map((item) => {
      const columns = [];
      const values = [];
      for (const key in item) {
        columns.push(`${key}`);
        values.push(`'${item[key]}'`);
      }
      const colStr = columns.join(",");
      const valStr = values.join(",");
      sqlArr.push([colStr,valStr])
    });
    const data = await mariadb.insertSignIn(sqlArr);
    ctx.body = common.responseBodyFormat(signInData);
  } catch (error) {
    console.log(error);
    ctx.body = common.responseBodyFormat(error, "error", 500);
  }
});

module.exports = router;
