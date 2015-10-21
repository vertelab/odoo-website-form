# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2015 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import http
from openerp.http import request
from openerp import SUPERUSER_ID
from datetime import datetime
import werkzeug
import pytz
import re

import logging

_logger = logging.getLogger(__name__)


#  1) vid nyskapande av form satt menyvalet till /form/<string>/order
#  2) template till website_form_order.order_form
#  3) submit knapp
#  4) markera obl falt

class website_form_order(http.Controller):
    @http.route(['/form/<string:form>/order', ], type='http', auth="public", website=True)
    def form_lead(self, form=False, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        form = request.env['form.form'].search([('name', '=', form)])
        
        if not form:
            _logger.info("Not Form 404")
            return request.render('website.page_404', {})            

# self.pool['mail.mail.statistics'].set_replied(cr, uid, mail_message_ids=message_ids, context=context)
# Sätt öppnade formulär i "replied" 
# message_ids == self.pool['mail.mail.statistics'].search([('model','=','crm.lead'),('res_id','=',lead.id)]  


        if request.httprequest.method == 'POST':
            
            partner_data = request.env['form.form'].form_eval('res.partner',post)
            sale_data    = request.env['form.form'].form_eval('sale.order',post)
            line_data    = request.env['form.form'].form_eval('sale.order.line',post)
            #raise Warning('line_data %s' % line_data)
            
            partner = request.env['res.partner'].search([('email','=',partner_data['email'])],limit=1)
            if not partner:
                partner = request.env['res.partner'].sudo().create(partner_data)
            sale_data['partner_id'] = partner.id
            order = request.env['sale.order'].sudo().create(sale_data)
            line_data['order_id'] = order.id
            line_data['product_uom_qty'] = 1.0
            line_data['price_unit'] = 1.0
            line = request.env['sale.order.line'].sudo().create(line_data)
            
            
            #_logger.debug("Form Data %s %s" % (partner_data + sale_data + line_data, post))
            
            
            return request.render('website_form_order.order_thanks',{'order':order})

#        return request.render(form.template, {'form': form, 'order': order})

        return request.render('website_form_order.order_form', {'form': form, })

