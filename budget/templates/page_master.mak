<%inherit file="budget.templates.master"/>

<%!
	from tg.flash import get_flash,get_status
	from repoze.what.predicates import not_anonymous,in_group,has_permission,has_any_permission
%>

<%def name="extTitle()">r-pac - Master</%def>

<div class="main-div">
    <div id="main-content">

        <div class="block">
            <a href="/currency/index"><img src="/images/currency.jpg" width="55" height="55" alt="" /></a>
            <p><a href="/currency/index">Currency</a></p>
            <div class="block-content">The module is the Currency master of the "FIN Budget" .</div>
        </div>

        <div class="block">
            <a href="/exchangerate/index"><img src="/images/exchangerate.jpg" width="55" height="55" alt="" /></a>
            <p><a href="/exchangerate/index">Exchange Rate</a></p>
            <div class="block-content">The module is the Exchange Rate master of the "FIN Budget" .</div>
        </div>

        <div class="block">
            <a href="/company/index"><img src="/images/company.jpg" width="55" height="55" alt="" /></a>
            <p><a href="/company/index">Company</a></p>
            <div class="block-content">The module is the Company master of the "FIN Budget" .</div>
        </div>

        <div class="block">
            <a href="/logicteam/index"><img src="/images/logicteam.jpg" width="55" height="55" alt="" /></a>
            <p><a href="/logicteam/index">Logic Team</a></p>
            <div class="block-content">The module is the Logic Team master of the "FIN Budget" .</div>
        </div>

        <div class="block">
            <a href="/businessteam/index"><img src="/images/businessteam.jpg" width="55" height="55" alt="" /></a>
            <p><a href="/businessteam/index">Business Team</a></p>
            <div class="block-content">The module is the Business Team master of the "FIN Budget" .</div>
        </div>
       
        <div class="block">
            <a href="/feegroup/index"><img src="/images/feegroup.jpg" width="55" height="55" alt="" /></a>
            <p><a href="/feegroup/index">Fee Group</a></p>
            <div class="block-content">The module is the Fee Group master of the "FIN Budget" .</div>
        </div>

        <div class="block">
            <a href="/feeitem/index"><img src="/images/feeitem.jpg" width="55" height="55" alt="" /></a>
            <p><a href="/feeitem/index">Fee Item</a></p>
            <div class="block-content">The module is the Fee Item master of the "FIN Budget" .</div>
        </div>

    </div>
</div>
