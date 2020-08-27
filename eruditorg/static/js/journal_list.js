import DOMRouter from './core/DOMRouter';
import JournalListController from './controllers/public/journal/JournalListController';


$(document).ready(function() {
  new DOMRouter({
    'public:journal:journal_list': JournalListController,
  }).init();
});
