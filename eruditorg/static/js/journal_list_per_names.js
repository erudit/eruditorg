import DOMRouter from './core/DOMRouter';
import JournalListPerNamesController from './controllers/public/journal/JournalListPerNamesController';


$(document).ready(function() {
  new DOMRouter({
    'public:journal:journal_list_per_names': JournalListPerNamesController,
  }).init();
});
