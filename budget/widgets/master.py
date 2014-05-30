# -*- coding: utf-8 -*-

from budget.model import *
from budget.widgets.components import *

__all__ = ['currencySearchForm', 'exchangeRateSearchForm', 'companySearchForm', 'companyUpdateForm', 'feeGroupSearchForm',
    'companyUpdateForm', 'feeGroupUpdateForm', 'feeItemSearchForm', 'feeItemUpdateForm', 'logicTeamSearchForm',
    'logicTeamUpdateForm']


getOptions = lambda obj, order_by="name", id="id": [((getattr(o, id)), o) for o in DBSession.query(obj).filter(obj.active == 0).order_by(getattr(obj, order_by))]


class CurrencySearchForm(RPACForm):
    fields = [
        RPACText("name", label_text="Currency Name"),
        RPACText("label", label_text="Currency Label"),
    ]

currencySearchForm = CurrencySearchForm()


class ExchangeRateSearchForm(RPACForm):
    fields = [
        RPACSelect("currency_id", label_text="Currency", options=getOptions(Currency)),
        RPACText("value", label_text="Value"),
        RPACText("year", label_text="Year"),
        RPACText("month", label_text="Month"),
    ]

exchangeRateSearchForm = ExchangeRateSearchForm()


class CompanySearchForm(RPACForm):
    fields = [
        RPACText("name", label_text="Company Name"),
        RPACText("label", label_text="Company Label"),
    ]

companySearchForm = CompanySearchForm()


class CompanyUpdateForm(RPACForm):
    fields = [
        RPACText("name", label_text="Company Name"),
        RPACText("label", label_text="Company Label"),
        RPACSelect("currency_id", label_text="Currency", options=getOptions(Currency)),
    ]

companyUpdateForm = CompanyUpdateForm()


class LogicTeamSearchForm(RPACForm):
    fields = [
        RPACText("name", label_text="Logic Team Name"),
        RPACText("label", label_text="Logic Team Label"),
    ]

logicTeamSearchForm = LogicTeamSearchForm()


class LogicTeamUpdateForm(RPACForm):
    fields = [
        RPACText("name", label_text="Logic Team Name"),
        RPACText("label", label_text="Logic Team Label"),
        RPACText("order", label_text="Logic Team Order"),
        RPACText("effect_from", label_text="Effect From"),
        RPACText("effect_to", label_text="Effect To"),
        RPACSelect("manager_id", label_text="Manager", options=getOptions(Group, 'group_name', 'group_id')),
    ]

logicTeamUpdateForm = LogicTeamUpdateForm()


class FeeGroupSearchForm(RPACForm):
    fields = [
        RPACText("name", label_text="Fee Group Name"),
        RPACText("label", label_text="Fee Group Label"),
    ]

feeGroupSearchForm = FeeGroupSearchForm()


class FeeGroupUpdateForm(RPACForm):
    fields = [
        RPACText("name", label_text="Fee Group Name"),
        RPACText("label", label_text="Fee Group Label"),
        RPACText("order", label_text="Fee Group Order"),
    ]

feeGroupUpdateForm = FeeGroupUpdateForm()


class FeeItemSearchForm(RPACForm):
    fields = [
        RPACText("name", label_text="Name"),
        RPACText("label", label_text="Label"),
        RPACSelect("feegroup_id", label_text="Fee Group", options=getOptions(FeeGroup)),
    ]

feeItemSearchForm = FeeItemSearchForm()


class FeeItemUpdateForm(RPACForm):
    fields = [
        RPACText("name", label_text="Fee Item Name"),
        RPACText("label", label_text="Fee Item Label"),
        RPACSelect("feegroup_id", label_text="Fee Group", options=getOptions(FeeGroup)),
        RPACText("is_share", label_text="Is Share"),
        RPACText("order", label_text="Order"),
        RPACText("type", label_text="Type"),
        RPACText("effect_from", label_text="Effect From"),
        RPACText("effect_to", label_text="Effect To"),
    ]

feeItemUpdateForm = FeeItemUpdateForm()
