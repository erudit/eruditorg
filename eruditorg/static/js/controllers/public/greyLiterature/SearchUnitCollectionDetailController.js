export default {
  init: function() {
    $('.document-extend').click(function(ev){
      ev.preventDefault();
      $(this).parents('.document').find('.description').slideDown();
      $(this).hide();
      $(this).parent().find('.document-reduce').show();
    });

    $('.document-reduce').click(function(ev){
      ev.preventDefault();
      $(this).parents('.document').find('.description').slideUp();
      $(this).hide();
      $(this).parent().find('.document-extend').show();
    });
  },
};
