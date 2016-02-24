ROUTER.registerController('userspace:editor:form', {
  init: function() {
    var journals = $('#id_editor_form_metadata').data('journals');
    function resetContactField() {
      $("#id_contact").val("");
      $("#id_contact").find("option").hide();
    }
    $(document).ready(function() {
      resetContactField();
      $("#id_journal").change(function(){
        var journal_id = $(this).val();
        var members = journals[journal_id];
        resetContactField();
        for (len = members.length, i=0; i<len; ++i) {
          $("#id_contact").find("option[value='"+members[i]+"']").show();
        }
      });
    });
  },
});
