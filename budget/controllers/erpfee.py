# -*- coding: utf-8 -*-
from datetime import datetime as dt
import traceback, os, sys, random
import transaction

# turbogears imports
from tg import expose, redirect, validate, flash, request, response
from tg.controllers import CUSTOM_CONTENT_TYPE

# third party imports
from paste.fileapp import FileApp
from pylons.controllers.util import forward
from repoze.what import predicates, authorize
from repoze.what.predicates import not_anonymous, in_group, has_permission
from sqlalchemy.sql.expression import and_, asc

# project specific imports
from budget.lib.base import BaseController
from budget.model import *
from budget.util.common import *
from budget.util.excel_helper import *
import budget.util.fin_helper as fin_helper
from budget.model.logic import Company, LogicTeam, Subline, SaleType, ERPFeeContent
from budget.util.oracle_helper import searchOracle
from budget.util.fin_helper import ERPInfo



__all__ = ['ERPFeeController']


class ERPFeeController(BaseController):
    # Uncomment this line if your controller requires an authenticated user
    allow_only = authorize.not_anonymous()

    @expose('budget.templates.erpfee.index')
    @tabFocus(tab_type = "main")
    def index(self, **kw):
        companies = DBSession.query(Company, Currency).filter(and_(Company.active == 0,
                                                                  Currency.active == 0,
                                                                  Company.currency_id == Currency.id,
                                                                  )).order_by(Company.name)

        subline = DBSession.query(Subline).filter(and_(Subline.active == 0)).order_by(Subline.label)
        saletype = DBSession.query(SaleType).filter(and_(SaleType.active == 0)).order_by(SaleType.label)

        result = {
                'companies' : companies,
                'subline'   : subline,
                'saletype'  : saletype,
                }

        if has_permission('FIN_VIEW_ALL'):  # if FIN team
            teams = DBSession.query(LogicTeam).filter(and_(LogicTeam.active == 0, LogicTeam.for_sale == 0)).order_by(LogicTeam.order).all()
            result['is_fin'] = True
        else:
            # get the user's belonging team
            result['is_fin'] = False
            teams = []
            try:
                mp = DBSession.query(Permission).filter(Permission.permission_name == 'MANAGER_VIEW').one()
                for g in request.identity["user"].groups:
                    if mp in g.permissions and g.logicteams:
                        teams.extend(g.logicteams)
            except:
                traceback.print_exc()
                pass
        result['teams'] = teams
        return result


    @expose("json")
    def ajax_load(self, **kw):
        company_id, team_id, year, month = gs(kw, 'company_id', 'team_id', 'year', 'month')
        records = DBSession.query(ERPFeeContent).filter(and_(ERPFeeContent.active == 0,
                                                ERPFeeContent.year == year,
                                                ERPFeeContent.month == month,
                                                ERPFeeContent.company_id == company_id,
                                                ERPFeeContent.logicteam_id == team_id,
                                                )).order_by(ERPFeeContent.create_time)

        _f = lambda v: None if v is None else unicode(v)

        company = DBSession.query(Company).get(company_id)
        try:
            rateobj = DBSession.query(ExchangeRate).filter(and_(ExchangeRate.currency_id == company.currency_id,
                                                  ExchangeRate.year == year,
                                                  ExchangeRate.month == month)).one()
            rate = rateobj.value
        except:
            rate = None

        result = dict(code = 0, status = None, data = [],
                      exchangerate = rate, currency = company.currency.label,
                      currency_id = company.currency_id)

        if records.count() > 0:
            result['status'] = records[0].status

        for d in records:
            result['data'].append({
                    'id' : d.id,
                    'customer' : d.customer,
                    'brand' : d.brand,
                    'subline_id' : d.subline_id,
                    'saletype_id' : d.saletype_id,
                    'actual_sale_value' : d.actual_sale_value,
                    'actual_cost_value' : d.actual_cost_value,
                    'budget_sale_value' : d.budget_sale_value,
                    'budget_cost_value' : d.budget_cost_value,
                    'forecast_sale_value' : d.forecast_sale_value,
                    'forecast_cost_value' : d.forecast_cost_value,
                  })

        return result





    @expose("json")
    def ajax_save(self, **kw):
        company_id, team_id, year, month = gs(kw, 'company_id', 'team_id', 'year', 'month')

        try:
            records = DBSession.query(ERPFeeContent).filter(and_(ERPFeeContent.active == 0,
                                                    ERPFeeContent.year == year,
                                                    ERPFeeContent.month == month,
                                                    ERPFeeContent.company_id == company_id,
                                                    ERPFeeContent.logicteam_id == team_id,
                                                    )).order_by(ERPFeeContent.create_time)


            existing = {}
            newrecords = {}
            for r in records : existing[unicode(r.id)] = r

            _g = lambda n : kw.get(n, None) or None

            customers = filterAndSorted('customer_', kw)
            for (cname, cval) in customers:
                if not cval : continue
                rid = cname[cname.rindex("_") + 1 :]

                if rid not in existing :  # new record:
                    params = {
                              'company_id' : company_id,
                              'logicteam_id' : team_id,
                              'year' : year,
                              'month' : month,
                              'customer' : _g('customer_' + rid),
                              'brand' : _g('brand_' + rid),
                              'subline_id' : _g('subline_id_' + rid),
                              'saletype_id' : _g('saletype_id_' + rid),
                              }
                    if has_permission('FIN_VIEW_ALL'):  # if FIN team
                        params.update({
                                       'actual_sale_value' : _g('actual_sale_value_' + rid),
                                       'actual_cost_value' : _g('actual_cost_value_' + rid),
                                       'budget_sale_value' : _g('budget_sale_value_' + rid),
                                       'budget_cost_value' : _g('budget_cost_value_' + rid)
                                       })
                    else:
                        params.update({
                                       'forecast_sale_value' : _g('forecast_sale_value_' + rid),
                                       'forecast_cost_value' : _g('forecast_cost_value_' + rid),
                                       })
                    obj = ERPFeeContent(**params)
                    DBSession.add(obj)
                    newrecords[rid] = obj
                else:  # existing ,should be update the record
                    obj = existing[rid]
                    attrs = ['customer', 'brand', 'subline_id', 'saletype_id', ]
                    if has_permission('FIN_VIEW_ALL'): attrs.extend(['actual_sale_value', 'actual_cost_value', 'budget_sale_value', 'budget_cost_value'])
                    else : attrs.extend(['forecast_sale_value', 'forecast_cost_value'])
                    for attr in attrs :
                        setattr(obj, attr, _g('%s_%s' % (attr, rid)))
                    existing.pop(rid)

            if len(existing.keys()) > 0:  # delete the existing records
                DBSession.query(ERPFeeContent).filter(ERPFeeContent.id.in_(existing.keys())).update({'active' : 1})

            DBSession.flush()

            return {
                    'code': 0,
                    'status' : STATUS_SAVED,
                    'newrecords' : [{'old_id' : k, 'new_id' : v.id} for (k, v) in newrecords.items()]
                    }
        except:
            traceback.print_exc()
            transaction.doom()
            return {'code': 1}


    @expose('json')
    def ajax_search_customer(self, **kw):
        term = kw.get('term', None) or None
        if not term : return {'data' : []}
        customer_list = ERPInfo.search_customer(term)
        return {'data' : customer_list}


    @expose('json')
    def ajax_search_brand(self, **kw):
        customer = kw.get('customer', None) or None
        term = kw.get('term', None) or None
        if not customer or not term: return {'data' : []}

        brand_list = ERPInfo.search_brand(customer, term)
        return {'data' : brand_list}



    @expose('json')
    def ajax_mark(self, **kw):
        company_id, team_id, year, month, status = gs(kw, 'company_id', 'team_id', 'year', 'month', 'status')
        try:
            records = DBSession.query(ERPFeeContent).filter(and_(ERPFeeContent.active == 0,
                                                       ERPFeeContent.company_id == company_id,
                                                       ERPFeeContent.logicteam_id == team_id,
                                                       ERPFeeContent.year == year,
                                                       ERPFeeContent.month == month))
            records.update({'status' : status})

            return {'code' : 0, 'status' : status}
        except:
            transaction.doom()
            traceback.print_exc()
            return {'code' : 1}



    @expose('json')
    def ajax_rate(self, **kw):
        try:
            DBSession.add(ExchangeRate(currency_id = kw['currency_id'],
                                       year = kw['year'], month = kw['month'],
                                       value = kw['rate']))
            return {'code' : 0}
        except:
            traceback.print_exc()
            return {'code' : 1}
