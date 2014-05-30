# -*- coding: utf-8 -*-

from budget.model import *
from budget.widgets.components import *

__all__ = ['budgetReportForm', 'saleReportForm']


def getOptions(obj, order_by = "name", id = "id", need_blank = False):
    def _f():
        options = [((getattr(o, id)), o) for o in DBSession.query(obj).filter(obj.active == 0).order_by(getattr(obj, order_by))]
        if need_blank:
            return [('', ''), ] + options
        else: return options
    return _f


class BudgetReportForm(RPACForm):

    fields = [
        RPACSelect("company_id", label_text = "Company", options = getOptions(Company)),
        RPACSelect("year", label_text = "Year", options = (lambda x: [(y, y) for y in x])(range(2013, 2020))),
        RPACSelect("logicteam_id", label_text = "Team", options = getOptions(LogicTeam, 'order', need_blank = True)),
        RPACSelect("month", label_text = "Month", options = (lambda x: [('', '')] + [('%.2d' % m, '%.2d' % m) for m in x])(range(1, 13))),
    ]

budgetReportForm = BudgetReportForm()


def getLogicTeam():
    result = [('', ''), ]
    result.extend([(r.id, r) for r in DBSession.query(LogicTeam).filter(and_(LogicTeam.active == 0 ,
                                                                    LogicTeam.for_sale == 0)).order_by(LogicTeam.order)])
    return result




class SaleReportForm(RPACForm):

    fields = [
        RPACSelect("company_id", label_text = "Company", options = getOptions(Company)),
        RPACSelect("year", label_text = "Year", options = (lambda x: [(y, y) for y in x])(range(2013, 2020))),
        RPACSelect("logicteam_id", label_text = "Team", options = getLogicTeam,)
#        RPACSelect("month", label_text = "Month", options = (lambda x: [('', '')] + [('%.2d' % m, '%.2d' % m) for m in x])(range(1, 13))),
    ]

saleReportForm = SaleReportForm()
