module.exports = {
  lintOnSave: false,
  chainWebpack: (config) => {
    config.plugin("html").tap((args) => {
      args[0].title = `签到小助手`;
      return args;
    });
  },
  configureWebpack: {
    devtool: "source-map",
  },
};
