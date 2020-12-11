export default {
    init: function() {
        this.togglePeriodFieldsets();
        // this.setAvailableMonths();
    },

    togglePeriodFieldsets: function() {
        $('form.counter').each(function() {
            // Make sure the default value of the period radio button is "monthly".
            $(this).find('input[value="monthly"]').prop('checked', true);

            // When clicking on a period radio button...
            $(this).find('input[name$="-period_type"]').on('click', function() {
                // Hide all period fieldsets...
                $(this).closest('form.counter').find('fieldset.period').hide();
                // Show the fieldset associated with the selected period...
                $(this).closest('form.counter').find('fieldset[id$=' + $(this).val()).show();
            });
        });
    },
/*    setAvailableMonths: function() {
        $('form.counter').each(function() {
            // Helper function to enable or disable month options based on the selected year and
            // the last available month.
            var toggleAvailableMonths = function($form_group) {
                // Get the year field.
                var $year_field = $form_group.find('select[name*="year"]');
                // Get the month field.
                var $month_field = $form_group.find('select[name*="month"]');
                // Get the value of the selected year.
                var selected_year = $year_field.children("option:selected").val();
                // Get the value of the last available month.
                var end_month = $form_group.closest('form').attr('data-end-month');

                // If the selected year is the same as the current year, disable all months that
                // come after the last available month.
                if (parseInt(selected_year) === (new Date).getFullYear()) {
                    for (i = 12; i > end_month; i--) {
                        $month_field.children('option[value="' + i + '"]').prop('disabled', true);
                    }
                // Counter R5 exception, monthly reports are only available since April 2017.
                } else if (parseInt(selected_year) === 2017) {
                    for (i = 3; i > 0; i--) {
                        $month_field.children('option[value="' + i + '"]').prop('disabled', true);
                    }
                // If the selected year is lower than the current year, enable all months.
                } else if (parseInt(selected_year) < (new Date).getFullYear()) {
                    $month_field.children('option').prop('disabled', false);
                }
            };

            // Set the available months on init.
            $(this).find('fieldset[id$="monthly"] select[name*="year"]').each(function() {
                toggleAvailableMonths($(this).closest('.form-group'));
            });

            // Set the available months on change.
            $(this).find('fieldset[id$="monthly"] select[name*="year"]').on('change', function() {
                toggleAvailableMonths($(this).closest('.form-group'));
            });
        });
    },*/
}
