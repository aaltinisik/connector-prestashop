# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.connector.event import on_record_create, on_record_write
from openerp.addons.connector_prestashop.unit.exporter import (
    export_record,
    PrestashopExporter,
    TranslationPrestashopExporter,
)
from openerp.addons.connector_prestashop.unit.mapper import \
    TranslationPrestashopExportMapper
from openerp.addons.connector_prestashop.backend import prestashop
from openerp.addons.connector.unit.mapper import mapping


@on_record_create(model_names='prestashop.product.feature')
def prestashop_product_feature_created(
        session, model_name, record_id, fields=None):
    if session.context.get('connector_no_export'):
        return
    export_record.delay(session, model_name, record_id, priority=20)


@on_record_create(model_names='prestashop.product.feature.value')
def prestashop_product_feature_value_created(
        session, model_name, record_id, fields=None):
    if session.context.get('connector_no_export'):
        return
    export_record.delay(session, model_name, record_id, priority=20)


@on_record_write(model_names='prestashop.product.feature')
def prestashop_product_feature_written(session, model_name, record_id,
                                         fields=None):
    if session.context.get('connector_no_export'):
        return
    export_record.delay(session, model_name, record_id, priority=20)


@on_record_write(model_names='prestashop.product.feature.value')
def prestashop_attribute_option_written(session, model_name, record_id,
                                        fields=None):
    if session.context.get('connector_no_export'):
        return
    export_record.delay(session, model_name, record_id, priority=20)


@on_record_write(model_names='product.feature')
def product_feature_written(session, model_name, record_id, fields=None):
    if session.context.get('connector_no_export'):
        return
    model = session.pool.get(model_name)
    record = model.browse(session.cr, session.uid,
                          record_id, context=session.context)
    for binding in record.prestashop_bind_ids:
        export_record.delay(session, 'prestashop.product.feature',
                            binding.id, fields, priority=20)


@on_record_write(model_names='product.feature.value')
def attribute_option_written(session, model_name, record_id, fields=None):
    if session.context.get('connector_no_export'):
        return
    model = session.pool.get(model_name)
    record = model.browse(session.cr, session.uid,
                          record_id, context=session.context)
    for binding in record.prestashop_bind_ids:
        export_record.delay(session,
                            'prestashop.product.feature.value',
                            binding.id, fields, priority=20)


@prestashop
class ProductFeatureExport(PrestashopExporter):
    _model_name = 'prestashop.product.feature'

    def _create(self, record):
        res = super(ProductFeatureExport, self)._create(record)
        return res['prestashop']['product_feature']['id']


@prestashop
class ProductFeatureExportMapper(TranslationPrestashopExportMapper):
    _model_name = 'prestashop.product.feature'

    direct = [
        ('prestashop_position', 'position')
    ]

    @mapping
    def translatable_fields(self, record):
        translatable_fields = [
            ('name', 'name')
        ]
        trans = TranslationPrestashopExporter(self.connector_env)
        translated_fields = self.convert_languages(
            trans.get_record_by_lang(record.id), translatable_fields)
        return translated_fields


@prestashop
class ProductFeatureValueExport(PrestashopExporter):
    _model_name = 'prestashop.product.feature.value'

    def _create(self, record):
        res = super(ProductFeatureValueExport, self)._create(record)
        return res['prestashop']['product_feature_value']['id']

    def _export_dependencies(self):
        """ Export the dependencies for the record"""
        feature_id = self.erp_record.feature_id.id
        # export product feature
        binder = self.binder_for('prestashop.product.feature')
        if not binder.to_backend(feature_id, wrap=True):
            exporter = self.get_connector_unit_for_model(
                PrestashopExporter,
                'prestashop.product.feature')
            exporter.run(feature_id)
        return


@prestashop
class ProductFeatureValueExportMapper(
        TranslationPrestashopExportMapper):
    _model_name = 'prestashop.product.feature.value'

    #direct = [('name', 'value')]

#     @mapping
#     def prestashop_product_feature_id(self, record):
#         feature_binder = self.binder_for(
#             'prestashop.product.feature.value')
#         return {
#             'id_feature': feature_binder.to_backend(
#                 record.feature_id.id, wrap=True)
#         }

    @mapping
    def prestashop_product_feature_id(self, record):
        feature_binder = self.binder_for(
            'prestashop.product.feature')
        return {
            'id_feature': feature_binder.to_backend(
                record.feature_id.id, wrap=True),
        }

    @mapping
    def translatable_fields(self, record):
        translatable_fields = [
            ('name', 'value'),
        ]
        trans = TranslationPrestashopExporter(self.connector_env)
        translated_fields = self.convert_languages(
            trans.get_record_by_lang(record.id), translatable_fields)
        return translated_fields
