# Static tools

### Install NPM package

```
  sudo npm install --save-dev
```

### start Gulp

```
  ./node_modules/.bin/gulp --gulpfile ./tools/static/gulpfile.js watch
```

### Live reload

For live reload support in your browser from Gulp, install this Chrome Extension :

https://chrome.google.com/webstore/detail/livereload/jnihajbhpnppcggbcgedagnkighmdlei

#### Forward port in Vagrant if needed for LiveReload server

```
  config.vm.network :forwarded_port, guest: 35729, host: 35729
```
