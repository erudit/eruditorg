import FormController from './editor/FormController';
import LandingController from './library/stats/legacy/LandingController';
import ConnectionLandingController from './library/connection/ConnectionLandingController';
import {JournalInformationFormController} from './journalinformation/FormController';

const controllers = {
  'userspace:editor:form': FormController,
  'userspace:library:stats:legacy:landing': LandingController,
  'userspace:library:connection:landing': ConnectionLandingController,
  'userspace:journalinformation:update': new JournalInformationFormController(),
};

export default controllers;
