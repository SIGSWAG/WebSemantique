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

// Random loading messages generation
var verbs = ["Calculating", "Computing", "Analyzing", "Generating", "Extrapolating", "Exploring", "Improving", "Processing", "Hashing", "Defining", "Quantifying", "Structuring", "Counting", "Measuring", "Abstracting", "Adding", "Substracting", "Multiplying", "Dividing", "Simplifying"];
var adjs = ["exponential", "underlying", "differential", "overloaded", "underloaded", "integrated", "abstract", "rigorous", "related", "similar", "logic", "formal", "natural", "virtual", "alternative", "derivable", "dedicated", "included", "excluded", "imported", "exported"];
var nouns = ["matrix", "values", "data", "search engines", "indices", "key/value pairs", "RDF triples", "numbers", "quantities", "structures", "patterns", "measures", "conclusion", "abstraction", "systems", "metadata", "theory", "language", "axioms"];

function getRandomElement(items){
    return items[Math.floor(Math.random()*items.length)];
}

function getLoadingMessage(){
    var verb = getRandomElement(verbs);
    var adj = getRandomElement(adjs);
    var noun = getRandomElement(nouns);
    return [verb, adj, noun].join(" ") + "...";
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
		params.append_keyword = $("input[name='appendKeyword']:checked").length?"true":"false";

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
