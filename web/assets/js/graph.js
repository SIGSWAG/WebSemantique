(function ($){

	$.fn.graph = function(parameters){

		var defaultSettings = {
			width: '100%',
			height: 800,
			json: "",
			linksLabelsColor: "#ccc",
			labelsColor: "#ccc"
		};
		var settings = $.extend(defaultSettings, parameters);

		if(settings.json == ""){
			console.error("No JSON provided. Giving up.");
			return ;
		}

		var width = settings.width,
			height = settings.height;

		var force = d3.layout.force()
			.charge(-120)
			.linkDistance(150)
			.size([width, height]);

		return this.each(function(){

			var svg = d3.select(this).append("svg")
				.attr("class", "graph")
				.attr("width", width)
				.attr("height", height);

			d3.json(settings.json, function(error, graph) {
				if (error) throw error;

				force
					.nodes(graph.nodes)
					.links(graph.links)
					.start();


				// Création des arcs

				var links = svg.selectAll(".link").data(graph.links).enter()
					.append("line")
						.attr("class", "link")
						.style("stroke-width", function(d) { return Math.sqrt(d.val); });

				var linksLabels = svg.selectAll("text").data(graph.links).enter()
					.append("text")
						.attr("fill", settings.linksLabelsColor)
						.attr("text-anchor", "middle")
						.text(function(d) { return d.val; });


				// Création des noeuds

				var nodes = svg.selectAll(".node").data(graph.nodes).enter()
					.append("g")
						.attr("class", "node")
						.attr("r", 5)
						.call(force.drag);

				nodes.append("circle")
					.attr("r", 8);

				nodes.append("a")
					.attr("xlink:href", function(d) { return d.name })
					.attr("target", "_blank")
					.append("text")
						.attr("fill", settings.labelsColor)
						.attr("text-anchor", "middle")
						.attr("dy", "1.5em")
						.text(function(d) { return d.name; });

				force.on("tick", function() {
					links
						.attr("x1", function(d) { return d.source.x; })
						.attr("y1", function(d) { return d.source.y; })
						.attr("x2", function(d) { return d.target.x; })
						.attr("y2", function(d) { return d.target.y; });

					linksLabels
						.attr("x", function(d) { return d.source.x + (d.target.x - d.source.x) / 2; })
						.attr("y", function(d) { return d.source.y + (d.target.y - d.source.y) / 2; });

					nodes.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
				});
			});

		});

	};

}(jQuery));
