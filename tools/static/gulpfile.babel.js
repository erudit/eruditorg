import 'babel-polyfill';

import ExtractTextPlugin from 'extract-text-webpack-plugin';
import gulp from 'gulp';
import concat from 'gulp-concat';
import consolidate from 'gulp-consolidate';
import iconfont from 'gulp-iconfont';
import minifyCSS from 'gulp-minify-css';
import modernizr from 'gulp-modernizr';
import rename from 'gulp-rename';
import sass from 'gulp-sass';
import uglify from 'gulp-uglify';
import gutil from 'gulp-util';
import named from 'vinyl-named';
import webpack from 'webpack';
import webpackStream from 'webpack-stream';

/* Global variables */
const root_dir = '../../'
const static_dir = root_dir + 'erudit/static/';
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
 * Webpack taks
 * ~~~~~~~~~~~~
 */

/* Task to build our CSS applications. */
gulp.task('build-css-applications', function () {
  let extractCSS = new ExtractTextPlugin('[name].css');
  return gulp.src([sass_dir + '/public.scss', sass_dir + '/userspace.scss'])
    .pipe(named())
    .pipe(webpackStream({
      output: {
        filename: '[name].css',
      },
      resolve: {
        modulesDirectories: [bower_dir],
        extensions: ['', 'scss'],
      },
      module: {
        loaders: [
          { test: /\.scss$/i, loader: extractCSS.extract(['css','sass']) },
          { test: /\.json$/, loader: 'json-loader' },
          { test: /\.txt$/, loader: 'raw-loader' },
          { test: /\.(png|jpg|jpeg|gif|svg|woff|woff2)(\?v=[0-9]\.[0-9]\.[0-9])?(\?[0-9a-zA-Z]*)?$/, loader: 'url-loader?limit=10000' },
          { test: /\.(eot|ttf|wav|mp3|otf)(\?v=[0-9]\.[0-9]\.[0-9])?(\?[0-9a-zA-Z]*)?$/, loader: 'file-loader' }
        ],
      },
      plugins: [
        extractCSS,
        ...(PROD_ENV ? [
          new webpack.optimize.UglifyJsPlugin({
            compress: { warnings: false }
          })
        ] : []),
      ]
    }))
    .pipe(gulp.dest(build_dir + '/css'));
});

/* Task to build our Javascript applications. */
gulp.task('build-js-applications', function() {
  return gulp.src([js_dir + '/PublicApp.js', js_dir + '/UserspaceApp.js'])
    .pipe(named())
    .pipe(webpackStream({
      output: {
        filename: '[name].js',
      },
      resolve: {
        modulesDirectories: ['node_modules', bower_dir],
        extensions: ['', '.webpack.js', '.web.js', '.js', '.jsx', '.json'],
      },
      module: {
        loaders: [
          { test: /\.jsx?$/, exclude: /node_modules/, loader: 'babel-loader' }
        ],
      },
      plugins: [
        ...(PROD_ENV ? [
          new webpack.optimize.UglifyJsPlugin({
            compress: { warnings: false }
          })
        ] : []),
      ],
    }))
    .pipe(gulp.dest(build_dir + '/js'));
});


/*
 * Other taks
 * ~~~~~~~~~~
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
    .pipe(gulp.dest(build_dir + '/js'))
});
gulp.task('build-videojs-css', function() {
  return gulp.src(bower_dir + '/video.js/dist/video-js.min.css')
    .pipe(rename('videojs.css'))
    .pipe(gulp.dest(build_dir + '/css'));
});
gulp.task('build-videojs', ['build-videojs-js', 'build-videojs-css', ]);

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
    .pipe(gulp.dest(build_dir + '/js'))
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
 * Global taks
 * ~~~~~~~~~~~
 */

gulp.task('build', [
  'build-modernizr', 'build-iconfont', 'build-videojs', 'build-pdfjs',
  'build-css-applications', 'build-js-applications',
]);
