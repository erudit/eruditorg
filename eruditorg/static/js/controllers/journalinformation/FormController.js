export class JournalInformationFormController {
  init() {
    $('#id_languages').select2();
    this.contributor_fieldset = $('fieldset[name="contributors"]');
    this.set_formset_state();
  }

  dump_fieldset() {
    var rows = $(this.contributor_fieldset).children('div[class="row"][id]');
    var instance = this;

    $(rows).each(function(row) {
      console.log("===")
      console.log("row:" + row);
      var inputs = $(instance.get_inputs($(rows)[row]));
      inputs.each(function(input_index) {
        var input = inputs[input_index];
        console.log($(input).attr('id'), $(input).val());
      });
    });

  }

  set_formset_state() {
    /*
     * Sets the state of the form in a declarative way
     */
    var instance = this;

    // add click handlers on add button
    $('#button-add-contributor').off("click").on("click", function() {
      instance.add_contributor();
      instance.set_formset_state();
    });

    // add click handlers to delete buttons
    $("button[data-action='delete']").off("click").on("click",function() {
      var row_id = $(this).parent().parent().data('object');
      instance.delete_contributor($("div[data-object='" + row_id + "']"));
      instance.set_formset_state();
    });

    // set the proper indexes on rows ans inputs
    var rows = $(this.contributor_fieldset).children('div[class="row"][id]');
    $(rows).each(function(row_idx) {
      $(this).attr('data-object', row_idx);
      $(instance.get_inputs($(this))).each(function (idx) {

        var old_id = $(this).attr('id');
        var new_id = old_id.replace(/\d+/, row_idx);
        var new_name = $(this).attr('name').replace(/\d/, row_idx);
        // fixme name of label
        //var new_label = $(new_row).find('label[for="' + old_id + '"]');
        //$(new_label).attr("for", new_id);
        $(this).attr("id", new_id);
        $(this).attr("name", new_name);
      });
    });

    // update the django management form
    var total_forms = $(this.contributor_fieldset).children('div[class="row"][id]').length;
    var initial_forms = $('input[type="hidden"][name$="id"][value]').length;
    $('#id_contributor_set-TOTAL_FORMS').val(total_forms);
    $('#id_contributor_set-INITIAL_FORMS').val(initial_forms);
  }

  clear_inputs(row) {
    var all_contributor_inputs = this.get_inputs(row);
    $(all_contributor_inputs).not('[id$="journal_information"]').not('[id$="id"]').val("");
  }

  get_inputs(row) {
    return $(row).find('input').add($(row).find('select'));
  }

  add_contributor() {
    // copy the last row and modify its inputs
    var last_row = $('fieldset[name="contributors"] > div[class="row"]:last');
    var new_row = $(last_row).clone();
    this.clear_inputs(new_row);
    $(last_row).after(new_row);
    //this.dump_fieldset();
  }

  delete_contributor(row) {
    var name = $(row).find('[id$="name"]').val();
    var confirm = window.confirm("Êtes-vous certain de vouloir retirer " + name + " de la liste des collaborateurs?");
    var url = $(this.contributor_fieldset).data('form-url');
    console.log(url);
    if (confirm) {
      var row_in_bd = false;
      var contributor_id = $(row).find('[id$="id"]').val();
      if (contributor_id !== "") {

        var instance = this;
        $.ajax({
          type: "POST",
          url: url,
          data: {"contributor_id": contributor_id},
          success: function() {
            instance.clear_inputs(row);
            if ($(this.contributor_fieldset).children('div[class="row"][id]').length > 1) {
              $(row).hide();
            }
          }
        });
      }
      // do not remove the last row
      if ($(this.contributor_fieldset).children('div[class="row"][id]').length == 1) {
        this.clear_inputs(row);
      } else {
        $(row).remove();
      }

      //this.dump_fieldset();
    }
  }

};
