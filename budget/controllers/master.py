# -*- coding: utf-8 -*-
import os
from datetime import datetime

from tg import expose
from tg import flash
from tg import redirect, config
from budget.controllers.basicMaster import *
from budget.model import *
from budget.util.common import *
from budget.widgets.master import *
import transaction

__all__ = ['CurrencyController', 'ExchangeRateController', 'FeeGroupController', 'FeeItemController', 'CompanyController',
        'LogicTeamController']


class CurrencyController(BasicMasterController):
    url = "currency"
    template = "budget.templates.master.index_currency"
    dbObj = Currency
    searchWidget = currencySearchForm
    updateWidget = currencySearchForm
    formFields = [
        "name",
        'label',
    ]


class ExchangeRateController(BasicMasterController):
    url = "exchangerate"
    template = "budget.templates.master.index_exchangerate"
    dbObj = ExchangeRate
    searchWidget = exchangeRateSearchForm
    updateWidget = exchangeRateSearchForm
    formFields = [
        "value",
        'currency_id',
        'year',
        'month'
    ]

    search_config = {
        'currency_id': ['currency_id', int]
    }


class CompanyController(BasicMasterController):
    url = "company"
    template = "budget.templates.master.index_company"
    dbObj = Company
    searchWidget = companySearchForm
    updateWidget = companyUpdateForm
    formFields = [
        "name",
        'label',
        'currency_id'
    ]


class LogicTeamController(BasicMasterController):
    url = "logicteam"
    template = "budget.templates.master.index_logicteam"
    dbObj = LogicTeam
    searchWidget = logicTeamSearchForm
    updateWidget = logicTeamUpdateForm
    formFields = [
        "name",
        'label',
        'order',
        'effect_from',
        'effect_to',
        'manager_id'
    ]


class FeeGroupController(BasicMasterController):
    url = "feegroup"
    template = "budget.templates.master.index_feegroup"
    dbObj = FeeGroup
    searchWidget = feeGroupSearchForm
    updateWidget = feeGroupUpdateForm
    formFields = [
        "name",
        'label',
        "order",
    ]


class FeeItemController(BasicMasterController):
    url = "feeitem"
    template = "budget.templates.master.index_feeitem"
    dbObj = FeeItem
    searchWidget = feeItemSearchForm
    updateWidget = feeItemUpdateForm
    formFields = [
        "name",
        'label',
        'feegroup_id',
        "order",
        'is_share',
        'type',
        'effect_from',
        'effect_to'
    ]
    search_config = {
        'feegroup_id': ['feegroup_id', int]
    }
