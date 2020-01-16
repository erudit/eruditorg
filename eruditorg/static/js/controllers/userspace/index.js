import FormController from './editor/FormController';
import ConnectionLandingController from './library/connection/ConnectionLandingController';
import {JournalInformationFormController} from './journalinformation/FormController';

const controllers = {
  'userspace:editor:form': FormController,
  'userspace:library:connection:landing': ConnectionLandingController,
  'userspace:journalinformation:update': new JournalInformationFormController(),
};

export default controllers;
