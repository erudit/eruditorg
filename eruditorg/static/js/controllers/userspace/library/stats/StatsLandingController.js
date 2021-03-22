export default {
    init: function() {
        this.togglePeriodFieldsets();
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
}
