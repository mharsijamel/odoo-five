odoo.define('product_cost.preview_cost_product', function (require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');
    var _t = core._t;

    function previewCostProduct(self) {
        var move_data = self.recordData;
        var invoice_line_ids = move_data.invoice_line_ids.data.map(function(line) {
            return {
                id: line.res_id,
                product_id: line.data.product_id.res_id,
                product_name: line.data.product_id.data.display_name,
                price_unit: line.data.price_unit,
                quantity: line.data.quantity,
            };
        });

        var charge_ids = move_data.charge_ids.data.map(function(charge) {
            return {
                amount: charge.data.amount,
            };
        });

        var preview_data = {
            currency_id: move_data.currency_id.res_id,
            company_currency_id: move_data.company_currency_id.res_id,
            company_id: move_data.company_id.res_id,
            invoice_date: move_data.invoice_date,
            invoice_line_ids: invoice_line_ids,
            charge_ids: charge_ids,
        };

        return self._rpc({
            model: 'account.move',
            method: 'preview_cost_product',
            args: [preview_data],
        }).then(function (result) {
            var message = _t("Preview Cost Product Results:\n\n");
            result.forEach(function (line) {
                message += _t("Product: ") + line.product_name + "\n";
                message += _t("Cost Product: ") + line.cost_product.toFixed(2) + "\n";
                message += _t("Base Cost: ") + line.base_cost.toFixed(2) + "\n";
                message += _t("Total Charges: ") + line.total_charges.toFixed(2) + "\n\n";
            });
            self.do_notify(_t("Cost Product Preview"), message);
        });
    }

    core.action_registry.add('preview_cost_product', previewCostProduct);

    return {
        previewCostProduct: previewCostProduct,
    };
});
