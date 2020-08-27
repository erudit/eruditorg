import Select2 from 'select2/dist/js/select2.full.min';


export default {
  init: function() {
    $('#id_contact').select2();

    var quitConfirm = false;
    function checkUploads(ev) {
      if (quitConfirm) { return; }

      var filesUploadingCount = $('#id_submissions').data('files-uploading');
      if (!filesUploadingCount) {
        quitConfirm = true;
        return;
      }

      if(filesUploadingCount) {
        var r = confirm(gettext("Certains de vos fichiers ne sont pas complètement téléversés. Êtes-vous sûr ?"));
        if (r == true) { quitConfirm = true; }
      }

      if (quitConfirm) { return; }

      ev.preventDefault();
    }

    $('form').submit(checkUploads);
    $('a:not(form a)').click(checkUploads);
    window.onbeforeunload = checkUploads;
  },
};
