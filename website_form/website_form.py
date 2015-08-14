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

class website_form(http.Controller):
        
    @http.route(['/form/<string:form>/add', ], type='http', auth="user", website=True)
    def form_add(self, form=False,model_id=False,add_menu=0, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        form = request.env['form.form'].create({'name': form,'model_id': model_id,'body':''})
        page = self.new_page(form.name)
        _logger.warning("This is form postnr %s" % (form))


               
        if add_menu:
            model, id  = request.registry["ir.model.data"].get_object_reference(request.cr, request.uid, 'website', 'main_menu')
            request.registry['website.menu'].create(request.cr, request.uid, {
                    'name': form.name,
                    'url': "/form/" + form.name,
                    'parent_id': id,
                }, context=request.context)
        
        return werkzeug.utils.redirect("/form/"+form.name)
        
    @http.route(['/form/<string:form>', ], type='http', auth="public", website=True)
    def form_view(self, form=False,**post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        form = request.env['form.form'].search([('name','=', form)])
        if request.httprequest.method == 'POST':
           
            str = []
            for key in post.keys():
                if re.match(".*_(\d+)",key):
                    str.append(post.pop(key))
            str = str.join(', ')
            
            
            for key in post.keys():
                if re.match(".*_(\d+)",key):
                    (field_name,nr) = re.split('_',key,1)
                    if form_data.get(field_name):
                        form_data[field_name].append(post.get(key))
                    else:
                        form_data[field_name] = [post.get(key)]
            for key in form_data.keys():
                if type(form_data[key]) is list:
                    form_data[key].join(', ')
            
            #post_nr = list(key for key in post.keys() if re.match(".*_(\d+)",key))
            _logger.warning("This is form postnr %s" % (form_data))
                    
            
                    
            post_keys = dict((key,post[key]) for key in post.keys() if re.match(".*_(\d+)",key))
        
                    
                        
            form_data = dict((field_name, post.pop(form.model_id.name + field_name))
                for field_name in form.fields_get().keys() if post.get(form.model_id.name + field_name))
                
            form_data['description'] = str
            object = request.env['project.issue'].create(form_data)
#            object = request.env[form.model_id].create(form_data)
            
            


        _logger.warning("This is form post %s %s" % (form,post))
        return request.render('website_form.form', {'form': form})


    @http.route(['/form/<string:form>/edit', ], type='http', auth="user", website=True)
    def form_edit(self, form=False,**post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        form = request.env['form.form'].search([('name','=', form)])
        if request.httprequest.method == 'POST':

            form_data = dict((field_name, post.pop('form.' + field_name))
                for field_name in form.fields_get().keys() if post.get('form.'+field_name))

            post_keys = list(key for key in post.keys())
            _logger.warning("This is form post %s" % (post_keys))

            form.write(form_data)


            
           
        return request.render('website_form.edit', {'form': form})



class form_form(models.Model):    
    _name = 'form.form'
    _description = 'Simple Form'
    _order = 'name'

    name = fields.Char('Name',required=True)
    model_id = fields.Many2one(comodel_name='ir.model',string='Model')
    body = fields.Text('Body')
    

