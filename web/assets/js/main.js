$(function(){
	$("#search").submit(function(e){
		e.preventDefault();
		$this = $(this);

		var path = "./ajax/";
		var params = {};

		params.searchText = $("#searchText").val();

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