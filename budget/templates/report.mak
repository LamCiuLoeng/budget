<%inherit file="budget.templates.master"/>

<%
  from repoze.what.predicates import not_anonymous, in_group, has_permission
%>

<%def name="extTitle()">r-pac - Report</%def>

<div class="main-div">
	<div id="main-content">
	
        <div class="block">
            <a href="/budgetreport/index"><img src="/images/ys.jpg" width="55" height="55" alt="" /></a>
            <p><a href="/budgetreport/index">FIN Budget Report</a></p>
            <div class="block-content">The module is for the "FIN Budget Report" .</div>
        </div>
        
        
        <div class="block">
            <a href="/budgetreport/saleindex"><img src="/images/budget.jpg" width="55" height="55" alt="" /></a>
            <p><a href="/budgetreport/saleindex">FIN Sale &amp; Cost Report</a></p>
            <div class="block-content">The module is for the "FIN Sale &amp; Cost Report" .</div>
        </div>
	    
	</div>
</div>