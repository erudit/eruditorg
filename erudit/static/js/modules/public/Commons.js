

class Commons {

  constructor() {
    this.init();
  }

  init() {
    this.scrollToTop();
    this.xhr();
  }

  /*
  * Scroll back to top of page from element
  */
  scrollToTop() {
   $('#scroll-top').on('click', function(e) {

     if( e ) {
       e.preventDefault();
       e.stopPropagation();
     }

     $('html,body').animate( { scrollTop: 0 }, 750 );
     return false;
   });
 }

 /*
  * after any XHR call
  */
  xhr() {
    $(document).ajaxComplete(function() {
      console.log("ajax call");
      // ROUTER.findControllers();
    });
  }

}

export default Commons;
