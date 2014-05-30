var new_record_count = 1;
var is_updated = false;
var currency = null;
var currency_id = null;
var exchangerate = null;

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
		'/erpfee/ajax_load',
		{
			'company_id' : company_id,
			'team_id' : team_id,
			'year' : year,
			'month' : month,
			't' : nowstr()
		},
		function(r){
			loading(1);
		
			if(r.code!=0){
				alert('Error');
			}else{

				$(".gridTable tbody tr").not(".template").remove();
				
				if(r.data.length<1){					
					add_row();
				}else{
					for(var i=0;i<r.data.length;i++){
						var d = r.data[i];
						//var tmp = $(".template").clone(true).removeClass("template");
						var tmp = gen_row(d.id);
						var names = ['customer','brand','subline_id','saletype_id','actual_sale_value','actual_cost_value',
									'budget_sale_value','budget_cost_value','forecast_sale_value','forecast_cost_value'];
						for(var j=0;j<names.length;j++){
						    var n = names[j];
						    $("[name^='"+n+"_']",tmp).val(d[n]);
						}
						$(".gridTable").append(tmp);
					}
					if(r.status >= 30){ //if it's not posted
						$(".gridTable tbody tr").not(".template").attr('disabled',true);
					}
				}
				
				status2buttons(r.status);
				
				currency = r.currency;
				currency_id = r.currency_id;
				exchangerate = r.exchangerate;

			}
		},
		'json'
	);
}



function ajax_save(){
	if(is_fin){
		if(!exchangerate){
			$("#currency").text(currency);
			$( "#dialog-form" ).dialog( "open" );
			return;
		}
	}

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
	
	var flag = false;
	$("tbody tr").not('.template').each(function(){
		flag = true;
		var tr = $(this);
		$('.feefield',tr).each(function(){
			var tmp = $(this);
			params[tmp.attr('name')] = tmp.val();
		});
	});
	
	if(!flag){
		$.prompt("Please input at lease one line data before saving!",{opacity: 0.6,prefix:'cleanred'});
		return;
	}
	
	loading(0);
	
	$.post(
		'/erpfee/ajax_save',
		params,
		function(r){
			loading(1);
			
			if(r.code!=0){
				$.prompt("Error when saving data, please check the data and try again!",{opacity: 0.6,prefix:'cleanred'});
			}else{
				for(var i=0;i<r.newrecords.length;i++){
					var d = r.newrecords[i];
					
					$("[name$='_"+ d.old_id +"']").each(function(){
						var tmp = $(this);
						var name = tmp.attr('name');
						tmp.attr('name',name.replace('_'+d.old_id, '_'+d.new_id));
					});
				}
 				status2buttons(r.status);
				$.prompt("Save data successfully!");
			}
		},
		'json'
	);
}


var ajax_mark = function (status) {
	if(is_updated){
		$.prompt("Please save the data first before this action!",{opacity: 0.6,prefix:'cleanred'});
		return;
	}
	var company_id = $('#company_id').val();
	var team_id = $('#team_id').val();
	var year = $('#year').val();
	var month = $('#month').val();
	
	var params = {
			'company_id' : company_id,
			'team_id' : team_id,
			'year' : year,
			'month' : month,
			'status' : status,
			't' : nowstr()
		};
		
	loading(0);
	$.post(
		'/erpfee/ajax_mark',
		params,
		function(r){
			loading(1);
			
			if(r.code!=0){
				$.prompt("Error when updating data, please check the data and try again!",{opacity: 0.6,prefix:'cleanred'});
			}else{
				if(r.status >= 20){
					$("tbody tr").not('.template').find('input,select').attr('disabled',true);
				}
				status2buttons(r.status);
				$.prompt("Update the data successfully!");
			}
		},
		'json'
	);
};


function remove_row(obj){
	$($(obj).parents("tr")[0]).remove();
	is_updated = true;
}

function add_row(){
	var tmp = gen_row('N' + new_record_count++);
	$(".gridTable").append(tmp);
	is_updated = true;
}

function gen_row(id){
	var tmp = $(".template").clone(true,true).removeClass("template");
	$("[name$='_x']",tmp).each(function(){
		var t = $(this);
		var n = t.attr('name');
		t.attr('name',n.replace('_x','_'+id));
	});
	
	$(".delbtn",tmp).show();
	
	bind_customer($('.accustomer',tmp));
	bind_brand($('.acbrand',tmp));
	return tmp;
}


function bind_customer(obj){
	obj.autocomplete({
		minLength: 2,
		source : function(request,response){
			$.getJSON(
				'/erpfee/ajax_search_customer',
				{
					'term' : request.term
				},
				function(r){
					response(r.data);
				}
			);
		}
	});
}

function bind_brand(obj){
	obj.autocomplete({
		//minLength: 2,
		source : function(request,response){
			var tr = $(obj.parents("tr")[0]);
			var customer = $("[name^='customer_']",tr).val();
			if(!customer){
				response([]);
			}else{
				$.getJSON(
					'/erpfee/ajax_search_brand',
					{
						'term' : request.term,
						'customer' : customer
					},
					function(r){
						response(r.data);
					}
				);
			}
		}
	});
}



function status2buttons(status){
	$(".addbtn,.savebtn,.postbtn,.delbtn").hide();
	
	if(is_fin){
		$("tbody tr").not('.template').find('input,select').not("input[name^='actual_'],input[name^='budget_']").removeAttr('disabled');
	}else{
		$("tbody tr").not('.template').find('input,select').not("input[name^='forecast_']").removeAttr('disabled');
	}
	
	
	if(status == null){ //if no data
		$(".addbtn,.savebtn").show();
	}else{
		if(status < 20){ //if it's not posted
			$(".addbtn,.savebtn,.postbtn,.delbtn").show();
		}else{
			// if's posted
			$("tbody tr").not('.template').find('input,select').attr('disabled',true);
		}
	
	}
}


function ajax_rate(rate){

	$.getJSON(
		'/erpfee/ajax_rate',
		{
		    'currency_id' : currency_id,
			'year' : $("#year").val(),
			'month' : $("#month").val(),
			'rate' : rate,
			't' : nowstr()
		},
		function(r){
			if(r.code!=0){
				alert('Error when saving the value,please adjust the value and try again!');
			}else{
				exchangerate = rate;
				alert('Save the exchange rate successfully!');
				$( "#dialog-form" ).dialog( "close" );
			}
		}
	)
	
}