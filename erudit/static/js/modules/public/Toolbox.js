import QuoteModal from './Quote';
import ShareModal from './Share';

class Toolbox {

  constructor(el) {
    this.el = el;
    this.init();
  }

  init() {

    this.quote = new QuoteModal( this.el.find('#tool-quote') );
    this.share = new ShareModal( this.el.find('#tool-share') );
  }

}

export default Toolbox;
