var LOCAL = true;
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

function replaceAll(str, find, replace) {
  return str.replace(new RegExp(find, 'g'), replace);
}

function drawGraph(json) {
	graph = {"nodes":[], "links":[]};
	for(var i=0 ; i<json.length ; i++){
		graph.nodes.push({
			"name": json[i].link
		});
		for(var j=0 ; j<json[i].results.films.length ; j++){
			var trouve = false;
			for(var k=0 ; k<graph.nodes.length ; k++){
				if(graph.nodes[k].name == json[i].results.films[j].movie.link){
					trouve = true;
					graph.links.push({
						"source": i,
						"target": k,
						"value": json[i].results.films[j].coeff
					})
				}
			}
			if(!trouve){
				graph.nodes.push({
					"name": json[i].results.films[j].movie.link
				});

				graph.links.push({
					"source": i,
					"target": graph.nodes.length-1,
					"value": json[i].results.films[j].coeff
				});
			}
		}
	}
	
	$("#results").append('<pre class="json">'+syntaxHighlight(graph)+'</pre>');
	$("#graph").graph({
		json: JSON.stringify(graph)
	});
}

// Random loading messages generation
var verbs = ["Calculating", "Computing", "Analyzing", "Generating", "Extrapolating", "Exploring", "Improving", "Processing", "Hashing", "Defining", "Quantifying", "Structuring", "Counting", "Measuring", "Abstracting", "Adding", "Substracting", "Multiplying", "Dividing", "Simplifying"];
var adjs = ["exponential", "underlying", "differential", "overloaded", "underloaded", "integrated", "abstract", "rigorous", "related", "similar", "logic", "formal", "natural", "virtual", "alternative", "derivable", "dedicated", "included", "excluded", "imported", "exported"];
var nouns = ["matrix", "values", "data", "search engines", "indices", "key/value pairs", "RDF triples", "numbers", "quantities", "structures", "patterns", "measures", "conclusion", "abstraction", "systems", "metadata", "theory", "language", "axioms"];

// Random color generation
var colors = ["primary", "success", "warning", "danger", "info"];

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
	var Elements = {
		$search : $("#search"),
		$searchSubmit : $("#searchSubmit"),
		$searchText : $("#searchText"),
		$loader : $("#loader"),
		$results : $("#results"),
		$graph : $("#graph"),
		$searchOptions : $("#searchOptions"),
		$progressMsg : $("#progressMsg"),
		$progressBar : $("#progressBar")
	};

	var loadingTimeout = null;

	var newLoading = function(){
		var minTimer = 1;
		var maxTimer = 10;
		var timer = (Math.floor(Math.random()*(maxTimer-minTimer))+minTimer)*1000;
		var color = getRandomElement(colors);
		var $bar = $('<div class="progress-bar progress-bar-'+color+'"></div>').css("transition-duration",(timer/1000)+"s");

		Elements.$progressMsg.text(getLoadingMessage());
		Elements.$progressBar.html($bar);
		// laisser le $bar.width
		$bar.width();
		$bar.addClass("load");

		loadingTimeout = setTimeout(function(){
			newLoading();
		},timer);
	};

	var createRanking = function(json, num){
		var rank = $("#rankPrototype").prop('innerHTML');
		rank = replaceAll(rank, "{{rank}}", num);
		rank = replaceAll(rank, "{{linkFilm}}", json.movie.link);
		rank = replaceAll(rank, "{{filmName}}", json.movie.infos.name.value);
		rank = replaceAll(rank, "{{coef}}", (json.coeff*100)+"%");
		var $rank = $("<li>"+rank+"</li>");
		return $rank;
	};

	var createFilm = function(json){
		var film = $("#filmPrototype .film").prop('outerHTML');
		film = replaceAll(film, "{{linkFilm}}", json.movie.link);
		film = replaceAll(film, "{{filmName}}", json.movie.infos.name.value);
		if(json.movie.infos.director){
			film = replaceAll(film, "{{directorLink}}", json.movie.infos.director.value);
		}
		if(json.movie.infos.dirName){
			film = replaceAll(film, "{{directorName}}", json.movie.infos.dirName.value);
		}
		if(json.movie.infos.country){
			film = replaceAll(film, "{{country}}", json.movie.infos.country.value);
		}
		if(json.movie.infos.starring){
			// traiter le starring ?
			film = replaceAll(film, "{{starring}}", json.movie.infos.starring.value);
		}
		var $film = $(film);
		return $(film);
	};

	var createResult = function(json){
		var result = $("#resultPrototype .result").prop('outerHTML');
		result = replaceAll(result, "{{link}}", json.link);
		result = replaceAll(result, "{{title}}", json.title);
		// here replace title
		var $result = $(result);
		// Pour chaque film
		for (var i = 0; i < json.results.films.length; i++) {
			$result.find(".result-right").append(createFilm(json.results.films[i]));
			$result.find(".ranking").append(createRanking(json.results.films[i], i+1))

		};
		return $result;
	};

	var loadResults = function(json){
		for (var i = 0; i < json.length; i++) {
			// Pour chaque resultats
			Elements.$results.append(createResult(json[i]));
		};
	};

	var States = {
		init: function(){
			console.log("States.init");
			Elements.$search.removeClass("small");
			Elements.$loader.addClass("hide");
			Elements.$results.addClass("hide");
			Elements.$graph.addClass("hide");
			Elements.$searchOptions.collapse("show");
		},
		loading: function(){
			console.log("States.loading");
			Elements.$search.addClass("small");
			Elements.$loader.removeClass("hide");
			Elements.$results.addClass("hide").empty();
			Elements.$graph.addClass("hide").empty();
			Elements.$searchOptions.collapse("hide");
			Elements.$searchSubmit.attr("disabled","disabled");
			Elements.$searchText.off("focus").focusout();
			Elements.$search.off("focusout");
			newLoading();
		},
		displayResults: function(json){
			console.log("States.displayResults");
			// to remove when ajax is ready
			clearTimeout(loadingTimeout)
			loadResults(json);
			drawGraph(json);
			Elements.$searchSubmit.removeAttr("disabled");
			//Elements.$search.addClass("small");
			Elements.$loader.addClass("hide");
			Elements.$results.removeClass("hide");
			Elements.$graph.removeClass("hide");
			Elements.$searchOptions.collapse("hide");
			Elements.$searchText.on("focus",function(){
				Elements.$search.removeClass("small");
			});
			Elements.$search.on("focusout",function(){
				Elements.$search.addClass("small");
			});
		}
	};


	$("#search").submit(function(e){
		e.preventDefault();
		$this = $(this);

		var path = "./cgi-bin/server.py";
		var params = {};

		params.mots_clefs = Elements.$searchText.val();
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

		States.loading();
		if(LOCAL){
			setTimeout(function(){States.displayResults(jsonsample)},5*100);
		}
		else{
			$.ajax({
				method: "GET",
				url: path,
				data: $.param(params),
				success : function(json, statut){
					console.log("SUCCESS-JSON : "+json);
					States.displayResults(json);
				},
				error: function (resultat, statut, erreur) {
					console.log("error");
					alert("Erreur lors de l'appel à "+path);
					console.log(resultat, statut, erreur);
					States.init();
				},
				complete: function(response){
					console.log("COMPLETE - RESPONSE : "+response);
				}
			});
		}

		return false;
	});

	// Run
	States.init();
});
