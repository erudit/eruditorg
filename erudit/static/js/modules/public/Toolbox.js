import QuoteModal from './Quote';
import ShareModal from './Share';

class Toolbox {

  constructor(el) {
    this.el = el;
    this.init();
  }

  init() {

  	this.el.on('click', '#tool-download', this.download);

    this.quote = new QuoteModal( this.el.find('#tool-quote') );
    this.share = new ShareModal( this.el.find('#tool-share') );
  }

  download(event) {
  	event.preventDefault();

  	window.open( $(this).data('href') );
  	return false;
  }

}

export default Toolbox;
