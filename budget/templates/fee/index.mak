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
    .ui-tabs-anchor{
    	font-size : 6px;
    }
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
		$( "#tabs" ).tabs();
		
		$("#company_id,#team_id,#year,#month").change(function(){
			ajax_load();
		});
		
		$("#company_id").change(function(){ company_change(); });
		
		$(".fee,.feecal,.feechange").numeric(false);
		
		$(".fee").change(function(){
			$(this).addClass('feechange');
		});
		
		$(".save,.actual_confirmed,.budget_confirmed,.post").hide();
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
	<td width="64" valign="top" align="left"><a href="/fee/index"><img src="/images/images/budget_g.jpg"/></a></td>
	%if is_fin:
		<td width="64" valign="top" align="left"><a href="/fee/im"><img src="/images/images/import_g.jpg"/></a></td>
	%endif
    <td width="23" valign="top" align="left"><img height="21" width="23" src="/images/images/menu_last.jpg"/></td>
    <td valign="top" style="background:url(/images/images/menu_end.jpg) repeat-x;width:100%"></td>
  </tr>
</tbody></table>
</div>

%if is_fin:
	<div class="nav-tree">Finance Budget&nbsp;&nbsp;&gt;&nbsp;&nbsp;Actual, Budget And Forecast</div>
%else:
	<div class="nav-tree">Finance Budget&nbsp;&nbsp;&gt;&nbsp;&nbsp;Forecast</div>
%endif



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
	
	<div style="margin:5px 0px 5px 10px;width:1200px;">
		<p>
			<span class="save"><input type="button" class="btn" value="Save" onclick="ajax_save()"/>&nbsp;</span>
		%if is_fin:
			<span class="actual_confirmed"><input type="button" class="btn" value="Mark 'Actual' as 'Confirmed'" onclick="ajax_mark('actual_status',20)"/>&nbsp;</span>
			<span class="budget_confirmed"><input type="button" class="btn" value="Mark 'Budget' as 'Confirmed'" onclick="ajax_mark('budget_status',20)"/>&nbsp;</span>
			<span class="post"><input type="button" class="btn" value="Post" onclick="ajax_mark(null,30)"/>&nbsp;</span>
		%endif
		</p>
	
	    <div id="tabs">
		  <ul>
		  	%for g in feegroups:
		    	<li><a href="#tabs-${g.id}">${g.label}</a></li>
		    %endfor
		  </ul>
		  %for g in feegroups:
			  <div id="tabs-${g.id}">
			      <table class="gridTable budget-table" cellpadding="0" cellspacing="0" border="0">
				      <thead>
				          <tr>
				              <th style="width:400px;border-left:1px solid #ccc;">&nbsp;</th>
			                  <th style="width:150px;">Actual<span class="currency"></span></th>
			                  <th style="width:150px;">Budget<span class="currency"></span></th>
			                  <th style="width:150px;">Forecast<span class="currency"></span></th>
				          </tr>
				      </thead>
				      <tbody>
				          %for item in g.items:
							<tr>
								<td style="text-align:left;border-left:1px solid #ccc;">${item.label}</td>
								%if item.type == 0:					
									%if is_fin:
									    <td><input type="text" name="a_${item.id}_${item.type}" id="a_${item.id}_${item.type}" value="" class="fee"/></td>
									    <td><input type="text" name="b_${item.id}_${item.type}" id="b_${item.id}_${item.type}" value="" class="fee"/></td>
									    <td><input type="text" name="f_${item.id}_${item.type}" id="f_${item.id}_${item.type}" value="" disabled style="text-align:right;"/></td>
									%else:
										<td><input type="text" name="a_${item.id}_${item.type}" id="a_${item.id}_${item.type}" value="" disabled style="text-align:right;"/></td>
									    <td><input type="text" name="b_${item.id}_${item.type}" id="b_${item.id}_${item.type}" value="" disabled style="text-align:right;"/></td>
									    <td><input type="text" name="f_${item.id}_${item.type}" id="f_${item.id}_${item.type}" value="" class="fee"/></td>
									%endif
								%else:
									%if is_fin:
									    <td><input type="text" name="a_${item.id}_${item.type}" id="a_${item.id}_${item.type}" value="" class="feecal"  readonly/></td>
									    <td><input type="text" name="b_${item.id}_${item.type}" id="b_${item.id}_${item.type}" value="" class="feecal"  readonly/></td>
									    <td><input type="text" name="f_${item.id}_${item.type}" id="f_${item.id}_${item.type}" value="" disabled style="text-align:right;"/></td>
									%else:
										<td><input type="text" name="a_${item.id}_${item.type}" id="a_${item.id}_${item.type}" value="" disabled style="text-align:right;"/></td>
									    <td><input type="text" name="b_${item.id}_${item.type}" id="b_${item.id}_${item.type}" value="" disabled style="text-align:right;"/></td>									    
									    <td><input type="text" name="f_${item.id}_${item.type}" id="f_${item.id}_${item.type}" value="" class="feecal" readonly/></td>
									%endif
								%endif
							</tr>
						%endfor
				      </tbody>
				  </table>
			  </div>
		  %endfor
		</div>	
    
	</div>
</div>