import '@babel/polyfill';

import MiniCssExtractPlugin from 'mini-css-extract-plugin';
import gulp from 'gulp';
import concat from 'gulp-concat';
import consolidate from 'gulp-consolidate';
import env from 'gulp-env';
import iconfont from 'gulp-iconfont';
import livereload from 'gulp-livereload';
import merge from 'merge-stream';
import minifyCSS from 'gulp-clean-css';
import modernizr from 'gulp-modernizr';
import rename from 'gulp-rename';
import sass from 'gulp-sass';
import uglify from 'gulp-uglify';
import gutil from 'gulp-util';
import path from 'path';
import named from 'vinyl-named';
import spritesmith from 'gulp.spritesmith';
import webpack from 'webpack';
import WebpackDevServer from 'webpack-dev-server';
import webpackStream from 'webpack-stream';


/* Get env variables */
env('.env');

/* Global variables */
const root_dir = '../../';
const static_dir = root_dir + 'eruditorg/static/';
const templates_dirs = root_dir + 'eruditorg/templates/';
const PROD_ENV = gutil.env.production;

/* DIRS */
var build_dir = PROD_ENV ? static_dir + 'build' : static_dir + 'build_dev';
var sass_dir = static_dir + 'sass';
var js_dir = static_dir + 'js';
var img_dir = static_dir + 'img';
var font_dir = static_dir + 'fonts';
var iconfont_dir = static_dir + 'iconfont';


/*
 * Global webpack config
 * ~~~~~~~~~~~~~~~~~~~~~
 */

var webpackConfig = {

  mode: PROD_ENV ? "production" : "development",

  output: {
    filename: 'js/[name].js',
  },
  resolve: {
    modules: ['node_modules'],
    extensions: ['.webpack.js', '.web.js', '.js', '.jsx', '.json', 'scss'],
  },
  module: {
    rules: [
      {
          test: /\.m?js$/,
          exclude: /node_modules/,
          use: {
              loader: 'babel-loader',
              options: {
                presets: ["@babel/preset-env"],
                plugins: ["@babel/plugin-proposal-function-bind"]
              }
          },
      },
      {
          test:  /\.(sa|sc|c)ss$/,
          use: [
              {
                  loader: MiniCssExtractPlugin.loader,
                  options: { allChunks: true, publicPath: '../'},
              },

              'css-loader',
              'sass-loader',
          ]
      },
      { test: /\.json$/, loader: 'json-loader' },
      { test: /\.txt$/, loader: 'raw-loader' },
      { test: /\.(png|jpg|jpeg|gif|svg|woff|woff2)(\?v=[0-9]\.[0-9]\.[0-9])?(\?[0-9a-zA-Z]*)?$/, loader: 'url-loader?limit=10000' },
      { test: /\.(eot|ttf|wav|mp3|otf)(\?v=[0-9]\.[0-9]\.[0-9])?(\?[0-9a-zA-Z]*)?$/, loader: 'file-loader' },
    ],
  },
  externals: {
    // require("jquery") is external and available
    //  on the global var jQuery
    'jquery': 'jQuery'
  },
  plugins: [
    new MiniCssExtractPlugin({
        filename: 'css/[name].css',
        chunkFilename: 'css/[id].css',
    })
  ],
};


/*
 * Webpack task
 * ~~~~~~~~~~~~
 */

/* Task to build our JS and CSS applications. */
gulp.task('build-webpack-assets', function () {
  return gulp.src([
        js_dir + '/app.js', sass_dir + '/app.scss',
      ])
    .pipe(named())
    .pipe(webpackStream(webpackConfig))
    .pipe(gulp.dest(build_dir));
});


/*
 * Other tasks
 * ~~~~~~~~~~~
 */

gulp.task('build-modernizr', function(){
  return gulp.src([js_dir + '**/*.js', sass_dir + '**/*.scss'])
    .pipe(modernizr({
      cache: true,
      devFiles: false,
      options : [
      "setClasses",
      "html5shiv",
      "prefixed",
      "prefixedCSS",
      "prefixedCSSValue"
      ]
    }))
    .pipe(PROD_ENV ? uglify() : gutil.noop())
    .pipe(gulp.dest(build_dir + '/js'));
});

gulp.task('build-iconfont', function(){
  let runTimestamp = Math.round(Date.now()/1000);
  return gulp.src([iconfont_dir + '/**/*.svg'])
    .pipe(iconfont({
      fontName: 'erudicon',
      formats: ['ttf', 'eot', 'woff', 'svg'],
      normalize: true,
      fontHeight: 1001,
      timestamp: runTimestamp
    }))
    .on('glyphs', function(glyphs, options) {
      // CSS templating, e.g.
      gulp.src(iconfont_dir + '/template.scss')
        .pipe(consolidate('lodash', {
          glyphs: glyphs,
          fontName: 'erudicon',
          fontPath: '/static/fonts/erudicon/',
          className: 'erudicon'
        }))
        .pipe(rename('_erudicon.scss'))
        .pipe(gulp.dest(sass_dir + '/utils/'));
    })
    .pipe(gulp.dest(font_dir + '/erudicon/'));
});

gulp.task('build-sprite', function () {
  let spriteData = gulp.src(img_dir + '/sprite/*.png').pipe(spritesmith({
    imgName: '../img/sprite.png',
    cssName: '_sprite.scss',
    cssVarMap: function (sprite) {
      sprite.name = 'sprite-' + sprite.name;
    }
  }));

  let imgStream = spriteData.img
    .pipe(gulp.dest(img_dir));

  let cssStream = spriteData.css
    .pipe(gulp.dest(sass_dir + '/utils/'));

  return merge(imgStream, cssStream);
});

/*
 * Global tasks
 * ~~~~~~~~~~~~
 */

gulp.task('build', gulp.parallel(
  'build-modernizr', 'build-iconfont',
  'build-webpack-assets',
));


/*
 * Development tasks
 * ~~~~~~~~~~~~~~~~~
 */

gulp.task('webpack-dev-server', function(callback) {
  var devWebpackConfig = Object.create(webpackConfig);
  devWebpackConfig.devtool = 'eval';
  devWebpackConfig.mode = 'development';
  devWebpackConfig.devServer = { hot: true };
  devWebpackConfig.entry = {
    app: [
      js_dir + '/app.js', sass_dir + '/app.scss',
      'webpack-dev-server/client?http://localhost:8080',
      'webpack/hot/only-dev-server',
    ],
  };
  devWebpackConfig.module = {
    rules: [
      {
        test: /\.m?js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ["@babel/preset-env"],
            plugins: ["@babel/plugin-proposal-function-bind"],
          },
        },
      },
      {
        test:  /\.(sa|sc|c)ss$/,
        use: ['style-loader', 'css-loader', 'sass-loader'],
      },
      {test: /\.json$/, loader: 'json-loader'},
      {test: /\.txt$/, loader: 'raw-loader'},
      {test: /\.(png|jpg|jpeg|gif|svg|woff|woff2)(\?v=[0-9]\.[0-9]\.[0-9])?(\?[0-9a-zA-Z]*)?$/, loader: 'url-loader?limit=10000'},
      {test: /\.(eot|ttf|wav|mp3|otf)(\?v=[0-9]\.[0-9]\.[0-9])?(\?[0-9a-zA-Z]*)?$/, loader: 'file-loader'},
    ],
  };
  devWebpackConfig.output = {
    path: path.resolve(__dirname, static_dir),
    publicPath: 'http://localhost:8080/static/',
    filename: 'js/[name].js'
  };
  devWebpackConfig.plugins = [
    new webpack.HotModuleReplacementPlugin(),
  ];
  devWebpackConfig.resolve = {
    modules: ['node_modules'],
  };
  devWebpackConfig.externals = {
    'jquery': 'jQuery',
  };

  // Start a webpack-dev-server
  new WebpackDevServer(webpack(devWebpackConfig), {
    contentBase: path.resolve(__dirname, static_dir, '..'),
    publicPath: '/static/',
    hot: true,
    inline: true,
    headers: { "Access-Control-Allow-Origin": "*" },
  }).listen(8080, 'localhost', function(err) {
    if(err) throw new gutil.PluginError('webpack-dev-server', err);
    gutil.log('[webpack-dev-server]', 'http://localhost:8080/webpack-dev-server/index.html');
  });
});

gulp.task('watch', function() {
  // start live reload server
  // host null will make it work for Vagrant
  livereload.listen({ host: eval( process.env.LIVE_RELOAD_IP ) });

  // watch any less file /css directory, ** is for recursive mode
  gulp.watch(sass_dir + '/**/*.scss', gulp.parallel('build-modernizr', 'build-webpack-assets'));
  // watch any js file /js directory, ** is for recursive mode
  gulp.watch(js_dir + '/**/*.js', gulp.parallel('build-webpack-assets'));
  // watch any svg file /iconfont directory, ** is for recursive mode
  gulp.watch(iconfont_dir + '/**/*.svg', gulp.parallel('build-iconfont'));

  /* Trigger a live reload on any Django template changes */
  gulp.watch([templates_dirs + '/**/*.html', templates_dirs + '**/*.xsl']).on('change', livereload.changed);
});
