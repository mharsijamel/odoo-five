odoo.define("bi_advance_hide_show_menu.HideCreateExportBtnList", function(require) {
    "use strict";

    var ListController = require('web.ListController');
    var session = require('web.session');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var _t = core._t;
    var qweb = core.qweb;
    var delete_group = false
    var export_group = false
    var def_delete = session.user_has_group('bi_advance_hide_show_menu.group_hide_delete_action').then(function (has_delete_group) {
         delete_group = has_delete_group;
     });
    var def_export_action = session.user_has_group('bi_advance_hide_show_menu.group_hide_export_action').then(function (has_export_action_group) {
        export_group = has_export_action_group;
    });

    ListController.include({
        
        willStart: function () {
            var self = this;
            var def_create = session.user_has_group('bi_advance_hide_show_menu.group_create_btn_access').then(function (has_create_group) {
                self.has_create_group = has_create_group;
            });
             var def_delete = session.user_has_group('bi_advance_hide_show_menu.group_hide_delete_action').then(function (has_delete_group) {
                 delete_group = has_delete_group;
             });
            var def_export_action = session.user_has_group('bi_advance_hide_show_menu.group_hide_export_action').then(function (has_export_action_group) {
                export_group = has_export_action_group;
            });
            var def_export_btn = session.user_has_group('bi_advance_hide_show_menu.group_export_btn_access').then(function (has_export_btn_group) {
                self.has_export_btn_group = has_export_btn_group;
            });

            return Promise.all([this._super.apply(this, arguments), def_create,def_delete, def_export_action, def_export_btn]);
        },

        updateButtons: function (mode) {
            if (this.hasButtons) {
                this.$buttons.toggleClass('o-editing', mode === 'edit');
                const state = this.model.get(this.handle, {raw: true});
                if (state.count) {
                    this.$buttons.find('.o_list_export_xlsx').show();
                } else {
                    this.$buttons.find('.o_list_export_xlsx').hide();
                }
            }
            if (this.has_create_group) {
                this.$buttons.find('.o_list_button_add').hide();
            }
            if (this.has_export_btn_group) {
                this.$buttons.find('.o_list_export_xlsx').hide();
            }
            this._updateSelectionBox();
        },

        _getActionMenuItems: function (state) {
            if (!this.hasActionMenus || !this.selectedRecords.length) {
                return null;
            }
            const props = this._super(...arguments);
            const otherActionItems = [];
            if (this.isExportEnable) {
            if (! export_group){
                otherActionItems.push({
                    description: _t("Export"),
                    callback: () => this._onExportData()
                });
            }}
            if (this.archiveEnabled) {
                otherActionItems.push({
                    description: _t("Archive"),
                    callback: () => {
                        Dialog.confirm(this, _t("Are you sure that you want to archive all the selected records?"), {
                            confirm_callback: () => this._toggleArchiveState(true),
                        });
                    }
                }, {
                    description: _t("Unarchive"),
                    callback: () => this._toggleArchiveState(false)
                });
            }

            if (this.activeActions.delete) {
            if (!delete_group){
                otherActionItems.push({
                    description: _t("Delete"),
                    callback: () => this._onDeleteSelectedRecords()
                });
            }}
            if (this.model){
                if (this.model['loadParams']){
                    if (this.model['loadParams']['modelName']=='project.project'){
                        if (! delete_group){
                            return Object.assign(props, {
                                items: Object.assign({}, this.toolbarActions, { other: otherActionItems }),
                                context: state.getContext(),
                                domain: state.getDomain(),
                                isDomainSelected: this.isDomainSelected,
                            });
                        }
                        else{
                            return Object.assign(props, {
                                items: Object.assign({}, { other: otherActionItems }),
                                context: state.getContext(),
                                domain: state.getDomain(),
                                isDomainSelected: this.isDomainSelected,
                            });
                        }
                    }
                    else{
                        return Object.assign(props, {
                            items: Object.assign({}, this.toolbarActions, { other: otherActionItems }),
                            context: state.getContext(),
                            domain: state.getDomain(),
                            isDomainSelected: this.isDomainSelected,
                        });
                    }
                }
            }
        },
    })
});



odoo.define("bi_advance_hide_show_menu.HideCreateEditBtnList", function(require) {
    "use strict";

    var FormController = require('web.FormController');
    var session = require('web.session');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var _t = core._t;
    var qweb = core.qweb;

    var delete_group = false
    var duplicate_group = false
    var def_delete = session.user_has_group('bi_advance_hide_show_menu.group_hide_delete_action').then(function (has_delete_group) {
         delete_group = has_delete_group;
     });
    var def_duplicate = session.user_has_group('bi_advance_hide_show_menu.group_hide_duplicate_action').then(function (has_duplicate_group) {
        duplicate_group = has_duplicate_group;
    });

    FormController.include({
        
        willStart: function () {
            var self = this;
            var def_create = session.user_has_group('bi_advance_hide_show_menu.group_create_btn_access').then(function (has_create_group) {
                self.has_create_group = has_create_group;
            });
            var def_edit = session.user_has_group('bi_advance_hide_show_menu.group_edit_form_btn_access').then(function (has_edit_group) {
                self.has_edit_group = has_edit_group;
            });
            var def_delete = session.user_has_group('bi_advance_hide_show_menu.group_hide_delete_action').then(function (has_delete_group) {
                 delete_group = has_delete_group;
             });
            var def_duplicate = session.user_has_group('bi_advance_hide_show_menu.group_hide_duplicate_action').then(function (has_duplicate_group) {
                duplicate_group = has_duplicate_group;
            });
            return Promise.all([this._super.apply(this, arguments), def_create, def_edit, def_delete,def_duplicate]);
        },



        _getActionMenuItems: function (state) {
            if (!this.hasActionMenus || this.mode === 'edit') {
                return null;
            }
            const props = this._super(...arguments);
            const activeField = this.model.getActiveField(state);
            const otherActionItems = [];
            if (this.archiveEnabled && activeField in state.data) {
                if (state.data[activeField]) {
                    otherActionItems.push({
                        description: _t("Archive"),
                        callback: () => {
                            Dialog.confirm(this, _t("Are you sure that you want to archive this record?"), {
                                confirm_callback: () => this._toggleArchiveState(true),
                            });
                        },
                    });
                } else {
                    otherActionItems.push({
                        description: _t("Unarchive"),
                        callback: () => this._toggleArchiveState(false),
                    });
                }
            }
            if (this.activeActions.create && this.activeActions.duplicate) {
            if (! duplicate_group){
                otherActionItems.push({
                    description: _t("Duplicate"),
                    callback: () => this._onDuplicateRecord(this),
                });
            }}

            if (this.activeActions.delete) {
                if (! delete_group){
                    otherActionItems.push({
                        description: _t("Delete"),
                        callback: () => this._onDeleteRecord(this),
                    });
            }}
            if (this.model){
                if (this.model['loadParams']){
                    if (this.model['loadParams']['modelName']=='project.project'){
                        if (! delete_group){
                            return Object.assign(props, {
                                items: Object.assign(this.toolbarActions, { other: otherActionItems }),
                            });
                        }
                        else{
                            return Object.assign(props, {
                                items: Object.assign({ other: otherActionItems }),
                            });
                        }
                    }
                    else{
                        return Object.assign(props, {
                            items: Object.assign(this.toolbarActions, { other: otherActionItems }),
                        });
                    }
                }
            }
        },
    })
});



odoo.define("bi_advance_hide_show_menu.HideCreateImportBtnKanban", function(require) {
    "use strict";

    var KanbanController = require('web.KanbanController');
    var session = require('web.session');

    KanbanController.include({
        
        willStart: function () {
            var self = this;
            var def_create = session.user_has_group('bi_advance_hide_show_menu.group_create_btn_access').then(function (has_create_group) {
                self.has_create_group = has_create_group;
            });
            return Promise.all([this._super.apply(this, arguments), def_create]);
        },
    })
});
