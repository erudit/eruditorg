import SavedCitationList from '../../modules/public/SavedCitationList';
import Toolbox from '../../modules/public/Toolbox';


export default {
  init() {
    console.log("Search!");

    this.toolbox();

    // Initializes the citation list
    this.saved_citations = new SavedCitationList();
    this.saved_citations.init();
  },

  toolbox() {
    $('#search-results .search-result-item .toolbox').each(function(){
      new Toolbox($(this));
    });
  }
};
