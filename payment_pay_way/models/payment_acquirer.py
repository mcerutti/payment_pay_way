from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(
        selection_add=[('payway', 'Payway')],
        ondelete={'payway': 'set default'}
    )
    payway_commerce = fields.Char(
        string='N. commerce',
    )
    payway_public_key = fields.Char(
        string='Public Api Key',
    )
    payway_secret_key = fields.Char(
        string='Api Key',
    )
    payway_cybersource = fields.Boolean(
        'CyberSource'
    )
    product_surcharge_id = fields.Many2one(
        'product.product',
        'Product for use in financial surcharge',
        related='company_id.product_surcharge_id',
        readonly=False
    )

    @api.model
    def _get_compatible_acquirers(self, *args, currency_id=None, **kwargs):
        """ Override of payment to unlist payway acquirers when the currency is not ARS. """
        acquirers = super()._get_compatible_acquirers(*args, currency_id=currency_id, **kwargs)

        # TODO: Deberíamos forzar la moneda a ARS ??
        # currency = self.env['res.currency'].browse(currency_id).exists()
        # if currency and currency.name != 'ARS':
        #     acquirers = acquirers.filtered(lambda a: a.provider != 'payway')

        return acquirers

    def _should_build_inline_form(self, is_validation=False):
        # if self.provider != 'payway':
        #     return super()._should_build_inline_form(self, is_validation=is_validation)

        # TODO: modify for redirect integration
        return True

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'payway':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_pay_way.payment_method_payway').id

    @api.depends('provider', 'inline_form_view_id')
    def _set_default_form_provider(self):
        if self.provider == 'payway' and not self.inline_form_view_id:
            self.inline_form_view_id = self.env.ref('payment_pay_way.inline_form').id
