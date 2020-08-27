import DOMRouter from './core/DOMRouter';
import ConnectionLandingController from './controllers/userspace/library/connection/ConnectionLandingController';


$(document).ready(function() {
  new DOMRouter({
    'userspace:library:connection:landing': ConnectionLandingController,
  }).init();
});
