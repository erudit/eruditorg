var gulp          = require('gulp'),
    rename        = require('gulp-rename'),
    sass          = require('gulp-sass'),
    concat        = require('gulp-concat'),
    iconfont      = require('gulp-iconfont'),
    consolidate   = require('gulp-consolidate')
    path          = require('path'),
    livereload    = require('gulp-livereload'),
    env           = require('gulp-env');

// get env variables
env(".env");

/* DIRS */
var static_dir = '../../erudit/static/';

var css_dir = static_dir + 'css/';
var js_dir = static_dir + 'js/';
var sass_dir = static_dir + 'sass/';
var scripts_dir = static_dir + 'scripts/';
var templates_dirs  = static_dir + '../templates/';
var vendor_dir = static_dir + 'vendor/';
var iconfont_dir = static_dir + 'iconfont/';
var font_dir = static_dir + 'fonts/';

// display (or swallow?) an error in console
// also prevent error to stop the gulp watch process unless restart
function swallowError (error) {
  console.log(error.toString());
  this.emit('end');
}

gulp.task('sass-erudit-main', function() {
  return gulp.src(sass_dir + 'main.scss')
    .pipe(sass())
    .on('error', sass.logError)
    .pipe(rename(function (path) {
      path.dirname += "/";
      path.basename += "-dev";
      path.extname = ".css";
    }))
    .pipe(gulp.dest(css_dir))
    .pipe(livereload());
});

gulp.task('sass-erudit-pdfjs', function() {
  return gulp.src(sass_dir + 'pages/pdf_viewer.scss')
    .pipe(sass())
    .on('error', sass.logError)
    .pipe(rename(function (path) {
      path.dirname += "/";
      path.basename += "-dev";
      path.extname = ".css";
    }))
    .pipe(gulp.dest(css_dir));
});

gulp.task('scripts-erudit-main', function() {
  return gulp.src([scripts_dir + '**/*.js'])
    .pipe(concat('erudit-scripts.js'))
    .pipe(rename(function (path) {
      path.dirname += "/build";
      path.basename += "-dev";
      path.extname = ".js";
    }))
    .pipe(gulp.dest(js_dir))
    .pipe(livereload());
});

gulp.task('scripts-erudit-vendors', function() {
  return gulp.src([
      vendor_dir + 'jquery/dist/jquery.min.js',
      vendor_dir + 'bootstrap-sass/assets/javascripts/bootstrap.js',
      vendor_dir + 'inline-svg/dist/inlineSVG.min.js',
      vendor_dir + 'sticky-kit/jquery.sticky-kit.js',
      vendor_dir + 'get-prefix/dist/get-prefix.js'
    ])
    .pipe(concat('erudit-vendors.js'))
    .pipe(rename(function (path) {
      path.dirname += "/build";
      path.basename += "-dev";
      path.extname = ".js";
    }))
    .pipe(gulp.dest(js_dir));
});

gulp.task('iconfont', function(){
  var runTimestamp = Math.round(Date.now()/1000);

  return gulp.src([iconfont_dir + '**/*.svg'])
    .pipe(iconfont({
      fontName: 'erudicon',
      formats: ['ttf', 'eot', 'woff', 'svg'],
      normalize: true,
      fontHeight: 1001,
      timestamp: runTimestamp
    }))
    .on('glyphs', function(glyphs, options) {
      // CSS templating, e.g. 
      gulp.src(iconfont_dir + 'template.scss')
        .pipe(consolidate('lodash', {
          glyphs: glyphs,
          fontName: 'erudicon',
          fontPath: '/static/fonts/erudicon/',
          className: 'erudicon'
        }))
        .pipe(rename('_erudicon.scss'))
        .pipe(gulp.dest(sass_dir + 'utils/'));
    })
    .pipe(gulp.dest(font_dir + 'erudicon/'));
});

gulp.task('modernizr', function(){
    var modernizr = require('gulp-modernizr');

    return gulp.src([scripts_dir + '**/*.js', sass_dir + '**/*.scss'])
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
               .pipe(rename(function (path) {
                  path.dirname += "/build";
                  path.basename += "-dev";
                  path.extname = ".js";
                }))
               .pipe(gulp.dest(js_dir));
});

gulp.task('watch', function() {

  // start live reload server
  // host null will make it work for Vagrant
  livereload.listen({ host: eval( process.env.LIVE_RELOAD_IP ) });

  // watch any less file /css directory, ** is for recursive mode
  gulp.watch(sass_dir + '**/*.scss', ['sass-erudit-main', 'sass-erudit-pdfjs', 'modernizr']);
  // watch any js file /js directory, ** is for recursive mode
  gulp.watch(scripts_dir + '**/*.js', ['scripts-erudit-main', 'scripts-erudit-vendors', 'modernizr']);
  // watch any svg file /iconfont directory, ** is for recursive mode
  gulp.watch(iconfont_dir + '**/*.svg', ['iconfont']);

  /* Trigger a live reload on any Django template changes */
  gulp.watch([templates_dirs + '**/*.html', templates_dirs + '**/*.xls']).on('change', livereload.changed);
});
