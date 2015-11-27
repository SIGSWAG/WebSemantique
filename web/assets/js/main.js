var LOCAL = true;

function callIMDB($film, titre){
	params = {};
	params.t = titre;
	params.plot = "full";
	params.r = "json";
	params.type = "movie";
	params.tomatoes = "true";
	$.ajax({
		method: "GET",
		url: "http://www.omdbapi.com/",
		data: $.param(params),
		success : function(json, statut){
			$film.find('.directorName').replaceWith(json.Director);
			$film.find('.country').replaceWith(json.Country);
			$film.find('.starring').replaceWith(json.Actors);
			if(json.Released != 'N/A'){
				$film.find('.dl-horizontal').append("<dt>Released :</dt>");
				$film.find('.dl-horizontal').append("<dd>"+ json.Released +"</dd>");
			}
			if(json.Genre != 'N/A'){
				$film.find('.dl-horizontal').append("<dt>Genre</dt>");
				$film.find('.dl-horizontal').append("<dd>"+ json.Genre +"</dd>");
			}
			if(json.Awards != "N/A"){
				$film.find('.dl-horizontal').append("<dt>Awards</dt>");
				$film.find('.dl-horizontal').append("<dd>"+ json.Awards +"</dd>");
			}
			if(json.Poster != "N/A"){
				$film.find('.poster').attr("src",json.Poster);
			}
		},
		error: function (resultat, statut, erreur) {
			console.log("erreur : "+erreur);
		}
	});
}

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
			"name": decodeURIComponent(json[i].link),
			"type": "link"
		});
		for(var j=0 ; j<json[i].results.films.length ; j++){
			var trouve = false;
			for(var k=0 ; k<graph.nodes.length ; k++){
				if(graph.nodes[k].name == json[i].results.films[j].movie.link){
					trouve = true;
					graph.links.push({
						"source": i,
						"target": k,
						"val": json[i].results.films[j].coeff
					})
				}
			}
			if(!trouve){
				graph.nodes.push({
					"name": decodeURIComponent(json[i].results.films[j].movie.link),
					"type": "movie"
				});

				graph.links.push({
					"source": i,
					"target": graph.nodes.length-1,
					"val": json[i].results.films[j].coeff
				});
			}
		}
	}

	// $("#results").append('<pre class="json">'+syntaxHighlight(graph)+'</pre>');
	$("#graph").graph({
		json: JSON.stringify(graph),
		width : $("#graph").width()
	});
	$(window).resize(function() {
	    	if(this.resizeTO) clearTimeout(this.resizeTO);
	    	this.resizeTO = setTimeout(function() {
	        	$(this).trigger('resizeEnd');
	    	}, 500);
	});

	$(window).bind('resizeEnd', function() {
		console.log('resizeEnd');
	    	$("#graph").empty().graph({
			json: JSON.stringify(graph),
			width : $("#graph").width()
		});
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
		$filmList : $("#filmList"),
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
		if(json.movie.link)
			rank = replaceAll(rank, "{{linkFilm}}", json.movie.link);
		if(json.movie.infos && json.movie.infos.name && json.movie.infos.name.value)
			rank = replaceAll(rank, "{{filmName}}", json.movie.infos.name.value);
		rank = replaceAll(rank, "{{coef}}", (Math.floor(json.coeff*100*1000)/1000));
		var $rank = $("<li>"+rank+"</li>");
		return $rank;
	};

	var createFilm = function(json){
		var film = $("#filmPrototype .film").prop('outerHTML');
		if(json.link)
			film = replaceAll(film, "{{linkFilm}}", json.link);
		if(json.infos){
			if(json.infos.name){
				film = replaceAll(film, "{{filmName}}", json.infos.name.value);
			}

			if(json.infos.director){
				film = replaceAll(film, "{{directorLink}}", json.infos.director.value);
			}
			else{
				film = replaceAll(film, '<a target="_blank" href="{{directorLink}}">{{directorName}}</a>', '{{directorName}}');
			}

			if(json.infos.dirName){
				film = replaceAll(film, "{{directorName}}", json.infos.dirName.value);
			}
			else{
				film = replaceAll(film, '{{directorName}}', '<span class="directorName">Unknown</span>');
			}

			if(json.infos.country){
				film = replaceAll(film, "{{country}}", json.infos.country.value);
			}
			else{
				film = replaceAll(film, '{{country}}', '<span class="country">Unknown</span>');
			}

			if(json.infos.starring){
				if(json.infos.starring.type == "literal"){
					var starring = json.infos.starring.value;
					starring = replaceAll(starring, "\\*", ",");
					starring = starring.replace(',', ' ');
					film = replaceAll(film, "{{starring}}", starring);
				}
				else if(json.infos.starring.type == "uri"){
					var uri = json.infos.starring.value;
					var starring = uri.split("/");
					starring = starring[starring.length-1];
					starring = replaceAll(starring,"_", " ");
					var linkStarring = '<a target="_blank" href="'+uri+'">'+starring+'</a>';
					film = replaceAll(film, "{{starring}}", linkStarring);
				}
				else{
					film = replaceAll(film, "{{starring}}", json.infos.starring);
				}
			}
			else{
				film = replaceAll(film, "{{starring}}", '<span class="starring">Unknown</span>');
			}
		}
		var $film = $(film);
		callIMDB($film, json.infos.name.value);
		return $film;
	};

	var createResult = function(json){
		var result = $("#resultPrototype .result").prop('outerHTML');
		result = replaceAll(result, "{{link}}", json.link);
		result = replaceAll(result, "{{title}}", json.title);
		// here replace title
		var $result = $(result);
		// Pour chaque film
		for (var i = 0; i < json.results.films.length; i++) {
			$result.find(".result-right").append(createFilm(json.results.films[i].movie));
			$result.find(".ranking").append(createRanking(json.results.films[i], i+1))
		};
		return $result;
	};

	var loadResults = function(json){
		Elements.$results.append($('<h1 class="center" id="results-title">Results, and related films</h1>'));
		for (var i = 0; i < json.length; i++) {
			// Pour chaque resultats
			Elements.$results.append(createResult(json[i]));
		};
	};

	var loadListFilm = function(json){
		Elements.$filmList.append($('<h1 class="center" id="list-title">Movies related to your search</h1>'));
		for (var i = 0; i < json.length; i++) {
			// Pour chaque resultats
			Elements.$filmList.append(createFilm(json[i]));
		};

	};

	// Machine à Etats, Ayyye !
	var States = {
		ajaxReturned: 0,
		NB_AJAX: 2,
		init: function(){
			console.log("States.init");
			Elements.$search.removeClass("small");
			Elements.$loader.addClass("hide");
			Elements.$results.addClass("hide");
			Elements.$filmList.addClass("hide");
			Elements.$graph.addClass("hide");
			Elements.$searchOptions.collapse("show");
			Elements.$searchSubmit.removeAttr("disabled");
		},
		loading: function(){
			console.log("States.loading");
			States.ajaxReturned = 0;
			Elements.$search.addClass("small");
			Elements.$loader.removeClass("hide");
			Elements.$results.addClass("hide").empty();
			Elements.$filmList.addClass("hide").empty();
			Elements.$graph.addClass("hide").empty();
			//Elements.$searchOptions.collapse("hide");
			Elements.$searchSubmit.attr("disabled","disabled");
			Elements.$searchText.off("focus").focusout();
			Elements.$search.off("focusout");
			newLoading();
		},
		displayResults: function(jsonResult){
			console.log("States.displayResults");
			States.ajaxReturned++;
			loadResults(jsonResult);
			drawGraph(jsonResult);
			Elements.$results.removeClass("hide");
			Elements.$graph.removeClass("hide");
			//Elements.$searchOptions.collapse("hide");
			if(States.ajaxReturned == States.NB_AJAX){
				States.requestFinished();
			}
		},
		displayFilmList : function(jsonFilmList){
			console.log("States.displayFilmList");
			States.ajaxReturned++;
			loadListFilm(jsonFilmList);
			Elements.$filmList.removeClass("hide");
			//Elements.$searchOptions.collapse("hide");
			if(States.ajaxReturned == States.NB_AJAX){
				States.requestFinished();
			}
		},
		requestFinished : function(){
			console.log("States.requestFinished");
			Elements.$loader.addClass("hide");
			Elements.$searchSubmit.removeAttr("disabled");
			Elements.$searchText.on("focus",function(){
				Elements.$search.removeClass("small");
			});
			Elements.$search.on("focusout",function(){
				Elements.$search.addClass("small");
			});
			Elements.$search.on("click",function(){
				Elements.$search.removeClass("small");
			});
		}
	};

	$("#search").submit(function(e){
		e.preventDefault();
		$this = $(this);

		var path = "./cgi-bin/server.py";
		var params1 = {}, params2 = {};
		params1.mots_clefs = Elements.$searchText.val();
		params2.mots_clefs = Elements.$searchText.val();
		params1.max_number_of_results =  $("#maxNumberOfResults").val();
		// 1 -> google
		// 2 -> bing
		// 3 -> google & bing
		params1.search_type =  $("input[name='searchType']:checked").val();
		// Confiance  petit -> plus de result
		params1.spotlight_confidence = $("#spotlightConfidence").val();
		// laisser a true pour le web
		params1.from_web = "true";
		params1.spotlight_support = 20;
		params1.append_keyword = $("input[name='appendKeyword']:checked").length?"true":"false";

		States.loading();
		if(LOCAL){
			setTimeout(function(){States.displayResults(jsonsample)},150*1000);
			setTimeout(function(){States.displayFilmList(jsonlistsample)},1*1000);
		}
		else{
			$.ajax({
				method: "GET",
				url: path,
				data: $.param(params2),
				success : function(json, statut){
					console.log(json);
					States.displayFilmList(json);
				},
				error: function (resultat, statut, erreur) {
					alert("Erreur lors de l'appel à "+path+$.param(params2));
					console.log(resultat, statut, erreur);
					States.init();
				}
			});
			$.ajax({
				method: "GET",
				url: path,
				data: $.param(params1),
				success : function(json, statut){
					console.log(json);
					States.displayResults(json);
				},
				error: function (resultat, statut, erreur) {
					alert("Erreur lors de l'appel à "+path+$.param(params1));
					console.log(resultat, statut, erreur);
					States.init();
				}
			});
		}
		return false;
	});

	// Run
	States.init();
});
