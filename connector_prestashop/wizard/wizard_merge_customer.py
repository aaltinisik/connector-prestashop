# -*- encoding: utf-8 -*-
#
#Created on Nov 22, 2019
#
#@author: dogan
#

from openerp import models, api, fields, exceptions


class WizardMergeNewCustomer(models.TransientModel):
    _name = 'prestashop.wizard.merge_customer.field'
    
    wizard_id = fields.Many2one('prestashop.wizard.merge_customer')
    field_id = fields.Many2one('ir.model.fields')
    

class WizardMergeNewCustomer(models.TransientModel):
    _name = 'prestashop.wizard.merge_customer'
    
    @api.model
    def _default_new_customer_id(self):
        selected_partner_id = self.env.context.get('active_id',False)
        if not selected_partner_id:
            raise exceptions.ValidationError(
                _("Error! No record is selected.")
            ) 
        
        return self.env['res.partner'].search([('id','=', selected_partner_id)])
        
    source_partner_id = fields.Many2one('res.partner',string='New Customer',default=_default_new_customer_id, readonly=True)
    target_partner_id = fields.Many2one('res.partner', string='Merge To', domain=[('parent_id','=',False)])
    update_target = fields.Boolean('Update Target Partner', default=False)
    #changed_field_ids = fields.One2many('prestashop.wizard.merge_customer.field', 'wizard_id', string='Changed Fields')
    
    @api.multi
    def action_merge(self):
        self.ensure_one()
        #self.source_partner_id.prestashop_bind_ids.write({'odoo_id': self.target_partner_id.id})
        child_ids = self.source_partner_id.child_ids
        partner_ids = [self.source_partner_id.id, self.target_partner_id.id]
#         wizard_defaults = {
#             'state':'selection',
#             'partner_ids':partner_ids,
#             'dst_partner_id':self.target_partner_id.id
#             }
#         
        partner_merge_wizard = self.pool.get('base.partner.merge.automatic.wizard')
        #wizard_id = partner_merge_wizard.create(self.env.cr, self.env.uid, wizard_defaults)
        context = dict(self.env.context)
        context.update({'no_update_values':self.update_target})
        partner_merge_wizard._merge(self.env.cr, self.env.uid, partner_ids, dst_partner=self.target_partner_id,context=context )
        
        self.target_partner_id.ps_new_customer = False
        child_ids.write({'ps_new_customer':False})
        
        
        