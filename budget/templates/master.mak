<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<%!
	from tg.flash import get_flash,get_status
	from repoze.what.predicates import not_anonymous,in_group, has_permission
%>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<meta http-Equiv="Cache-Control" Content="no-cache">
	<meta http-Equiv="Pragma" Content="no-cache">
	<meta http-Equiv="Expires" Content="0">
	<title>${self.extTitle()}</title>
	<link href="/images/favicon.ico" type="images/x-icon" rel="shortcut icon" />
    <link rel="stylesheet" type="text/css" href="/css/normalize.css" media="screen,print"/>
	<link rel="stylesheet" type="text/css" href="/css/screen.css" media="screen,print"/>
	<link rel="stylesheet" type="text/css" href="/css/all.css" media="screen,print"/>
    <link rel="stylesheet" type="text/css" href="/css/impromt.css" media="screen,print"/>
	${self.extCSS()}

	<script type="text/javascript" src="/js/jquery-1.8.3.min.js"></script>
	<script type="text/javascript" src="/js/jquery-impromptu.1.5.js"></script>
	<script type="text/javascript" src="/js/menu.js"></script>
	
	%if get_flash():
	<script language="JavaScript" type="text/javascript">
	    //<![CDATA[
		  $(document).ready(function(){
		  	%if get_status() == "ok":
		  		$.prompt("${get_flash()}",{opacity: 0.6,prefix:'cleanblue'});
		  	%elif get_status() == "warn":
		  		$.prompt("${get_flash()}",{opacity: 0.6,prefix:'cleanred'});
		  	%endif
		  });
	    //]]>
	</script>
	%endif


	${self.extJavaScript()}

</head>

<body>
	<div id="page-div">
		${self.header()}
		${self.body()}
	</div>
	<div style="clear:both"></div>
	${self.footer()}
</body>

</html>


<%def name="extTitle()">r-pac - Tribal</%def>
<%def name="extCSS()"></%def>
<%def name="extJavaScript()"></%def>

<%def name="header()">
<div>
<table width="100%" border="0" cellspacing="0" cellpadding="0">
  <tr>
    <td width="200" valign="middle"><img src="/images/logo.jpg" width="737" height="72" /></td>
    <td valign="middle" bgcolor="#EDF6FF">
    	<div id="pageLogin"><span class="welcome">Welcome :</span> ${request.identity["user"]} | <a href="/">Home</a> | <a href="/logout_handler">Logout</a></div>
    </td>
  </tr>
</table>
</div>


<div class="menu-tab">
    <ul>
        <li class="${'highlight' if tab_focus=='main' else ''}"><a href="/index">Main</a></li>
        <!-- <li class="${'highlight' if tab_focus=='view' else ''}"><a href="/tracking">Tracking</a></li> -->
        %if in_group("Admin") or has_permission('FIN_VIEW_ALL'):
        <li class="${'highlight' if tab_focus=='report' else ''}"><a href="/report">Report</a></li>
        %endif
        %if in_group("Admin") or has_permission('MASTER'):
        	<li class="${'highlight' if tab_focus=='master' else ''}"><a href="/master">Master</a></li>
        %endif
        %if in_group("Admin"):
        	<li class="${'highlight' if tab_focus=='access' else ''}"><a href="/access">Access</a></li>
        %endif
    </ul>
</div>

<div style="clear:both"></div>

</%def>


<%def name="footer()">
<div id="footer"><span style="margin-right:40px">Copyright r-pac International Corp.</span></div>
</%def>