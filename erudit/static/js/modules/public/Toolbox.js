import CiteModal from './Cite';
import SavedCitationList from './SavedCitationList';
import ShareModal from './Share';

class Toolbox {

  constructor(el) {
    this.el = el;
    this.init();
  }

  init() {

  	this.el.on('click', '#tool-download', this.download);

    // Initializes modals
    this.citation = new CiteModal( this.el.find('#tool-quote') );
    this.share = new ShareModal( this.el.find('#tool-share') );

    // Initializes the citation list
    this.saved_citations = new SavedCitationList();
    this.saved_citations.init();
  }

  download(event) {
  	event.preventDefault();

  	window.open( $(this).data('href') );
  	return false;
  }

}

export default Toolbox;
