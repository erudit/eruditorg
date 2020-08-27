import DOMRouter from './core/DOMRouter';
import JournalDetailController from './controllers/public/journal/JournalDetailController';


$(document).ready(function() {
  new DOMRouter({
    'public:journal:journal_detail': JournalDetailController,
  }).init();
});
