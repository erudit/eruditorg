import DOMRouter from './core/DOMRouter';
import AdvancedSearchController from './controllers/public/search/AdvancedSearchController';


$(document).ready(function() {
  new DOMRouter({
    'public:search:advanced-search': AdvancedSearchController,
  }).init();
});
