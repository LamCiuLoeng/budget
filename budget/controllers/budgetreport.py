# -*- coding: utf-8 -*-
from __future__ import division

import traceback
import os
import sys
import random
import shutil
from datetime import datetime as dt

# turbogears imports
from tg import expose, redirect, validate, flash, request, response, config

# third party imports
from paste.fileapp import FileApp
from pylons.controllers.util import forward
from repoze.what import predicates, authorize
from repoze.what.predicates import not_anonymous, in_group, has_permission

from sqlalchemy import *
from sqlalchemy.sql import *

# project specific imports
from budget.lib.base import BaseController
from budget.model import *
from budget.util.common import *
from budget.util.excel_helper import *
from budget.widgets.report import *
from budget.model.logic import ERPFeeContent, SaleType

__all__ = ['BudgetReportController']

MONTHS = dict(zip(['%.2d' % i for i in range(1, 13)],
    ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'July', 'August', 'Sept', 'Oct', 'Nov', 'Dec']))


class BudgetReportController(BaseController):
    # Uncomment this line if your controller requires an authenticated user
    allow_only = authorize.not_anonymous()

    @expose('budget.templates.report.budgetreport')
    @tabFocus(tab_type = "report")
    def index(self):
        try:
            report_form = budgetReportForm
            return dict(report_form = report_form, values = {})
        except:
            traceback.print_exc()

    @expose()
    def export(self, **kw):
        if not kw:
            redirect("/budgetreport/index")
        try:
            current = dt.now()
            dateStr = current.strftime("%Y%m%d")
            fileDir = os.path.join(config.get("public_dir"), "report", dateStr)
            if not os.path.exists(fileDir):
                os.makedirs(fileDir)
            templatePath = os.path.join(config.get("public_dir"), 'TEMPLATE', "FIN_TEMPLATE.xls")
            tempFileName = os.path.join(fileDir, "tmp_%s.xls" % current.strftime("%Y%m%d%H%M%S"))
            realFileName = os.path.join(fileDir, "FIN_Budget_%s.xls" % current.strftime("%Y%m%d%H%M%S"))
            shutil.copy(templatePath, tempFileName)
            report_xls = FinBudgetExcel(templatePath = tempFileName, destinationPath = realFileName)
            data = []
            if kw:
                data = _query_result(kw)
            report_xls.inputData(data = data)
            report_xls.outputData()
            try:
                os.remove(tempFileName)
            except:
                pass
            return serveFile(unicode(realFileName))
        except:
            traceback.print_exc()
            flash("Export Fail.")
            redirect("/budgetreport/index")



    @expose('json')
    def ajax_post(self, **kw):
        teams = kw.get('logicteam_id', [])
        if type(teams) != list : teams = [teams]
        for team in teams:
            # 1. get the team's data
            params = {
                      'company_id' : kw.get('company_id', None),
                      'logicteam_id' : team,
                      'year' : kw.get('year', None),
                      'month' : kw.get('month'),
                      }

            # 2. create the excel

            # 3. Send the excel to the manager

            pass



#===============================================================================
# added by CL ,for the ERP module report
#===============================================================================
    @expose('budget.templates.report.saleindex')
    @tabFocus(tab_type = "report")
    def saleindex(self, **kw):
        try:
            report_form = saleReportForm
            return dict(report_form = report_form, values = {})
        except:
            traceback.print_exc()




    @expose()
    def saleexport(self, **kw):
        if not kw: redirect("/budgetreport/saleindex")
        company_id = kw.get('company_id', None)
        year = kw.get('year', None)
        logicteam_id = kw.get('logicteam_id', None)

        if not company_id or not year:
            flash('Please input the company or year to generate the report!')
            redirect("/budgetreport/saleindex")

        # get the data
        company = DBSession.query(Company).get(company_id)
        last_year = unicode(int(year) - 1)

        # get the exchange rate for this year and last year
        this_exrate = [company.currency.default_rate, ] * 12
        for er in DBSession.query(ExchangeRate).filter(and_(ExchangeRate.active == 0, ExchangeRate.year == year,
                                                  ExchangeRate.currency_id == company.currency_id)):
            this_exrate[int(er.month) - 1] = er.value

        last_exrate = [company.currency.default_rate, ] * 12
        for er in DBSession.query(ExchangeRate).filter(and_(ExchangeRate.active == 0, ExchangeRate.year == last_year,
                                                  ExchangeRate.currency_id == company.currency_id)):
            last_exrate[int(er.month) - 1] = er.value

        condition = [ERPFeeContent.active == 0, ERPFeeContent.company_id == company_id]
        if logicteam_id:
            condition.append(ERPFeeContent.logicteam_id == logicteam_id)
            teams = DBSession.query(LogicTeam).filter(and_(LogicTeam.id == logicteam_id, LogicTeam.for_sale == 0)).order_by(LogicTeam.order)
        else:
            teams = DBSession.query(LogicTeam).filter(LogicTeam.for_sale == 0).order_by(LogicTeam.order)

        this_year_data = DBSession.query(ERPFeeContent).filter(and_(*condition)).filter(ERPFeeContent.year == year).order_by(ERPFeeContent.logicteam_id,
                                                                                                                              ERPFeeContent.customer,
                                                                                                                              ERPFeeContent.brand,
                                                                                                                              ERPFeeContent.subline_id,
                                                                                                                              ERPFeeContent.saletype_id)
        last_year_data = DBSession.query(ERPFeeContent).filter(and_(*condition)).filter(ERPFeeContent.year == last_year).order_by(ERPFeeContent.logicteam_id,
                                                                                                                              ERPFeeContent.customer,
                                                                                                                              ERPFeeContent.brand,
                                                                                                                              ERPFeeContent.subline_id,
                                                                                                                              ERPFeeContent.saletype_id)

        # format the data
#        data = _format(resultset)
        data = _format_sale_data(last_year_data, this_year_data, teams)
        data['COMPANY'] = unicode(company)
        data['CURRENT_YEAR'] = year
        data['PAST_YEAR'] = unicode(int(year) - 1)
        data['CURRENCY'] = unicode(company.currency)
        data['LAST_RATE'] = last_exrate  # for temp ,will update
        data['THIS_RATE'] = this_exrate  # for temp ,will update

        current = dt.now()
        dateStr = current.strftime("%Y%m%d")
        fileDir = os.path.join(config.get("public_dir"), "report", dateStr)
        if not os.path.exists(fileDir): os.makedirs(fileDir)
        templatePath = os.path.join(config.get("public_dir"), 'TEMPLATE', "FIN_SALE_TEMPLATE.xls")
        tempFileName = os.path.join(fileDir, "tmp_%s.xls" % current.strftime("%Y%m%d%H%M%S"))
        realFileName = os.path.join(fileDir, "FIN_Sale_%s.xls" % current.strftime("%Y%m%d%H%M%S"))
        shutil.copy(templatePath, tempFileName)
        report_xls = FinSaleExcel(templatePath = tempFileName, destinationPath = realFileName)
        report_xls.inputData(data = data)  # fill to the excel
        report_xls.outputData()
        try:
            os.remove(tempFileName)
        except:
            pass
        return serveFile(unicode(realFileName))  # get the report file


def _query_result(kw):
    try:
        conditions = []
        teams = []
        months = []
        company_id = ''
        company = None
        year = ''

        if kw.get("company_id", False):
            company_id = int(kw.get("company_id", 0))
            company = Company.get_by_id(company_id)
            conditions.append(FeeContent.company_id == company_id)
        if kw.get("logicteam_id", False):
            logicteam_id = int(kw.get("logicteam_id", 0))
            teams = [LogicTeam.get_by_id(logicteam_id)]
            conditions.append(FeeContent.logicteam_id == logicteam_id)
        else:
            teams = LogicTeam.get_all()

        if kw.get("year", False):
            year = kw.get("year", '')
            conditions.append(FeeContent.year == year)
        if kw.get("month", False):
            m = kw.get("month", '')
            conditions.append(FeeContent.month == m)
            months = [m]
        else:
            months = ['%.2d' % i for i in range(1, 13)]

        obj = DBSession.query(FeeContent).filter(FeeContent.active == 0)
        if len(conditions):
            for condition in conditions:
                obj = obj.filter(condition)

        rows = obj.order_by(FeeContent.company_id, FeeContent.logicteam_id,
                            cast(FeeContent.year, Integer), cast(FeeContent.month, Integer), FeeContent.feeitem_id).all()

        result = dict(company_name = company.label, year = year, team_names = [], teams = [])

        feegroups = DBSession.query(FeeGroup).filter(FeeGroup.active == 0).order_by(FeeGroup.order).all()

        tmp_kw = dict(rows = rows, company_id = company_id, logicteam_id = '',
                      feeitem_id = '', year = year, month = '', exchangerate = '')

        rates = [company.get_exrate(year, m) for m in months]
        m_rates = dict(zip(months, rates))

        months_len = len(months)

        rate_data = [''] + reduce(lambda x, y: x + y,
                                  [(lambda x: [x] * 2 + [''] + [x])('Ex-Rate : %s' % str(r)) for r in rates])

        # feegroup_labels = [f.label for f in feegroups if f.label]

        months_data = ['USD'] + reduce(lambda x, y: x + y,
                                       [(lambda x: [x] * 2 + ['%'] + [x])('%s,%s' % (MONTHS.get(m), year)) for m in months])
        abf_data = [''] + ['Actual', 'Budget', 'A/B', 'Forecast'] * months_len
        result['rates'] = rate_data

        for t in teams:
            tmp_kw['logicteam_id'] = t.id
            tmp = dict(team_name = t.label, data = [])
            result['team_names'].append(t.label)
            # months
            # tmp['data'].append(['USD'] + reduce(lambda x, y: x + y, [['%s.%s' % (MONTHS.get(m), year)] * 3 for m in months]))
            tmp['data'].append(months_data)
            # A, B, F
            # tmp['data'].append([''] + ['Actual', 'Budget', 'Forecast'] * months_len)
            tmp['data'].append(abf_data)
            # Ex-Rate
            # tmp['data'].append([''] + reduce(lambda x, y: x + y, [['Ex-Rate : %s' % str(r)] * 3 for r in rates]))
            tmp['data'].append(rate_data)

            # fee group
            row_count = 2
            feegroups_loc = []
            for fi, f in enumerate(feegroups):
                # fee item
                if fi > 0:
                    tmp['data'].append([''] + ['', '', '', ''] * months_len)
                    row_count += 1
                if f.label:
                    tmp['data'].append([f.label] + ['', '', '', ''] * months_len)
                    row_count += 1
                    feegroups_loc.append(row_count)

                for item in f.items:
                    tmp_kw['feeitem_id'] = item.id
                    tmp_ms = [item.label]
                    for m in months:
                        tmp_kw['month'] = m
                        tmp_kw['exchangerate'] = m_rates.get(m)
                        tmp_ms += _get_abf(**tmp_kw)
                    tmp['data'].append(tmp_ms)
                    row_count += 1
            tmp['feegroups_loc'] = feegroups_loc
            result['teams'].append(tmp)

        return result
    except:
        traceback.print_exc()


def _get_abf(**kw):
    result = ['', '', '', '']
    exchangerate = kw.get('exchangerate', None)
    if exchangerate:
        rows = kw.get('rows', [])
        convert = lambda x: x / exchangerate if x else 0
        # pf = lambda x, y: (x - y) / abs(y) if x > 0 and y > 0 else 0
        for r in rows:
            if (r.company_id == kw.get('company_id', None) and
                r.logicteam_id == kw.get('logicteam_id', None) and
                r.feeitem_id == kw.get('feeitem_id', None) and
                r.year == kw.get('year', None) and
                r.month == kw.get('month', None)):
                aa = convert(r.actual_value)
                bb = convert(r.budget_value)
                result = [aa, bb, '', convert(r.forecast_value)]
                break
    return result




def _format_sale_data(last_year_data, this_year_data, teams):
    teamdata = {}

    for team in teams:
        teamdata[team.id] = { "team" : team.label, "data" : {}, }

    direct = DBSession.query(SaleType).filter(SaleType.name == 'DIRECT_SALES').one()
    inter_com = DBSession.query(SaleType).filter(SaleType.name == 'INTER_COM_SALES').one()
    inter_dept = DBSession.query(SaleType).filter(SaleType.name == 'INTER_DEPT_SALES').one()

    def _f(data, prefix):
        for r in data:
            key = '%s|%s|%s' % (r.brand, r.subline_id, r.saletype_id)

            if key in teamdata[r.logicteam_id]['data']:
                tmp = teamdata[r.logicteam_id]['data'][key]
            else:
                flag, sumup_customer, color = _check_special_customer(r.customer)
                tmp = {
                       'header' : map(unicode, [r.brand, r.subline, r.saletype]),
                       'last_sale'  : [0] * 12,  # RMB/HKD AND THE USD
                       'last_cost'  : [0] * 12,
                       'this_sale'  : [0] * 12,
                       'this_cost'  : [0] * 12,
                       'is_direct' : r.saletype_id == direct.id,
                       'is_inter_com'  : r.saletype_id == inter_com.id,
                       'is_inter_dept'  : r.saletype_id == inter_dept.id,
                       'is_special_customer' : flag,
                       'sumup_customer' : sumup_customer,
                       'customer_color' : color,
                       }

                teamdata[r.logicteam_id]['data'][key] = tmp


            tmp['%s_sale' % prefix][int(r.month) - 1] += r.actual_sale_value
            tmp['%s_cost' % prefix][int(r.month) - 1] += r.actual_cost_value

    _f(last_year_data, 'last')
    _f(this_year_data, 'this')

    return {'teamdata' : teamdata}



def _check_special_customer(customer):
    checklist = [
                 ['WAL-MART', ],
                 ['WAL-MART CANADA', ],
                 ['KOHLS', ],
                 ['PEI', ],
                 ['JAG'],
                 ['JJG'],
                 ['MBI'],
                 ['TARGET', ],
                 ['AVON', ],
                 ['AVON CA', ],
                 ['AVON OTHER COUNTRIES', ],
                 ['AVON UK', ],
                 ['SPORTS AUTHORITY', ],
                 ]
    result = [
              ('Walmart', 16),  # name + excel color index
              ('Walmart Canada', 19),
              ('KOHLS', 35),
              ('PEI', 31),
              ('JAG', 46),
              ('JJG', 50),
              ('MBI', 42),
              ('TARGET', 51),
              ('AVON', 40),
              ('AVON CA', 44),
              ('AVON OTHER COUNTRIES', 53),
              ('AVON UK', 36),
              ('SPORTS AUTHORITY', 45),
              ]

    for (cl, r) in  zip(checklist, result):
        if customer in cl : return (True, r[0], r[1])
    return (False, None, None)
