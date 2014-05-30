<%inherit file="budget.templates.master"/>

<%
  from repoze.what.predicates import not_anonymous, in_group, has_permission
%>

<%def name="extTitle()">r-pac - Main</%def>

<div class="main-div">
	<div id="main-content">
	    
	    
	    %if has_permission('FIN_VIEW_ALL'):
	    <div class="block">
	    	<a href="/fee/index"><img src="/images/ys.jpg" width="55" height="55" alt="" /></a>
	    	<p><a href="/fee/index">Finance Budget</a></p>
	    	<div class="block-content">The module is for the "Finance Budget" .</div>
	    </div>

		<div class="block">
	    	<a href="/erpfee/index"><img src="/images/budget.jpg" width="55" height="55" alt="" /></a>
	    	<p><a href="/erpfee/index">Sale And Cost</a></p>
	    	<div class="block-content">The module is for the "Sale And Cost" .</div>
	    </div>
	    %endif
	    
	    <div class="block">
            <a href="/file/index"><img src="/images/report_upload.jpg" width="55" height="55" alt="" /></a>
            <p><a href="/file/index">Finance Report Upload</a></p>
            <div class="block-content">The module is used to upload the finance budget report.</div>
        </div>
	</div>
</div>