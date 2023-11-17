import werkzeug
from odoo import http, _
from odoo.http import request
from odoo.addons.payment import utils as payment_utils
from odoo.exceptions import ValidationError
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing

class PaymentPayway(http.Controller):
    @http.route('/payment/payway/get_acquirer_info', type='json', auth='public')
    def payway_get_acquirer_info(self, rec_id, flow, net_amount=0):
        """ Return public information on the acquirer.

        :param int rec_id: The payment option handling the transaction, as a `payment.acquirer` or `payment.token` id
        :return: Information on the acquirer, namely: the state, payment method type, login ID, and
                 public client key
        :rtype: dict
        """
        if flow == "token":
            acquirer_sudo = request.env['payment.token'].browse(rec_id).acquirer_id.sudo()
        else:
            acquirer_sudo = request.env['payment.acquirer'].sudo().browse(rec_id).exists()
        return {
            'public_key': acquirer_sudo.payway_public_key,
            'base_url': acquirer_sudo.payway_get_base_url(),
            'card_tree': acquirer_sudo.payway_card_installment_tree(float(net_amount)),
            'cybersource': not acquirer_sudo.payway_cybersource,
        }

    @http.route('/payment/payway/payment', type='json', auth='public')
    def payway_payment(self, reference, partner_id, access_token=None, **kwargs):
        # Check that the transaction details have not been altered
        # if not payment_utils.check_access_token(access_token, reference, partner_id):
        #    raise ValidationError("payway: " + _("Received tampered payment request data."))

        # Make the payment request to payway
        tx_sudo = request.env['payment.transaction'].sudo().search([('reference', '=', reference)])
        tx_sudo.fees = float(kwargs['fees'])
        tx_sudo.amount += float(kwargs['fees'])

        tx_sudo.payway_payment_method = str(kwargs['payway_payment_method'])
        tx_sudo.payway_payment_instalment = int(kwargs['payway_payment_instalment'])

        response_content = tx_sudo._payway_create_transaction_request(kwargs)
        # Handle the payment request response
        feedback_data = {'reference': tx_sudo.reference, 'response': response_content}
        request.env['payment.transaction'].sudo()._handle_feedback_data('payway', feedback_data)


    @http.route('/payment/payway_confirmation', type='http', methods=['GET'], auth='public', website=True)
    def payment_confirm(self, tx_id, access_token, **kwargs):
        """ Display the payment confirmation page with the appropriate status message to the user.

        :param str tx_id: The transaction to confirm, as a `payment.transaction` id
        :param str access_token: The access token used to verify the user
        :param dict kwargs: Optional data. This parameter is not used here
        :raise: werkzeug.exceptions.NotFound if the access token is invalid
        """
        tx_id = self._cast_as_int(tx_id)
        if tx_id:
            tx_sudo = request.env['payment.transaction'].sudo().browse(tx_id)

            # Raise an HTTP 404 if the access token is invalid
            if not payment_utils.check_access_token(
                access_token, tx_sudo.partner_id.id, tx_sudo.amount - tx_sudo.fees, tx_sudo.currency_id.id
            ):
                raise werkzeug.exceptions.NotFound  # Don't leak info about existence of an id

            # Fetch the appropriate status message configured on the acquirer
            if tx_sudo.state == 'draft':
                status = 'info'
                message = tx_sudo.state_message \
                          or _("This payment has not been processed yet.")
            elif tx_sudo.state == 'pending':
                status = 'warning'
                message = tx_sudo.acquirer_id.pending_msg
            elif tx_sudo.state in ('authorized', 'done'):
                status = 'success'
                message = tx_sudo.acquirer_id.done_msg
            elif tx_sudo.state == 'cancel':
                status = 'danger'
                message = tx_sudo.acquirer_id.cancel_msg
            else:
                status = 'danger'
                message = tx_sudo.state_message \
                          or _("An error occurred during the processing of this payment.")

            # Display the payment confirmation page to the user
            PaymentPostProcessing.remove_transactions(tx_sudo)
            render_values = {
                'tx': tx_sudo,
                'status': status,
                'message': message
            }
            return request.render('payment.confirm', render_values)
        else:
            # Display the portal homepage to the user
            return request.redirect('/my/home')

    @staticmethod
    def _cast_as_int(str_value):
        """ Cast a string as an `int` and return it.

        If the conversion fails, `None` is returned instead.

        :param str str_value: The value to cast as an `int`
        :return: The casted value, possibly replaced by None if incompatible
        :rtype: int|None
        """
        try:
            return int(str_value)
        except (TypeError, ValueError, OverflowError):
            return None
