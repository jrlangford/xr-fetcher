function isCheckedCheckboxGroup(forma, salida,grupo, mensaje) {
	//if (salida != "undefined"){
	//if (salida.selectedIndex != 0){
	forma.target="_blank";
	//} else{
	//forma.target="";
	//}
	//}

	var checked = false;
	// Si hay por lo menos un checkbox
	if (typeof grupo != "undefined") { // grupo es undefined cuando no hay ningun checkbox
		if (typeof grupo.length != "undefined") { // grupo.length es undefined cuando s�lo hay un checkbox
			for (var i = 0; i < grupo.length; i++) {
				if (grupo[i].checked) {
					checked = true;
					break; // sale del for
				}
			}
		} else { // s�lo hay un checkbox
			if (grupo.checked) {
				checked = true;
			}
		}
	} // typeof grupo != "undefined"
	if ( ! checked) {
		alert(mensaje);
		return false;
	} // ! checked
	return true;
} // isCheckedCheckboxGroup

function esMenorIgual(fecha1,fecha2,idioma){
	if (idioma != "en"){
		if (fecha1 != "dd/mm/aaaa" && fecha2 != "dd/mm/aaaa" && fecha1 != "" && fecha2 != ""){
			var f1 = fecha1.split("/");
			var f2 = fecha2.split("/");
			var d1 = new Date(Number(f1[2]),Number(f1[1])-1,Number(f1[0]));
			var d2 = new Date(Number(f2[2]),Number(f2[1])-1,Number(f2[0]));
			if (d2.getTime()<d1.getTime()){
				alert("La fecha final es anterior a la fecha inicial.");
				return false;
			}
		}
	}else{
		if (fecha1 != "mm/dd/yyyy" && fecha2 != "mm/dd/yyyy" && fecha1 != "" && fecha2 != ""){
			var f1 = fecha1.split("/");
			var f2 = fecha2.split("/");
			var d1 = new Date(Number(f1[2]),Number(f1[0])-1,Number(f1[1]));
			var d2 = new Date(Number(f2[2]),Number(f2[0])-1,Number(f2[1]));
			if (d2.getTime()<d1.getTime()){
				alert("The final date is lower than the initial date.");
				return false;
			}
		}
	}
	return true;
}
function dentroDeRango(fecha1,fecha2,fechaMinima,fechaMaxima,idioma){
	var fechaSplitMinima=fechaMinima.split("/");
	var dateMinimo=new Date(Number(fechaSplitMinima[2]),Number(fechaSplitMinima[1])-1,Number(fechaSplitMinima[0]));

	var fechaSplitMaxima=fechaMaxima.split("/");
	var dateMaximo=new Date(Number(fechaSplitMaxima[2]),Number(fechaSplitMaxima[1])-1,Number(fechaSplitMaxima[0]));

	if (idioma != "en"){
		if(fecha1!= "dd/mm/aaaa"&& fecha1 != ""){
			var f1 = fecha1.split("/");
			var d1 = new Date(Number(f1[2]),Number(f1[1])-1,Number(f1[0]));
			if (d1.getTime()<dateMinimo.getTime()){
				alert("Las fechas deben estar dentro del rango: "+fechaMinima+" - "+fechaMaxima);
				return false;
			}
		}
		if(fecha2!= "dd/mm/aaaa"&& fecha2 != ""){
			var f2 = fecha2.split("/");
			var d2 = new Date(Number(f2[2]),Number(f2[1])-1,Number(f2[0]));
			if (d2.getTime()>dateMaximo.getTime()){
				alert("Las fechas deben estar dentro del rango: "+fechaMinima+" - "+fechaMaxima);
				return false;
			}
		}
	}else{
		if(fecha1!= "mm/dd/yyyy"&& fecha1 != ""){
			var f1 = fecha1.split("/");
			var d1 = new Date(Number(f1[2]),Number(f1[0])-1,Number(f1[1]));
			if (d1.getTime()<dateMinimo.getTime()){
				alert("Dates must be within the range: "+fechaMinima+" - "+fechaMaxima);
				return false;
			}
		}
		if(fecha2!= "mm/dd/yyyy"&& fecha2 != ""){
			var f2 = fecha2.split("/");
			var d2 = new Date(Number(f2[2]),Number(f2[0])-1,Number(f2[1]));
			if (d2.getTime()>dateMaximo.getTime()){
				alert("Dates must be within the range: "+fechaMinima+" - "+fechaMaxima);
				return false;
			}
		}
	}
	return true;
}
