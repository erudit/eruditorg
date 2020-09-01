import DOMRouter from './core/DOMRouter';
import JournalListPerDisciplinesController from './controllers/public/journal/JournalListPerDisciplinesController';


$(document).ready(function() {
  new DOMRouter({
    'public:journal:journal_list_per_disciplines': JournalListPerDisciplinesController,
  }).init();
});
