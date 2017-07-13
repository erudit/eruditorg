import 'babel-polyfill';

// Forces the evaluation of jQuery and some other related code in the global context
import '!!script!akkordion/dist/akkordion.min.js';
import '!!script!jquery/dist/jquery.min';
import '!!script!bootstrap-sass/assets/javascripts/bootstrap.min';
import '!!script!inline-svg/dist/inlineSVG.min';

import controllers from './controllers';
import modules from './modules';

import csrfSafeMethod from './core/csrfSafeMethod';
import Select2 from 'select2/dist/js/select2.full';
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
  // Initializes the router
  router.init();
  // Initializes the scope chooser
  $('#id_scope_chooser').select2();
});
