odoo.define('supplier_evaluation.web_widget_color', function(require) {
    "use strict";

    var field_registry = require('web.field_registry');
    var fields = require('web.basic_fields');

    var FieldCharColor = fields.FieldChar.extend({

        template: 'FieldCharColor',
        widget_class: 'oe_form_field_char_color',

        _renderReadonly: function () {
            var show_value = this._formatValue(this.value);
            this.$el.text(show_value);
            if (show_value == 'A'){
                this.$el.addClass('green_color_class');
            } else if (show_value === 'B') {
                this.$el.addClass('yellow_color_class');
            } else if (show_value === 'C' || show_value === 'D') {
                this.$el.addClass('red_color_class');
            }

        },

    });

        field_registry
        .add('charcolor', FieldCharColor);




return {
    FieldCharColor: FieldCharColor
};


});
