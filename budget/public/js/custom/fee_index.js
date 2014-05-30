function company_change(){
	var c = $("#company_id :selected").attr('currency');
	if(c){
		$(".currency").text('[' + c + ']');
	}else{
		$(".currency").text('');
	}
}

function loading(flag){
	if(flag == 0){
		$(".gridTable").showLoading();
	}else{
		$(".gridTable").hideLoading();
	}
}




function ajax_load(){
	var company_id = $('#company_id').val();
	var team_id = $('#team_id').val();
	var year = $('#year').val();
	var month = $('#month').val();

	if( !company_id || !team_id || !year || !month){
		return;
	}

	loading(0);
	
	$.post(
		'/fee/ajax_load',
		{
			'company_id' : company_id,
			'team_id' : team_id,
			'year' : year,
			'month' : month,
			't' : nowstr()
		},
		function(r){
			loading(1);
			$(".fee,.feecal").val("");
			$(".feechange").removeClass("feechange");
		
			if(r.code!=0){
				alert('Error');
			}else{				
				for(var i=0;i<r.data.length;i++){
					var d = r.data[i];
					$("[id^=a_"+d.feeitem_id+"_]").val(d.actual_value); 
					$("[id^=b_"+d.feeitem_id+"_]").val(d.budget_value);
					$("[id^=f_"+d.feeitem_id+"_]").val(d.forecast_value);
				}
				status2buttons(r.actual_status,r.budget_status,r.forecast_status);
			}
		},
		'json'
	);
}

function ajax_save(){
	var company_id = $('#company_id').val();
	var team_id = $('#team_id').val();
	var year = $('#year').val();
	var month = $('#month').val();

	var params = {
			'company_id' : company_id,
			'team_id' : team_id,
			'year' : year,
			'month' : month,
			't' : nowstr()
		};
	
	var flag = true;
	$('.fee,.feecal').each(function(){
		var tmp = $(this);
		if(tmp.val() && !checkfloat(tmp.val())){
			flag = false;
			tmp.addClass('feewarning');
		}
		params[tmp.attr('id')] = tmp.val();
	});
	
	if(!flag){
		$.prompt("Please correct the data in red before saving!",{opacity: 0.6,prefix:'cleanred'});
		return;
	}
	
	loading(0);
	
	$.post(
		'/fee/ajax_save',
		params,
		function(r){
			loading(1);
			
			if(r.code!=0){
				$.prompt("Error when saving data, please check the data and try again!",{opacity: 0.6,prefix:'cleanred'});
			}else{
				for(var i=0;i<r.updated.length;i++){
					var d = r.updated[i];
					$("[id^=a_"+d.feeitem_id+"_]").val(d.actual_value);
					$("[id^=b_"+d.feeitem_id+"_]").val(d.budget_value);
					$("[id^=f_"+d.feeitem_id+"_]").val(d.forecast_value);
				}
			    $(".feechange").removeClass("feechange");
			    status2buttons(r.actual_status,r.budget_status,r.forecast_status);
				$.prompt("Save the data successfully!");
			}
		},
		'json'
	);
}


function ajax_mark(field,s){
	var company_id = $('#company_id').val();
	var team_id = $('#team_id').val();
	var year = $('#year').val();
	var month = $('#month').val();
	var status = parseInt(s, 10);
	
	var params = {
			'company_id' : company_id,
			'team_id' : team_id,
			'year' : year,
			'month' : month,
			'status' : status,
			'field' : field,
			't' : nowstr()
		};
		
	$.post(
		'/fee/ajax_mark',
		params,
		function(r){
			if(r.code != 0){
				$.prompt("Error when saving data, please check the data and try again!",{opacity: 0.6,prefix:'cleanred'});
			}else{
				status2buttons(r.actual_status,r.budget_status,r.forecast_status);
				$.prompt("Update data successfully!");
			}
		},
		'json'
	)
}





function status2buttons(actual_status,budget_status,forecast_status){
	
}