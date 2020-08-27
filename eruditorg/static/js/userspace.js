import '@babel/polyfill';

import '!!script-loader!akkordion/dist/akkordion.min';
import '!!script-loader!bootstrap-sass/assets/javascripts/bootstrap.min';
import '!!script-loader!inline-svg/dist/inlineSVG.min';

import modules from './modules';
import Select2 from 'select2/dist/js/select2.full.min';
import DOMRouter from './core/DOMRouter';

import {JournalInformationFormController} from './controllers/userspace/journalinformation/FormController';

const controllers = {
  'userspace:journalinformation:update': new JournalInformationFormController(),
};

export default controllers;

// Defines the router and initializes it!
let router = new DOMRouter(controllers);
$(document).ready(function(ev) {
  // Initializes the router
  router.init();
  // Initializes the scope chooser
  $('#id_scope_chooser').select2();
});
