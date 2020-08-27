import DOMRouter from './core/DOMRouter';
import LoginController from './controllers/public/LoginController';


$(document).ready(function() {
  new DOMRouter({
    'public:login': LoginController,
  }).init();
});
