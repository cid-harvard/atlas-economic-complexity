var gulp = require('gulp'),
    autoprefixer = require('gulp-autoprefixer'),
    minifycss = require('gulp-minify-css'),
    jshint = require('gulp-jshint'),
    uglify = require('gulp-uglify'),
    imagemin = require('gulp-imagemin'),
    rename = require('gulp-rename'),
    concat = require('gulp-concat'),
    notify = require('gulp-notify'),
    cache = require('gulp-cache'),
    svgmin = require('gulp-svgmin'),
    htmlmin = require('gulp-htmlmin'),
    del = require('del');

gulp.task('styles', function() {
  return gulp.src('media/css/home.css')
    .pipe(autoprefixer('last 2 version', 'safari 5', 'ie 8', 'ie 9', 'opera 12.1', 'ios 6', 'android 4'))
    .pipe(gulp.dest('media/dist/assets/css'))
    .pipe(rename({suffix: '.min'}))
    .pipe(minifycss())
    .pipe(gulp.dest('media/dist/assets/css'))
    .pipe(notify({ message: 'Styles task complete' }));
});

gulp.task('scripts', function() {
  return gulp.src('media/js/views/*.js')
    .pipe(jshint('.jshintrc'))
    .pipe(jshint.reporter('default'))
    .pipe(concat('home.js'))
    .pipe(gulp.dest('media/dist/assets/js'))
    .pipe(rename({suffix: '.min'}))
    .pipe(uglify())
    .pipe(gulp.dest('media/dist/assets/js'))
    .pipe(notify({ message: 'Scripts task complete' }));
});

gulp.task('images', function() {
  return gulp.src('media/img/**/*')
    .pipe(cache(imagemin({ optimizationLevel: 5, progressive: true, interlaced: true })))
    .pipe(gulp.dest('media/dist/assets/img'))
    .pipe(notify({ message: 'Images task complete' }));
});

// Not running right now because I was having trouble, revisit - GW
gulp.task('svg', function() {
  return gulp.src('media/img/examples/us_exports_2012.svg')
    .pipe(svgmin())
    .pipe(gulp.dest('media/dist/assets/img'))
});

gulp.task('html', function() {
  gulp.src('html/home.html')
    .pipe(htmlmin({collapseWhitespace: true}))
    .pipe(gulp.dest('media/dist'))
});

gulp.task('clean', function(cb) {
    del(['media/dist/assets/css', 'media/dist/assets/js', 'media/dist/assets/img'], cb)
});

gulp.task('default', ['clean'], function() {
    gulp.start('styles', 'scripts', 'images', 'html');
});

gulp.task('watch', function() {

  // Watch .scss files
  gulp.watch('media/css/home.css', ['styles']);

  // Watch .js files
  gulp.watch('media/js/views/*.js', ['scripts']);

  // Watch image files
  gulp.watch('media/img/**/*', ['images']);

});