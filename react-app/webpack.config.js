module.exports = {
    mode: "development",
    devtool: "inline-source-map",
    entry: "./src/index.tsx",
    output: {
      filename: "bundle.js"
    },
    resolve: {
      extensions: [".ts", ".tsx", ".js"]
    },
    module: {
      rules: [
        { test: /.tsx?$/, loader: "ts-loader" }
      ]
    },
    devServer: {
      historyApiFallback: true,
      publicPath: '/dist/',
      host: '127.0.0.1',
      port: 9000,
      disableHostCheck: true,
    },
  };