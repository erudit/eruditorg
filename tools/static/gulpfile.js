var gulp       = require('gulp'),
    rename     = require('gulp-rename'),
    sass       = require('gulp-sass'),
    concat     = require('gulp-concat'),
    path       = require('path'),
    livereload = require('gulp-livereload'),
    env        = require('gulp-env');

// get env variables
env(".env");

// display (or swallow?) an error in console
// also prevent error to stop the gulp watch process unless restart
function swallowError (error) {
  console.log(error.toString());
  this.emit('end');
};

gulp.task('sass-erudit-main', function() {
  return gulp.src('../../erudit/base/static/sass/main.scss')
    .pipe(sass())
    .on('error', sass.logError)
    .pipe(rename(function (path) {
      path.dirname += "/";
      path.basename += "-dev";
      path.extname = ".css"
    }))
    .pipe(gulp.dest('../../erudit/base/static/css/'))
    .pipe(livereload());
});

gulp.task('sass-erudit-pdfjs', function() {
  return gulp.src('../../erudit/base/static/sass/pages/pdf_viewer.scss')
    .pipe(sass())
    .on('error', sass.logError)
    .pipe(rename(function (path) {
      path.dirname += "/";
      path.basename += "-dev";
      path.extname = ".css"
    }))
    .pipe(gulp.dest('../../erudit/base/static/css/'));
});

gulp.task('scripts-erudit-main', function() {
  return gulp.src(['../../erudit/base/static/scripts/**/*.js', '!../../erudit/base/static/scripts/build/**'])
    .pipe(concat('erudit-scripts.js'))
    .pipe(rename(function (path) {
      path.dirname += "/build";
      path.basename += "-dev";
      path.extname = ".js"
    }))
    .pipe(gulp.dest('../../erudit/base/static/scripts/'))
    .pipe(livereload());
});

gulp.task('scripts-erudit-vendors', function() {
  return gulp.src([
      '../../erudit/base/static/vendor/jquery/dist/jquery.min.js',
      '../../erudit/base/static/bootstrap-sass/assets/javascripts/bootstrap.js'
    ])
    .pipe(concat('erudit-vendors.js'))
    .pipe(rename(function (path) {
      path.dirname += "/build";
      path.basename += "-dev";
      path.extname = ".js"
    }))
    .pipe(gulp.dest('../../erudit/base/static/scripts/'));
});

gulp.task('watch', function() {

  // start live reload server
  // host null will make it work for Vagrant
  livereload.listen({ host: eval( process.env.LIVE_RELOAD_IP ) });

  // watch any less file /css directory, ** is for recursive mode
  gulp.watch('../../erudit/base/static/sass/**/*.scss', ['sass-erudit-main', 'sass-erudit-pdfjs']);
  // watch any js file /js directory, ** is for recursive mode
  gulp.watch('../../erudit/base/static/scripts/**/*.js', ['scripts-erudit-main', 'scripts-erudit-vendors']);

  /* Trigger a live reload on any Django template changes */
  gulp.watch('../../erudit/base/templates/**/*.html').on('change', livereload.changed);
});
