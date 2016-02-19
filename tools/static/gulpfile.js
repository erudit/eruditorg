var gulp       = require('gulp'),
    rename     = require('gulp-rename'),
    sass       = require('gulp-sass'),
    concat     = require('gulp-concat'),
    path       = require('path'),
    livereload = require('gulp-livereload'),
    env        = require('gulp-env');

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
      vendor_dir + 'bootstrap-sass/assets/javascripts/bootstrap.js'
    ])
    .pipe(concat('erudit-vendors.js'))
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
  gulp.watch(sass_dir + '**/*.scss', ['sass-erudit-main', 'sass-erudit-pdfjs']);
  // watch any js file /js directory, ** is for recursive mode
  gulp.watch(scripts_dir + '**/*.js', ['scripts-erudit-main', 'scripts-erudit-vendors']);

  /* Trigger a live reload on any Django template changes */
  gulp.watch([templates_dirs + '**/*.html', templates_dirs + '**/*.xls']).on('change', livereload.changed);
});
