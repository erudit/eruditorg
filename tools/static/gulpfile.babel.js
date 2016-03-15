import 'babel-polyfill';

import ExtractTextPlugin from 'extract-text-webpack-plugin';
import gulp from 'gulp';
import concat from 'gulp-concat';
import consolidate from 'gulp-consolidate';
import env from 'gulp-env';
import iconfont from 'gulp-iconfont';
import livereload from 'gulp-livereload';
import minifyCSS from 'gulp-minify-css';
import modernizr from 'gulp-modernizr';
import rename from 'gulp-rename';
import sass from 'gulp-sass';
import uglify from 'gulp-uglify';
import gutil from 'gulp-util';
import path from 'path';
import named from 'vinyl-named';
import webpack from 'webpack';
import WebpackDevServer from 'webpack-dev-server';
import webpackStream from 'webpack-stream';


/* Get env variables */
env('.env');

/* Global variables */
const root_dir = '../../';
const static_dir = root_dir + 'erudit/static/';
const templates_dirs = root_dir + 'erudit/templates/';
const PROD_ENV = gutil.env.production;

/* DIRS */
var build_dir = PROD_ENV ? static_dir + 'build' : static_dir + 'build_dev';
var bower_dir = root_dir + 'bower_components';
var sass_dir = static_dir + 'sass';
var js_dir = static_dir + 'js';
var img_dir = static_dir + 'img';
var font_dir = static_dir + 'fonts';
var iconfont_dir = static_dir + 'iconfont';


/*
 * Global webpack config
 * ~~~~~~~~~~~~~~~~~~~~~
 */

let extractCSS = new ExtractTextPlugin('css/[name].css', { allChunks: true });
var webpackConfig = {
  output: {
    filename: 'js/[name].js',
  },
  resolve: {
    modulesDirectories: ['node_modules', bower_dir],
    extensions: ['', '.webpack.js', '.web.js', '.js', '.jsx', '.json', 'scss'],
  },
  module: {
    loaders: [
      { test: /\.jsx?$/, exclude: /node_modules/, loader: 'babel-loader' },
      { test: /\.scss$/i, loader: extractCSS.extract(['css','sass'], { publicPath: '../'}) },
      { test: /\.json$/, loader: 'json-loader' },
      { test: /\.txt$/, loader: 'raw-loader' },
      { test: /\.(png|jpg|jpeg|gif|svg|woff|woff2)(\?v=[0-9]\.[0-9]\.[0-9])?(\?[0-9a-zA-Z]*)?$/, loader: 'url-loader?limit=10000' },
      { test: /\.(eot|ttf|wav|mp3|otf)(\?v=[0-9]\.[0-9]\.[0-9])?(\?[0-9a-zA-Z]*)?$/, loader: 'file-loader' },
    ],
  },
  plugins: [
    extractCSS,
    ...(PROD_ENV ? [
      new webpack.optimize.UglifyJsPlugin({
        compress: { warnings: false }
      })
    ] : []),
  ],
};


/*
 * Webpack task
 * ~~~~~~~~~~~~
 */

/* Task to build our JS and CSS applications. */
gulp.task('build-webpack-assets', function () {
  return gulp.src([
        js_dir + '/PublicApp.js', js_dir + '/UserspaceApp.js',
        sass_dir + '/PublicApp.scss', sass_dir + '/UserspaceApp.scss',
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

gulp.task('build-videojs-js', function() {
  return gulp.src([
        bower_dir + '/video.js/dist/video.min.js',
        bower_dir + '/videojs-vimeo/src/Vimeo.js',
      ])
    .pipe(concat('videojs.js'))
    .pipe(PROD_ENV ? uglify() : gutil.noop())
    .pipe(gulp.dest(build_dir + '/js'));
});
gulp.task('build-pdfjs-js-map', function() {
  return gulp.src(bower_dir + '/video.js/dist/video.min.js.map')
    .pipe(gulp.dest(build_dir + '/js'));
});
gulp.task('build-videojs-css', function() {
  return gulp.src(bower_dir + '/video.js/dist/video-js.min.css')
    .pipe(rename('videojs.css'))
    .pipe(gulp.dest(build_dir + '/css'));
});
gulp.task('build-videojs', ['build-videojs-js','build-pdfjs-js-map', 'build-videojs-css', ]);

gulp.task('build-pdfjs-css', function() {
  return gulp.src([
        sass_dir + '/pages/pdf_viewer.scss',
        bower_dir + '/pdfjs-build/generic/web/viewer.css',
      ])
    .pipe(sass())
    .on('error', sass.logError)
    .pipe(concat('pdf-viewer.css'))
    .pipe(PROD_ENV ? minifyCSS() : gutil.noop())
    .pipe(gulp.dest(build_dir + '/css'));
});
gulp.task('build-pdfjs-js', function() {
  return gulp.src([
        bower_dir + '/pdfjs-build/generic/web/l10n.js',
        bower_dir + '/pdfjs-build/generic/build/pdf.js',
        bower_dir + '/pdfjs-build/generic/web/debugger.js',
        bower_dir + '/pdfjs-build/generic/web/viewer.js',
      ])
    .pipe(concat('pdf-viewer.js'))
    .pipe(PROD_ENV ? uglify() : gutil.noop())
    .pipe(gulp.dest(build_dir + '/js'));
});
gulp.task('build-pdfjs-locale', function() {
  return gulp.src(bower_dir + '/pdfjs-build/generic/web/locale/**/*')
    .pipe(gulp.dest(build_dir + '/locale/pdf-viewer'));
});
gulp.task('build-pdfjs-images', function() {
  return gulp.src(bower_dir + '/pdfjs-build/generic/web/images/**/*')
    .pipe(gulp.dest(build_dir + '/css/images'));
});
gulp.task('build-pdfjs-worker', function() {
  return gulp.src(bower_dir + '/pdfjs-build/generic/build/pdf.worker.js')
    .pipe(gulp.dest(build_dir + '/js'));
});
gulp.task('build-pdfjs', [
  'build-pdfjs-css', 'build-pdfjs-js', 'build-pdfjs-locale', 'build-pdfjs-images', 'build-pdfjs-worker', ]);


/*
 * Global tasks
 * ~~~~~~~~~~~~
 */

gulp.task('build', [
  'build-modernizr', 'build-iconfont', 'build-videojs', 'build-pdfjs',
  'build-webpack-assets',
]);


/*
 * Development tasks
 * ~~~~~~~~~~~~~~~~~
 */

gulp.task('webpack-dev-server', function(callback) {
  var devWebpackConfig = Object.create(webpackConfig);
  devWebpackConfig.devtool = 'eval';
  devWebpackConfig.debug = true;
  devWebpackConfig.devServer = { hot: true };
  devWebpackConfig.entry = {
    PublicApp: [
      js_dir + '/PublicApp.js', sass_dir + '/PublicApp.scss',
      'webpack-dev-server/client?http://localhost:8080',
      'webpack/hot/only-dev-server',
    ],
    UserspaceApp: [
      js_dir + '/UserspaceApp.js', sass_dir + '/UserspaceApp.scss',
      'webpack-dev-server/client?http://localhost:8080',
      'webpack/hot/only-dev-server',
    ],
  };
  devWebpackConfig.module = {
    loaders: [
      { test: /\.jsx?$/, exclude: /node_modules/, loader: 'babel-loader' },
      { test: /\.scss$/i, loaders: ['style', 'css', 'sass', ] },
      { test: /\.json$/, loader: 'json-loader' },
      { test: /\.txt$/, loader: 'raw-loader' },
      { test: /\.(png|jpg|jpeg|gif|svg|woff|woff2)(\?v=[0-9]\.[0-9]\.[0-9])?(\?[0-9a-zA-Z]*)?$/, loader: 'url-loader?limit=10000' },
      { test: /\.(eot|ttf|wav|mp3|otf)(\?v=[0-9]\.[0-9]\.[0-9])?(\?[0-9a-zA-Z]*)?$/, loader: 'file-loader' },
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

  // Start a webpack-dev-server
  new WebpackDevServer(webpack(devWebpackConfig), {
    contentBase: path.resolve(__dirname, static_dir, '..'),
    publicPath: '/static/',
    hot: true,
    inline: true,
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
  gulp.watch(sass_dir + '/**/*.scss', ['build-modernizr', 'build-pdfjs-css', 'build-webpack-assets', ]);
  // watch any js file /js directory, ** is for recursive mode
  gulp.watch(js_dir + '/**/*.js', ['build-webpack-assets', ]);
  // watch any svg file /iconfont directory, ** is for recursive mode
  gulp.watch(iconfont_dir + '/**/*.svg', ['iconfont']);

  /* Trigger a live reload on any Django template changes */
  gulp.watch([templates_dirs + '/**/*.html', templates_dirs + '**/*.xls']).on('change', livereload.changed);
});
