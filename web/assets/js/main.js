function syntaxHighlight(json) {
    if (typeof json != 'string') {
         json = JSON.stringify(json, undefined, 4);
    }
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        var cls = 'number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'key';
            } else {
                cls = 'string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'boolean';
        } else if (/null/.test(match)) {
            cls = 'null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}

function drawGraph(json) {

	$("#results").graph({
		json: json
	});

}


$(function(){
	$("#search").submit(function(e){
		e.preventDefault();
		$this = $(this);

		var path = "./cgi-bin/server.py";
		var params = {};

		params.mots_clefs = $("#searchText").val();
		params.max_number_of_results =  $("#maxNumberOfResults").val();
		// 1 -> google
		// 2 -> bing
		// 3 -> google & bing	
		params.search_type =  $("input[name='searchType']:checked").val();
		// Confiance  petit -> plus de result
		params.spotlight_confidence = $("#spotlightConfidence").val();
		// laisser a true pour le web
		params.from_web = "true";
		params.spotlight_support = 20;
		params.append_keyword = "false";

		$.ajax({
			method: "GET",
			url: path,
			data: $.param(params),
			success : function(json, statut){
				$("#results").append('<pre class="json">'+syntaxHighlight(json)+'</pre>');
				drawGraph(json);
				console.log(syntaxHighlight(json));
			},
			error: function (resultat, statut, erreur) {
				console.log("error");
				alert("Erreur lors de l'appel à "+path);
				console.log(resultat, statut, erreur);
			},
			complete: function(response){
				console.log(response);
			}
		});
		return false;
	});
});
