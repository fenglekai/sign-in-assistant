module.exports = {
  lintOnSave: false,
  productionSourceMap: true,
  chainWebpack: (config) => {
    config.plugin("html").tap((args) => {
      args[0].title = `签到小助手`;
      return args;
    });
  },
};
