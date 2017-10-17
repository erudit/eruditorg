import Select2 from 'select2/dist/js/select2.full';


export default {
  init: function() {

    let add_counter_year_onchange_event_handlers = function(prefix) {
      let year_component_id = "#" + prefix + "-year";
      let format_component_id = "#" + prefix + "-format";

      let interval_components = [
        "#" + prefix + "-year_start",
        "#" + prefix + "-year_end",
        "#" + prefix + "-month_start",
        "#" + prefix + "-month_end"
      ]

      // when an interval is selected, reset year components
      for (let index in interval_components) {
        $(interval_components[index]).change(function() {
          $(year_component_id).val("");
        });
      }

      // when year is selected, reset all interval components
      $(year_component_id).change(function() {
        for (let index in interval_components) {
          $(interval_components[index]).val("");
        }
      });

      $(format_component_id).change(function() {
        let format = $(format_component_id).val();
        let start_year = 2011;
        if (format == 'csv') {
          start_year = 2009;
        }

        // hide all options older than start_year
        $(year_component_id + " > option").show();
        $(year_component_id + " > option").filter(
          function() {
            return $(this).val() < start_year && $(this).val() != "";
          }
        ).hide();

        // set year component to lowest possible start year
        if ($(year_component_id).val() != "" && $(year_component_id).val() < start_year) {
          $(year_component_id).val(start_year);
        }

      });
    };

    add_counter_year_onchange_event_handlers("id_counter_jr1");
    add_counter_year_onchange_event_handlers("id_counter_jr1_goa");
  },
};
