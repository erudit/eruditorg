import DOMRouter from './core/DOMRouter';
import ResultsController from './controllers/public/search/ResultsController';


$(document).ready(function() {
  new DOMRouter({
    'public:search:results': ResultsController,
  }).init();
});
