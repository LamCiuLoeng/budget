<%inherit file="budget.templates.master"/>
<%
	from repoze.what.predicates import in_any_group,in_group,has_permission
%>


<%def name="extTitle()">r-pac - Sale And Cost</%def>
<%def name="extCSS()">
<link rel="stylesheet" type="text/css" href="/css/redmond/jquery-ui-1.10.1.custom.min.css" media="screen,print"/>
<link rel="stylesheet" type="text/css" href="/css/showLoading.css" media="screen,print"/>
<link rel="stylesheet" type="text/css" href="/css/custom/budget.css" media="screen,print"/>

<style type="text/css">
    .first{
        border-left:1px solid #ccc;
    }
    .template{
    	display : none;
    }
    
    .addbtn{
    	display : none;
    }
    .savebtn{
    	display : none;
    }
    .postbtn{
    	display : none;
    }
</style>

</%def>

<%def name="extJavaScript()">
<script type="text/javascript" src="/js/jquery-ui-1.10.1.custom.min.js"></script>
<script type="text/javascript" src="/js/jquery.numeric.js"></script>
<script type="text/javascript" src="/js/jquery.showLoading.min.js"></script>
<script type="text/javascript" src="/js/util.js"></script>
<script type="text/javascript" src="/js/custom/erpfee_index.js"></script>

<script language="JavaScript" type="text/javascript">
	$(document).ready(function(){		
		$("#company_id,#team_id,#year,#month").change(function(){
			ajax_load();
		});
		
		$("#company_id").change(function(){ company_change(); });
		
		$(".erpfee,.feechange").numeric(false);
		
		$("#rate").numeric();
		
		$( "#dialog-form" ).dialog({
			autoOpen: false,
			height: 250,
		    width: 400,
		    modal: true,
		    buttons: {
		    	"Save" : function(){
		    	    var rate = $("#rate").val();
		    		ajax_rate(rate);
		    	},
		    	Cancel: function() {
		          $( this ).dialog( "close" );
		        }
		    }
		});

	});
	
	%if is_fin:
		var is_fin = true;
	%else:
		var is_fin = false;
	%endif
</script>
</%def>

<div id="function-menu">
    <table width="100%" cellspacing="0" cellpadding="0" border="0">
  <tbody><tr>
  	<td width="36" valign="top" align="left"><img src="/images/images/menu_start.jpg"/></td>
	<td width="64" valign="top" align="left"><a href="/erpfee/index"><img src="/images/images/sale_cost_g.jpg"/></a></td>
    <td width="23" valign="top" align="left"><img height="21" width="23" src="/images/images/menu_last.jpg"/></td>
    <td valign="top" style="background:url(/images/images/menu_end.jpg) repeat-x;width:100%"></td>
  </tr>
</tbody></table>
</div>

%if has_permission('FIN_VIEW_ALL'):
	<div class="nav-tree">Sale And Cost&nbsp;&nbsp;&gt;&nbsp;&nbsp;Actual, Budget And Forecast</div>
%else:
	<div class="nav-tree">Sale And Cost&nbsp;&nbsp;&gt;&nbsp;&nbsp;Forecast</div>
%endif



<div style="width:1800px;margin:0px;">
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
		<ul>
    		<li class="label"><label class="fieldlabel">Team</label></li>
    		<li>
    			<select name="team_id" id="team_id" style="width:250px">
					%if len(teams) > 1:
						<option value="">--- Select Team ---</option>
					%endif:
					%for t in teams:
						<option value="${t.id}">${t.label}</option>
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
		<p>
			<span class="addbtn"><input type="button" class="btn" value="Add Row" onclick="add_row()"/>&nbsp;&nbsp;</span>
			<span class="savebtn"><input type="button" class="btn" onclick="ajax_save();" value="Save"/>&nbsp;&nbsp;</span>
			<span class="postbtn"><input type="button" class="btn" onclick="ajax_mark(20);" value="Post"/>&nbsp;&nbsp;</span>
		</p>	
	
	    <table class="gridTable budget-table" cellpadding="0" cellspacing="0" border="0" style="width:1300px">
			<thead>
	          <tr>
	              <th style="width:70px;" class="first">&nbsp;</th>
	              <th style="width:200px;">Cooperate Customer</th>
                  <th style="width:150px;">Brand</th>
                  <th style="width:100px;">Subline</th>
                  <th style="width:150px;">Sale Type</th>
                  <th style="width:200px;">Actual<span class="currency"></span></th>
                  <th style="width:200px;">Budget<span class="currency"></span></th>
                  <th style="width:200px;">Forecast<span class="currency"></span></th>
	          </tr>
	      </thead>
		  <tbody>
		      <tr class="template">
		          <td class="first"><input type="button" class="btn delbtn" value="Del" onclick="remove_row(this)" style="width:50px"/></td>
		          <td><input type="text" name="customer_x" class="feefield accustomer" style="width:150px"/></td>
		          <td><input type="text" name="brand_x" class="feefield acbrand" style="width:100px"/></td>
		          <td>
		              <select name="subline_id_x" class="feefield">
		                  <option value=""></option>
		                  %for s in subline:
		                  	<option value="${s.id}">${s}</option>
		                  %endfor
		              </select>
		          </td>
		          <td>
				      <select name="saletype_id_x" class="feefield">
				          <option value=""></option>
		                  %for s in saletype:
		                  	<option value="${s.id}">${s}</option>
		                  %endfor
		              </select>
				  </td>
				  %if has_permission('FIN_VIEW_ALL'):
			          <td>
			              <input type="text" name="actual_sale_value_x" class="feefield erpfee"/>
			          	  <input type="text" name="actual_cost_value_x" class="feefield erpfee"/>
			          </td>
			          <td>
			              <input type="text" name="budget_sale_value_x" class="feefield erpfee"/>
			              <input type="text" name="budget_cost_value_x" class="feefield erpfee"/>
			          </td>
			          <td>
			              <input type="text" name="forecast_sale_value_x" disabled/>
			          	  <input type="text" name="forecast_cost_value_x" disabled/>
			          </td>
		          %else:
			          <td>
			              <input type="text" name="actual_sale_value_x" disabled/>
			          	  <input type="text" name="actual_cost_value_x" disabled/>
			          </td>
			          <td>
			              <input type="text" name="budget_sale_value_x" disabled/>
			              <input type="text" name="budget_cost_value_x" disabled/>
			          </td>
			          <td>
			              <input type="text" name="forecast_sale_value_x" class="feefield erpfee"/>
			              <input type="text" name="forecast_cost_value_x" class="feefield erpfee"/>
			          </td>
		          %endif
		      </tr>
		  <tbody>
    	</table>


	</div>
</div>


<div id="dialog-form" title="Create new user">
  <p>Please input the exchange rate : </p>
  <p>1 USD = <input type="text" id="rate"/> <span id="currency"></span></p>
</div>