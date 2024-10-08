odoo.define('bi_advance_hide_show_menu.ActionMenus', function (require) {
    "use strict";
    var session = require('web.session');

    let print_group
    let action_group
    var def_print = session.user_has_group('bi_advance_hide_show_menu.group_hide_print_btn').then(function (has_print_group) {
        print_group = has_print_group;
    });
    var def_action = session.user_has_group('bi_advance_hide_show_menu.group_hide_action_btn').then(function (has_action_group) {
         action_group = has_action_group;
    });

    const components = {
        ActionMenus: require('web.ActionMenus'),
    };

    const { patch } = require('web.utils');


    patch(components.ActionMenus.prototype, 'bi_advance_hide_show_menu.ActionMenus', {


        async willStart() {
            this._super(...arguments);
            this.actionItems = await this._setActionItems(this.props);
            this.printItems = await this._setPrintItems(this.props);
            var def_print = session.user_has_group('bi_advance_hide_show_menu.group_hide_print_btn').then(function (has_print_group) {
                print_group = has_print_group;
            });
            var def_action = session.user_has_group('bi_advance_hide_show_menu.group_hide_action_btn').then(function (has_action_group) {
                 action_group = has_action_group;
             });

            if (action_group){
                this.actionItems.length = 0;
                }
            if (print_group){
                this.printItems.length = 0;
                }
        },

        async willUpdateProps(nextProps) {
            this._super(...arguments);
            this.actionItems = await this._setActionItems(nextProps);
            this.printItems = await this._setPrintItems(nextProps);
            var def_print = session.user_has_group('bi_advance_hide_show_menu.group_hide_print_btn').then(function (has_print_group) {
                print_group = has_print_group;
            });
            var def_action = session.user_has_group('bi_advance_hide_show_menu.group_hide_action_btn').then(function (has_action_group) {
                 action_group = has_action_group;
            });
            if (action_group){
                this.actionItems.length = 0;
                }
            if (print_group){
                this.printItems.length = 0;
                }
        },

    });


});