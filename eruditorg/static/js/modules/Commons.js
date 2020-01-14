class Commons {

  constructor() {
    this.init();
  }

  init() {
    this.scrollToTop();
  }

  /*
  * Scroll back to top of page from element
  */
  scrollToTop() {
   $('.scroll-top').on('click', function(e) {

     if( e ) {
       e.preventDefault();
       e.stopPropagation();
     }

     $('html,body').animate( { scrollTop: 0 }, 450 );
     return false;
   });
 };
}

export default Commons;
