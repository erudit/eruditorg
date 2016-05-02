import 'babel-polyfill';

// Forces the evaluation of jQuery and some other related code in the global context
import '!!script!jquery/dist/jquery.min';
import '!!script!bootstrap-sass/assets/javascripts/bootstrap.min';

import controllers from './controllers/public';
import modules from './modules/public';
import csrfSafeMethod from './core/csrfSafeMethod';
import DOMRouter from './core/DOMRouter';
import getCsrfToken from './core/getCsrfToken';


// Initializes the jQuery csrf setup
$.ajaxSetup({
  beforeSend: function(xhr, settings) {
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader("X-CSRFToken", getCsrfToken());
    }
  }
});


// Defines the router and initializes it!
let router = new DOMRouter(controllers);
$(document).ready(function(ev) {
  router.init();
});
