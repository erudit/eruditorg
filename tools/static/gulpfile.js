var gulp       = require('gulp'),
    rename     = require('gulp-rename'),
    sass       = require('gulp-sass'),
    path       = require('path');

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
    .pipe(gulp.dest('../../erudit/base/static/css/'));
});

gulp.task('watch', function() {
  // watch any less file /css directory, ** is for recursive mode
  gulp.watch('../../erudit/base/static/sass/**/*.scss', ['sass-erudit-main']);
});
