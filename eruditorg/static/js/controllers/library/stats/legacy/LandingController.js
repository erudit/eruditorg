import Select2 from 'select2/dist/js/select2.full';


export default {
  init: function() {

    let add_counter_year_onchange_event_handler = function(prefix) {
      let year_component_id = "#" + prefix + "-year";
      let format_component_id = "#" + prefix + "-format";
      console.log(format_component_id);
      $(format_component_id).change(function() {
        let format = $(format_component_id).val();
        let start_year = 2011;
        if (format == 'csv') {
          start_year = 2009;
        }

        $(year_component_id + " > option").show();
        $(year_component_id + " > option").filter(function() { return $(this).val() < start_year && $(this).val() != ""; }).hide();

        if ($(year_component_id).val() != "" && $(year_component_id).val() < start_year) {
          $(year_component_id).val(start_year);
        }

      });
    };

    add_counter_year_onchange_event_handler("id_counter_jr1");
    add_counter_year_onchange_event_handler("id_counter_jr1_goa");
  },
};
