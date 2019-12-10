import './base';
import DOMRouter from './core/DOMRouter';
import controllers from './controllers/public';

// Defines the router and initializes it!
let router = new DOMRouter(controllers);
$(document).ready(function(ev) {
  // Initializes the router
  router.init();
});
