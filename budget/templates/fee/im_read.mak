<%inherit file="budget.templates.master"/>
<%
	from repoze.what.predicates import in_any_group,in_group,has_permission
	from budget.util.mako_filter import b,isnone
%>

<%def name="extTitle()">r-pac - Finance Budget</%def>
<%def name="extCSS()">
<link rel="stylesheet" type="text/css" href="/css/redmond/jquery-ui-1.10.1.custom.min.css" media="screen,print"/>
<link rel="stylesheet" type="text/css" href="/css/showLoading.css" media="screen,print"/>
<link rel="stylesheet" type="text/css" href="/css/custom/budget.css" media="screen,print"/>
<style type="text/css">
    
</style>

</%def>

<%def name="extJavaScript()">
<script type="text/javascript" src="/js/jquery-ui-1.10.1.custom.min.js"></script>
<script type="text/javascript" src="/js/jquery.showLoading.min.js"></script>
<script type="text/javascript" src="/js/util.js"></script>
<script type="text/javascript" src="/js/custom/fee_index.js"></script>

<script language="JavaScript" type="text/javascript">
	$(document).ready(function(){

	});
	
	
	function toCancel(){
		if(window.confirm('Are you sure to leave this page ?')){
			redirect('/fee/im');
		}
	}
	
	function toImport(){
		redirect('/fee/im_save');
	}
	
</script>
</%def>

<div id="function-menu">
    <table width="100%" cellspacing="0" cellpadding="0" border="0">
  <tbody><tr>
  	<td width="36" valign="top" align="left"><img src="/images/images/menu_start.jpg"/></td>
	<td width="64" valign="top" align="left"><a href="/fee/index"><img src="/images/images/budget_g.jpg"/></a></td>
    <td width="23" valign="top" align="left"><img height="21" width="23" src="/images/images/menu_last.jpg"/></td>
    <td valign="top" style="background:url(/images/images/menu_end.jpg) repeat-x;width:100%"></td>
  </tr>
</tbody></table>
</div>


<div class="nav-tree">Finance Budget&nbsp;&nbsp;&gt;&nbsp;&nbsp;Import Result</div>



<div style="margin:5px 0px 5px 10px;">
	<p><input type="button" value="Confirm & Import" class="btn" onclick="toImport()"/>&nbsp;<input type="button" value="Cancel Import" onclick="toCancel()" class="btn"/></p>

	<table class="gridTable budget-table" cellpadding="0" cellspacing="0" border="0">
		<thead>
			<tr>
				<th>&nbsp;</th>
				%for x in result['x_header']:
					<th style="width:150px">${x}</th>
				%endfor
			</tr>
		</thead>
		<tbody>
			%for index,y in enumerate(result['y_header']):
				<tr>
					<td class="first" style="text-align:left;">${y}</td>
					%for v in result['data'][index] : 
						<td>${v[2]|isnone}</td>
					%endfor
				</tr>
			%endfor
		</tbody>
	</table>
</div>
