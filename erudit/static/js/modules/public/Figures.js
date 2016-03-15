import '!!script!inline-svg/dist/inlineSVG.min';

class Figures {

  constructor() {
    this.init();
  }

  init() {
    console.log("Figures init");
    this.svg();
  }

  /*
   * Register different type of modal windows
   */
  svg() {
    inlineSVG.init({
      svgSelector: 'img.inline-svg', // the class attached to all images that should be inlined
      initClass: 'js-inlinesvg', // class added to <html>
    });
  }
}

export default Figures;
