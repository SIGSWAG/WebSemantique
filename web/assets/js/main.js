$(function(){
	$("#search").submit(function(e){
		e.preventDefault();
		$this = $(this);

		var path = "./cgi-bin/main.cgi";
		var params = {};

		params.mots_clefs = $("#searchText").val();
		params.seuil_jordan = 0.1;

		$.ajax({
			method: "GET",
			url: path,
			data: $.param(params),
			success : function(json, statut){

			},
			error: function (resultat, statut, erreur) {
				console.log("error");
				alert("Erreur lors de l'appel à "+path);
				console.log(resultat, statut, erreur);
			},
			complete: function(response){
				console.log(response);
				$("#results").append("<pre>"+response.responseText+"</pre>");
			}
		});
		return false;
	});
});