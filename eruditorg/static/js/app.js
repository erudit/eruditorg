import '@babel/polyfill';

// Forces the evaluation of jQuery and some other related code in the global context
import '!!script-loader!akkordion/dist/akkordion.min';
import '!!script-loader!bootstrap-sass/assets/javascripts/bootstrap.min';
import '!!script-loader!inline-svg/dist/inlineSVG.min';

import '!!script-loader!magnific-popup/dist/jquery.magnific-popup.min';
import '!!script-loader!sticky-kit/dist/sticky-kit.min';
import '!!script-loader!clipboard-polyfill/dist/clipboard-polyfill.promise';

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
  },
  // Normally, the "X-CSRFToken" should be enough for our purpose, but
  // some proxies strip this header so it's safer to also include it in
  // the POST values.
  data: { csrfmiddlewaretoken: getCsrfToken() }
});

// Defines the router and initializes it!
let router = new DOMRouter(controllers);
$(document).ready(function(ev) {
  // Initializes the router
  router.init();
  // Initializes the scope chooser
  $('#id_scope_chooser').select2();
});
