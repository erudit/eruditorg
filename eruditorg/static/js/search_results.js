import ResultsController from './controllers/public/search/ResultsController';
import DOMRouter from './core/DOMRouter';


$(document).ready(function() {
  new DOMRouter({
    'public:search:results': ResultsController,
  }).init();
});
