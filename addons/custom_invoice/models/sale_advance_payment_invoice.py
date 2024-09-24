from odoo import models, fields, api


class SaleAdvancePaymentInv(models.TransientModel):

    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        print("order : ", order)
        invoice_id = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        invoice_id.write({
            'steg_credit': order.steg_credit,
            'sub_anme': order.sub_anme,
        })
        return invoice_id



    # def _prepare_invoice_values(self, order, name, amount, so_line):
    #     print("order : ", order)
    #     res = super()._prepare_invoice_values(order, name, amount, so_line)
    #     res['steg_credit'] = order.steg_credit
    #     res['sub_anme'] = order.sub_anme
    #     return res

    # def _prepare_invoice_values(self, order, name, amount, so_line):
    #     invoice_vals = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(order, name, amount, so_line)
    #     invoice_vals.update({
    #         'steg_credit': order.steg_credit,
    #         'sub_anme': order.sub_anme,
    #     })
    #     print("invoice_vals : ", invoice_vals)
    #
    #     return invoice_vals
