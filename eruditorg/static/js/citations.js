import DOMRouter from './core/DOMRouter';
import SavedCitationListController from './controllers/public/citations/SavedCitationListController';


$(document).ready(function() {
  new DOMRouter({
    'public:citations:list': SavedCitationListController,
  }).init();
});

