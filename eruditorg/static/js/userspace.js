import './base';
import Select2 from 'select2/dist/js/select2.full.min';
import DOMRouter from './core/DOMRouter';
import controllers from './controllers/userspace';

// Defines the router and initializes it!
let router = new DOMRouter(controllers);
$(document).ready(function(ev) {
  // Initializes the router
  router.init();
  // Initializes the scope chooser
  $('#id_scope_chooser').select2();
});
