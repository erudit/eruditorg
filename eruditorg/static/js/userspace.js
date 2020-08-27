import '@babel/polyfill';

import '!!script-loader!akkordion/dist/akkordion.min';
import '!!script-loader!bootstrap-sass/assets/javascripts/bootstrap.min';
import '!!script-loader!inline-svg/dist/inlineSVG.min';

import modules from './modules';
import Select2 from 'select2/dist/js/select2.full.min';

$(document).ready(function() {
  $('#id_scope_chooser').select2();
});
