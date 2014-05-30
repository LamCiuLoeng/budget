<%inherit file="budget.templates.master"/>
<%
	from repoze.what.predicates import in_any_group,in_group,has_permission
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
<script type="text/javascript" src="/js/jquery.numeric.js"></script>
<script type="text/javascript" src="/js/jquery.showLoading.min.js"></script>
<script type="text/javascript" src="/js/util.js"></script>
<script type="text/javascript" src="/js/custom/fee_index.js"></script>

<script language="JavaScript" type="text/javascript">
	$(document).ready(function(){

	});
	
	function toSave(){
		var msg = [];
		if(!$("#company_id").val()){
			msg.push("Please select the 'Company' field!");
		}
		
		if(!$("#year").val()){
			msg.push("Please select the 'Year' field!");
		}
		
		if(!$("#month").val()){
			msg.push("Please select the 'Month' field!");
		}
		
		if(!$("#data").val()){
			msg.push("Please select the file's path!");
		}
		
		if(msg.length > 0){
			$.prompt(msg.join('<br />'),{opacity: 0.6,prefix:'cleanred'});			
		}else{	
			$("form").submit();
		}
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


<div class="nav-tree">Finance Budget&nbsp;&nbsp;&gt;&nbsp;&nbsp;Import</div>


<form method="POST" enctype="multipart/form-data" action="/fee/im_read">
<div style="width:1400px;margin:0px;">
	<div class="case-list-one">
		<ul>
    		<li class="label"><label class="fieldlabel">Company</label></li>
			<li>
				<select name="company_id" id="company_id" style="width:250px">
					<option value="">--- Select Company ---</option>
					%for (company,currency) in companies:
						<option value="${company.id}" currency="${currency.label}">${company.label}</option>
					%endfor
				</select>
			</li>
		</ul>
	</div>	
	<div class="case-list-one">
		<ul>
    		<li class="label"><label class="fieldlabel">Date</label></li>
    		<li>
    			<select name="year" id="year" style="width:100px">
					<option value="">-- Year --</option>
					%for y in range(2013,2020):
						<option value="${y}">${y}</option>
					%endfor
				</select>
				<select name="month" id="month" style="width:100px">
					<option value="">-- Month --</option>
					%for m in range(1,13):
						<option value="${'%.2d' %m}">${'%.2d' %m}</option>
					%endfor
				</select>
			</li>
    	</ul>

	</div>
	<br class="clear"/>
	
	<div style="margin:5px 0px 5px 10px">
	<p><input type="file" id="data" name="data" size="50"/>&nbsp;&nbsp;<input type="button" value="Upload" onclick="toSave()" class="btn"/></p>
	</div>
	</div>
</div>
</form>