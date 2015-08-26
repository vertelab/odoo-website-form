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

class website_form_crm(http.Controller):
    @http.route(['/form/<string:form>/lead/<model("crm.lead"):lead>', ], type='http', auth="public", website=True)
    def form_lead(self, form=False, lead=False, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        form = request.env['form.form'].search([('name', '=', form)])
        
        if not form:
            _logger.info("Not Form 404")
            return request.render('website.page_404', {})            
        if not lead:
            _logger.info("Not Lead 404")
            return request.render('website.page_404', {})

# self.pool['mail.mail.statistics'].set_replied(cr, uid, mail_message_ids=message_ids, context=context)
# Sätt öppnade formulär i "replied" 
# message_ids == self.pool['mail.mail.statistics'].search([('model','=','crm.lead'),('res_id','=',lead.id)]  


        if request.httprequest.method == 'POST':
            
            form_data = request.env['form.form'].form_eval(form.model_id.model,post)
            _logger.debug("Form Data %s %s" % (form_data, post))
            
            partner = request.env['res.partner'].sudo().create({'is_company': True, 'name': form_data['partner_name'], 'email': form_data.get('email_from',''),  'phone': form_data.get('phone',''), 'mobile':form_data.get('mobile',''), 'ref': form_data.get('contact_name','') })
            form_data['partner_id'] = partner.id
            form_data['type'] = 'opportunity'
            form_data['stage_id'] = request.env.ref('crm.stage_lead1').id
            lead.sudo().write(form_data)
            
            return werkzeug.utils.redirect(form.thanks_url)

        return request.render(form.template, {'form': form, 'lead': lead})


