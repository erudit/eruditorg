import CiteModal from './Cite';
import ShareModal from './Share';

class Toolbox {

  constructor(el) {
    this.el = el;
    this.init();
  }

  init() {

    this.cite  = new CiteModal( this.el.find('#tool-cite') );
    this.share = new ShareModal( this.el.find('#tool-share') );
  }

}

export default Toolbox;
