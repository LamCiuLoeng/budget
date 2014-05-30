function nowstr(){
    return Date.parse(new Date())
}

function checkfloat(v){
	var int_exp = /^-?\d+$/;
	var float_exp = /^-?([1-9]\d*.\d*|0.\d*[1-9]\d*|0?.0+|0)$/;
	if( int_exp.test(v) || float_exp.test(v) ){
		return true;
	}
	return false;
}

function redirect(url){
	window.location.href = url;
}