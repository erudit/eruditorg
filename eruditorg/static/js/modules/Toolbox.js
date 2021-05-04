import { InlineCiteModal, AjaxCiteModal } from './Cite';
import ShareModal from './Share';

class Toolbox {

  constructor(el) {
    this.el = el;
    this.init();
  }

  init() {

    this.el.on('click', '.tool-download', this.download);

    // Initializes modals
    this.citation = new InlineCiteModal( this.el.find('.tool-cite.inline') );
    this.citation = new AjaxCiteModal( this.el.find('.tool-cite.ajax') );
    this.share = new ShareModal( this.el.find('.tool-share') );
  }

  download(event) {
    event.preventDefault();

    window.open( $(this).data('href') );
    return false;
  }

}

export default Toolbox;
