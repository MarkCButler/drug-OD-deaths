const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  entry: {
    main: './src/main.js'
  },
  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, '../static'),
    clean: true,
  },
  module: {
    rules: [
      {
        test: /\.scss$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          {
            loader: 'postcss-loader',
            options: {
              postcssOptions: {
                plugins: function() {
                  return [
                    require('autoprefixer')
                  ];
                }
              }
            }
          },
          'sass-loader'
        ]
      },
      {
        test: /\.js$/,
        use: [
          'ify-loader',
          'transform-loader?plotly.js/tasks/compress_attributes.js',
        ]
      }
    ]
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name].css'
    }),
  ]
};
