import SavedCitationList from '../../../modules/public/SavedCitationList';
import Toolbox from '../../../modules/public/Toolbox';

export default {

  init: function() {
    this.document = $('#document');

    // Initializes the toolbox
    this.toolbox = new Toolbox(this.document);

    // Initializes the citation list
    this.saved_citations = new SavedCitationList();
    this.saved_citations.init();
  },
};
