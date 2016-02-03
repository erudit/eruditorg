# Static tools

TODO: how to use...

### Install NPM package

  sudo npm install --save-dev

### start Gulp

  ./node_modules/.bin/gulp --gulpfile ./tools/static/gulpfile.js watch

### Overide static config in your settings_env.py

  STATICFILES_FINDERS = (
      'django.contrib.staticfiles.finders.FileSystemFinder',
      'django.contrib.staticfiles.finders.AppDirectoriesFinder',
      'pipeline.finders.PipelineFinder',
  )

  STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

### Collect static without copying dev css files

  ./erudit/manage.py collectstatic -i main.css
