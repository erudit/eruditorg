class Commons {

  constructor() {
    this.init();
  }

  init() {
    this.scrollToTop();
    this.randomImage();
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

   /*
   * Display random campaign image
   */
   randomImage() {

     var x = Math.floor(Math.random() * 5) + 1;

     $('#campaign-banner, #campaign-sidebar').addClass('image' + x);

   }

}

export default Commons;
