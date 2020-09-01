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
import path from 'path';
import named from 'vinyl-named';
import spritesmith from 'gulp.spritesmith';
import webpack from 'webpack';
import WebpackDevServer from 'webpack-dev-server';
import webpackStream from 'webpack-stream';
import minimist from 'minimist';
import through2 from 'through2';
import PluginError from 'plugin-error';
import log from 'fancy-log';
import analyzer from 'webpack-bundle-analyzer';


var args = minimist(process.argv.slice(2), {
  boolean: ['production', 'analyzer'],
  string: ['host', 'port'],
  default: {host: 'localhost', port: '8080'}
})

/* Global variables */
const root_dir = '../../';
const static_dir = root_dir + 'eruditorg/static/';
const templates_dirs = root_dir + 'eruditorg/templates/';
const PROD_ENV = args.production;
const WEBPACK_URL = 'http://' + args.host + ':' + args.port;

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

  entry: {
    main: [
      sass_dir + '/main.scss',
    ],
    error_pages: [
      sass_dir + '/error_pages.scss',
    ],
    home: [
      sass_dir + '/home.scss',
    ],
    brand: [
      sass_dir + '/brand.scss',
    ],
    twenty_years: [
      sass_dir + '/twenty_years.scss',
    ],
    account: [
      sass_dir + '/account.scss',
    ],
    book: [
      sass_dir + '/book.scss',
    ],
    thesis_home: [
      sass_dir + '/thesis_home.scss',
    ],
    thesis_collection_list: [
      sass_dir + '/thesis_collection_list.scss',
    ],
    thesis_collection_home: [
      sass_dir + '/thesis_collection_home.scss',
    ],
    public: [
      js_dir + '/public.js',
    ],
    userspace: [
      js_dir + '/userspace.js',
      sass_dir + '/userspace.scss',
    ],
    issue_reader: [
      js_dir + '/issue_reader.js',
      sass_dir + '/issue_reader.scss',
    ],
    login: [
      js_dir + '/login.js',
      sass_dir + '/login.scss',
    ],
    advanced_search: [
      js_dir + '/advanced_search.js',
      sass_dir + '/advanced_search.scss',
    ],
    search_results: [
      js_dir + '/search_results.js',
      sass_dir + '/search_results.scss',
    ],
    article: [
      js_dir + '/article.js',
      sass_dir + '/article.scss',
    ],
    issue: [
      js_dir + '/issue.js',
      sass_dir + '/issue.scss',
    ],
    journal: [
      js_dir + '/journal.js',
      sass_dir + '/journal.scss',
    ],
    authors_list: [
      sass_dir + '/authors_list.scss',
    ],
    journal_list_per_names: [
      js_dir + '/journal_list_per_names.js',
      sass_dir + '/journal_list_per_names.scss',
    ],
    journal_list_per_disciplines: [
      js_dir + '/journal_list_per_disciplines.js',
      sass_dir + '/journal_list_per_disciplines.scss',
    ],
    citations: [
      js_dir + '/citations.js',
      sass_dir + '/citations.scss',
    ],
    editor: [
      js_dir + '/editor.js',
    ],
    library_connection: [
      js_dir + '/library_connection.js',
    ],
    journal_info: [
      js_dir + '/journal_info.js',
    ],
    authorizations: [
      sass_dir + '/authorizations.scss',
    ],
    issue_submission: [
      sass_dir + '/issue_submission.scss',
    ],
  },
  optimization: {
    splitChunks: {
      chunks: 'all',
      minSize: 100000,
      name: function (module, chunks, cacheGroupKey) {
        return chunks.map((item) => item.name).join('-');
      },
    },
  },
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
    new analyzer.BundleAnalyzerPlugin({
      analyzerMode: args.analyzer ? 'server' : 'disabled',
      openAnalyzer: args.analyzer,
    }),
    new MiniCssExtractPlugin({
      filename: 'css/[name].css',
    })
  ],
  performance: {
    // Raise error if prod assets & entrypoints exceed max sizes (300KiB & 600KiB).
    hints: PROD_ENV ? 'error' : false,
    maxAssetSize: PROD_ENV ? 300000 : 600000,
    maxEntrypointSize: PROD_ENV ? 500000 : 1000000,
    // Only check CSS & JS files and ignore issue_reader files.
    assetFilter: function(assetFilename) {
      return (/\.(css|js)$/.test(assetFilename)) && !(/issue_reader/.test(assetFilename));
    }
  }
};


/*
 * Webpack task
 * ~~~~~~~~~~~~
 */

/* Task to build our JS and CSS applications. */
gulp.task('build-webpack-assets', function () {
  return gulp.src([
        js_dir + '/*.js', sass_dir + '/*.scss',
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
    .pipe(PROD_ENV ? uglify() : through2.obj())
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
    public: [
      js_dir + '/advanced_search.js',
      js_dir + '/article.js',
      js_dir + '/citations.js',
      js_dir + '/issue.js',
      js_dir + '/journal.js',
      js_dir + '/journal_list_per_disciplines.js',
      js_dir + '/journal_list_per_names.js',
      js_dir + '/login.js',
      js_dir + '/public.js',
      js_dir + '/search_results.js',
      sass_dir + '/account.scss',
      sass_dir + '/advanced_search.scss',
      sass_dir + '/article.scss',
      sass_dir + '/authors_list.scss',
      sass_dir + '/book.scss',
      sass_dir + '/brand.scss',
      sass_dir + '/citations.scss',
      sass_dir + '/error_pages.scss',
      sass_dir + '/home.scss',
      sass_dir + '/issue.scss',
      sass_dir + '/journal.scss',
      sass_dir + '/journal_list_per_disciplines.scss',
      sass_dir + '/journal_list_per_names.scss',
      sass_dir + '/login.scss',
      sass_dir + '/main.scss',
      sass_dir + '/search_results.scss',
      sass_dir + '/thesis_collection_home.scss',
      sass_dir + '/thesis_collection_list.scss',
      sass_dir + '/thesis_home.scss',
      sass_dir + '/twenty_years.scss',
    ],
    userspace: [
      js_dir + '/editor.js',
      js_dir + '/journal_info.js',
      js_dir + '/library_connection.js',
      js_dir + '/userspace.js',
      sass_dir + '/authorizations.scss',
      sass_dir + '/issue_submission.scss',
      sass_dir + '/userspace.scss',
    ],
    issue_reader: [
      js_dir + '/issue_reader.js',
      sass_dir + '/issue_reader.scss',
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
    publicPath: WEBPACK_URL + '/static/',
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
  }).listen(args.port, args.host, function(err) {
    if(err) throw new PluginError('webpack-dev-server', err);
    log('[webpack-dev-server]', WEBPACK_URL + '/webpack-dev-server/index.html');
  });
});

gulp.task('watch', function() {
  // start live reload server
  // host null will make it work for Vagrant
  livereload.listen();

  // watch any less file /css directory, ** is for recursive mode
  gulp.watch(sass_dir + '/**/*.scss', gulp.parallel('build-modernizr', 'build-webpack-assets'));
  // watch any js file /js directory, ** is for recursive mode
  gulp.watch(js_dir + '/**/*.js', gulp.parallel('build-webpack-assets'));
  // watch any svg file /iconfont directory, ** is for recursive mode
  gulp.watch(iconfont_dir + '/**/*.svg', gulp.parallel('build-iconfont'));

  /* Trigger a live reload on any Django template changes */
  gulp.watch([templates_dirs + '/**/*.html', templates_dirs + '**/*.xsl']).on('change', livereload.changed);
});
