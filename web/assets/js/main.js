$(function(){
	$("#search").submit(function(e){
		e.preventDefault();
		$this = $(this);

		var path = "./cgi-bin/main.cgi";
		var params = {};

		params.mots_clefs = $("#searchText").val();
		params.max_number_of_results = 10;
		params.search_type = 1;
		params.spotlight_confidence = 0.1;
		params.from_web = "true";
		params.spotlight_support = "false";

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