import modules from './modules';

import '!!script-loader!select2/dist/js/select2.full.min';

$(document).ready(function() {
  $('#id_scope_chooser').select2();
});
