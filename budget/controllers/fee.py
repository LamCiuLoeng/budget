# -*- coding: utf-8 -*-
from datetime import datetime as dt
import traceback, os, sys, random
import transaction

# turbogears imports
from tg import expose, redirect, validate, flash, request, response, session

# third party imports

from repoze.what import predicates, authorize
from repoze.what.predicates import not_anonymous, in_group, has_permission
from sqlalchemy.sql.expression import and_, asc

# project specific imports
from budget.lib.base import BaseController
from budget.model import *
from budget.util.common import *
from budget.util.excel_helper import *
import budget.util.fin_helper as fin_helper
from budget.model.logic import FeeGroup, Company, LogicTeam, FeeContent
from budget.util.fin_helper import round2int


__all__ = ['FeeController']


class FeeController(BaseController):
    # Uncomment this line if your controller requires an authenticated user
    allow_only = authorize.not_anonymous()


    @expose('budget.templates.fee.index')
    @tabFocus(tab_type = "main")
    def index(self, **kw):
        feegrouups = DBSession.query(FeeGroup).filter(FeeGroup.active == 0).order_by(FeeGroup.order)
        companies = DBSession.query(Company, Currency).filter(and_(Company.active == 0,
                                                                  Currency.active == 0,
                                                                  Company.currency_id == Currency.id,
                                                                  )).order_by(Company.name)

        result = {
                'feegroups' : feegrouups,
                'companies' : companies,
                'is_fin' : has_permission('FIN_VIEW_ALL'),
                }

        if has_permission('FIN_VIEW_ALL'):  # if FIN team
            teams = DBSession.query(LogicTeam).filter(LogicTeam.active == 0).order_by(LogicTeam.order).all()
        else:
            # get the user's belonging team
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
        records = DBSession.query(FeeContent).filter(and_(FeeContent.active == 0,
                                                FeeContent.year == year,
                                                FeeContent.month == month,
                                                FeeContent.company_id == company_id,
                                                FeeContent.logicteam_id == team_id,
                                                ))

        _f = lambda v: None if v is None else unicode(v)
        data = []
        result = dict(code = 0)
        actual_status = None
        budget_status = None
        forecast_status = None

        if records.count() < 1:  # no records
            actual_status = budget_status = forecast_status = None

        else:
            for d in records:
                data.append({
                          'feeitem_id': d.feeitem_id,
                          'actual_value': _f(d.actual_value),
                          'actual_status' : d.actual_status,
                          'budget_value': _f(d.budget_value),
                          'budget_status' : d.budget_status,
                          'forecast_value': _f(d.forecast_value),
                          'forecast_status' : d.forecast_status,
                          })

                actual_status, budget_status, forecast_status = d.actual_status, d.budget_status, d.forecast_status

        result['data'] = data
        result['actual_status'] = actual_status
        result['budget_status'] = budget_status
        result['forecast_status'] = forecast_status

        return result



    @expose("json")
    def ajax_save(self, **kw):
        company_id, team_id, year, month = gs(kw, 'company_id', 'team_id', 'year', 'month')

        context = {
                   'company_id' : company_id, 'logicteam_id' : team_id,
                   'year' : year, 'month' : month,
                   }
        done_rs = {}  # to add the finish cal records
        notdone_rs = []  # to add the not yet finish cal records

        try:
            records = DBSession.query(FeeContent).filter(and_(FeeContent.active == 0,
                                                    FeeContent.year == year,
                                                    FeeContent.month == month,
                                                    FeeContent.company_id == company_id,
                                                    FeeContent.logicteam_id == team_id,
                                                    ))

            if records.count() < 1:  # no record before, should create new record

                if has_permission('FIN_VIEW_ALL'):  # if FIN team
                    actual_values = filterAndSorted('a_', kw)
                    budget_values = filterAndSorted('b_', kw)
                    for (aname, aval), (bname, bval) in zip(actual_values, budget_values):
                        tmp, feeitem_id, flag = aname.split("_")
                        obj = FeeContent(
                                         year = year, month = month, company_id = company_id, logicteam_id = team_id,
                                         feeitem_id = feeitem_id, actual_value = aval or None, budget_value = bval or None,

                                         )
                        DBSession.add(obj)
                        if flag == '0' :  done_rs[unicode(feeitem_id)] = obj
                        else : notdone_rs.append(obj)


                else:  # if the team member
                    forecast_values = filterAndSorted('f_', kw)
                    for (fname, fval) in forecast_values:
                        tmp, feeitem_id, flag = fname.split("_")
                        obj = FeeContent(
                                             year = year, month = month, company_id = company_id, logicteam_id = team_id,
                                             feeitem_id = feeitem_id, forecast_value = fval or None,
                                             )
                        DBSession.add(obj)
                        if flag == '0' :  done_rs[unicode(feeitem_id)] = obj
                        else : notdone_rs.append(obj)

            else:  # if the records exist, update the content
                mapping = {}
                for r in records: mapping[unicode(r.feeitem_id)] = r

                if has_permission('FIN_VIEW_ALL'):  # if FIN team
                    actual_values = filterAndSorted('a_', kw)
                    budget_values = filterAndSorted('b_', kw)

                    for (aname, aval), (bname, bval) in zip(actual_values, budget_values):
                        tmp, feeitem_id, flag = aname.split("_")
                        obj = mapping.get(feeitem_id, None)
                        if obj :  # if record exist, update the actual and budget value
                            obj.actual_value, obj.budget_value = aval or None, bval or None
                        else:  # if not exist, create new one
                            obj = FeeContent(
                                     year = year, month = month, company_id = company_id, logicteam_id = team_id,
                                     feeitem_id = feeitem_id, actual_value = aval or None, budget_value = bval or None,
                                     )
                            DBSession.add(obj)

                        if flag == '0' : done_rs[unicode(feeitem_id)] = obj
                        else : notdone_rs.append(obj)

                else:  # member team
                    forecast_values = filterAndSorted('f_', kw)
                    for (fname, fval) in forecast_values:
                        tmp, feeitem_id, flag = fname.split('_')
                        obj = mapping.get(feeitem_id, None)
                        if obj :  # if record exist, update the forecast value
                            obj.forecast_value = fval or None
                        else:  # if not exist, create new one
                            obj = FeeContent(
                                             year = year, month = month, company_id = company_id, logicteam_id = team_id,
                                             feeitem_id = feeitem_id, forecast_value = fval or None,
                                             )
                            DBSession.add(obj)

                        if flag == '0' : done_rs[unicode(feeitem_id)] = obj
                        else : notdone_rs.append(obj)

            updated_rs = self._cal(context , done_rs, notdone_rs)  # cal the exp
            self._acc(company_id, team_id, year)  # cal the acc value in every month

            _f = lambda v: None if v is None else unicode(v)
            result = {'code' : 0, 'updated' : []}

            actual_status = budget_status = forecast_status = None
            for r in updated_rs.values():
                result['updated'].append({
                                          'feeitem_id': r.feeitem_id,
                                          'actual_value': _f(r.actual_value),
                                          'budget_value': _f(r.budget_value),
                                          'forecast_value': _f(r.forecast_value),
                                          })
                actual_status, budget_status, forecast_status = r.actual_status, r.budget_status, r.forecast_status

            result['actual_status'] = actual_status or 0
            result['budget_status'] = budget_status or 0
            result['forecast_status'] = forecast_status or 0
            return result

        except:
            traceback.print_exc()
            transaction.doom()
            return {'code': 1}



    def _cal(self, context, done_rs, notdone_rs):
        # handle the cal fields

        updated_rs = {}
        while len(notdone_rs) > 0:
            ids_set = set(map(unicode, done_rs.keys()))
            tmp = []

            for obj in notdone_rs:
                feeitem = getattr(obj, 'feeitem', DBSession.query(FeeItem).get(obj.feeitem_id))
                args_list = map(lambda v: unicode(v.strip()), feeitem.args.split(","))

                args_ids = filter(lambda a : a.isdigit(), args_list)
                args_set = set(args_ids)
                if not args_set.issubset(ids_set):  # if not all the args is ready ,put it to the next round
                    tmp.append(obj)
                    continue
                # if all the params is fulfill ,the cal the val
                # 1. get the fomula
                fun = eval(feeitem.expression.exp)
                # 2, prepare the args value
                attrs = ['actual_value', 'budget_value'] if has_permission('FIN_VIEW_ALL') else  ['forecast_value']
                for attr in attrs:
                    vals = []
                    for a in args_list:
                        if a.isdigit() : vals.append(float(getattr(done_rs[a], attr) or 0.0))
                        elif a.startswith('$') : vals.append(context[a[1:]])
                    # 3. run the exp and set the value
                    setattr(obj, attr, fin_helper.round2int(fun(*vals)))
                done_rs[unicode(obj.feeitem_id)] = obj
                updated_rs[unicode(obj.feeitem_id)] = obj
            notdone_rs = tmp
        return updated_rs


    #===========================================================================
    # cal the  Accumulated Profit / (Loss)
    #===========================================================================
    def _acc(self, company, team, year):
        def _g(name):
            return DBSession.query(FeeContent).filter(and_(FeeContent.active == 0, FeeItem.active == 0,
                                                FeeContent.feeitem_id == FeeItem.id,
                                                FeeItem.name == name,
                                                FeeContent.company_id == company,
                                                FeeContent.logicteam_id == team,
                                                FeeContent.year == year,
                                                )).order_by(FeeContent.month).all()
        updated_rs = {}
        netprofit, accprofit = _g('NET_PROFIT'), _g('ACCUMULATED_PROFIT_LOSS')
        attrs = ['actual_value', 'budget_value'] if has_permission('FIN_VIEW_ALL') else  ['forecast_value']
        for i in range(len(netprofit)):
            for f in attrs:
                v = sum(map(lambda n : float(getattr(n, f) or 0), netprofit[:i + 1]))
                setattr(accprofit[i], f, round2int(v))
            updated_rs[unicode(accprofit[i].feeitem_id)] = accprofit[i]
        return updated_rs





    @expose('json')
    def ajax_mark(self, **kw):
        company_id, team_id, year, month, field, status = gs(kw, 'company_id', 'team_id', 'year', 'month', 'field', 'status')
        try:
            records = DBSession.query(FeeContent).filter(and_(FeeContent.active == 0,
                                                    FeeContent.year == year,
                                                    FeeContent.month == month,
                                                    FeeContent.company_id == company_id,
                                                    FeeContent.logicteam_id == team_id,
                                                    ))
            if records.count() < 1: return {'code': 1}

            actual_status = budget_status = forecast_status = None

            if not field and status == unicode(STATUS_POSTED):  # if it's post action
                records.update({'status' : STATUS_POSTED,
                                'actual_status' : STATUS_POSTED,
                                'budget_status' : STATUS_POSTED,
                                'forecast_status' : STATUS_POSTED,
                                })
                actual_status = budget_status = forecast_status = STATUS_POSTED
            else:  # if it's confirm action
                records.update({field : status})

                if field == 'actual_status':
                    actual_status = budget_status = STATUS_CONFIRMED
                else:
                    budget_status = STATUS_CONFIRMED
                    actual_status = records[0].actual_status

            return {'code' : 0,
                    'actual_status' : actual_status,
                    'budget_status' : budget_status,
                    'forecast_status' : forecast_status}
        except:
            traceback.print_exc()
            transaction.doom()
            return {'code': 1}



    @expose('budget.templates.fee.im')
    @tabFocus(tab_type = "main")
    def im(self, **kw):
        companies = DBSession.query(Company, Currency).filter(and_(Company.active == 0,
                                                                  Currency.active == 0,
                                                                  Company.currency_id == Currency.id,
                                                                  )).order_by(Company.name)
        teams = DBSession.query(LogicTeam).filter(LogicTeam.active == 0).order_by(LogicTeam.order).all()

        return {
                'companies' : companies,
                'teams' : teams,
                }


    @expose('budget.templates.fee.im_read')
    @tabFocus(tab_type = "main")
    def im_read(self, **kw):
        # 1. save the upload file
        (flag, fs) = sysUpload(attachment_list = [kw['data']], return_obj = True)
        if flag != 0 or len(fs) < 1 or not fs[0]:
            flash('Error when uploading file to the server !')
            return redirect('/fee/im')
        # 2. open the excel and parse the data
        # 3. parse the columns

        result = parseExcel(fs[0].file_path)
        result['company_id'] = kw.get('company_id', None) or None
        result['year'] = kw.get('year', None) or None
        result['month'] = kw.get('month', None) or None

        # 4, return back to page
#        if 'expense_data' in session :  del session['expense_data']
        session['expense_data'] = result
        session.save()
        return {'result' :result}


    @expose()
    def im_save(self, **kw):
        if 'expense_data' not in session :
            flash('Error ,no data imported!')
            return redirect('/fee/im')

        data = session.pop('expense_data')
        try:
            records = DBSession.query(FeeContent).filter(and_(FeeContent.active == 0,
                                                              FeeContent.company_id == data['company_id'],
                                                              FeeContent.year == data['year'],
                                                              FeeContent.month == data['month'],
                                                              ))
            existing = {}
            for r in records : existing[ '%s_%s' % (r.logicteam_id, r.feeitem_id) ] = r

            for row in data['data']:
                for d in row:
                    team_id, item_id, val = d
                    key = '%s_%s' % (team_id, item_id)
                    if key not in existing:
                        obj = FeeContent(
                                         company_id = data['company_id'],
                                         logicteam_id = team_id,
                                         year = data['year'], month = data['month'],
                                         feeitem_id = item_id,
                                         actual_value = val or 0
                                         )
                        DBSession.add(obj)
                    else:
                        obj = existing[key]
                        if obj.actual_status < STATUS_CONFIRMED: obj.actual_value = val or 0

            flash('Successfully importing the data!')
        except:
            transaction.doom()
            traceback.print_exc()
            flash('Error when importing the data!')

        return redirect('/fee/im')

