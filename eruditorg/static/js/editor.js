import DOMRouter from './core/DOMRouter';
import FormController from './controllers/userspace/editor/FormController';


$(document).ready(function() {
  new DOMRouter({
    'userspace:editor:form': FormController,
  }).init();
});
