export default {
  init() {
    $('.thesis-extend').click(function(ev){
      ev.preventDefault();
      $(this).parents('.thesis').find('.thesis-description').slideDown();
      $(this).hide();
      $(this).parent().find('.thesis-reduce').show();
    });

    $('.thesis-reduce').click(function(ev){
      ev.preventDefault();
      $(this).parents('.thesis').find('.thesis-description').slideUp();
      $(this).hide();
      $(this).parent().find('.thesis-extend').show();
    });
  },
};
