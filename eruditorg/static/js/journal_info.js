import DOMRouter from './core/DOMRouter';
import {JournalInformationFormController} from './controllers/userspace/journalinformation/FormController';


$(document).ready(function() {
  new DOMRouter({
    'userspace:journalinformation:update': new JournalInformationFormController(),
  }).init();
});
