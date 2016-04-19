import SavedCitationList from '../../../modules/public/SavedCitationList';


export default {
  init: function() {
    // Initializes the citation list
    this.saved_citations = new SavedCitationList();
    this.saved_citations.init();
  },
};
