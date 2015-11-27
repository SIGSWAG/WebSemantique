(function($) {

	$.fn.graph = function(parameters) {

		var defaultSettings = {
			width: "300",
			height: "400",
			json: "",
			linksLabelsColor: "#999",
			labelsColor: "#ccc"
		};
		var settings = $.extend(defaultSettings, parameters);

		if (settings.json == "") {
			console.error("No JSON provided. Giving up.");
			return;
		}

		var width = settings.width,
			height = settings.height;

		var force = d3.layout.force()
			.charge(-1500)
			.linkDistance(250)
			.size([width, height]);

		var graph = JSON.parse(settings.json);

		return this.each(function() {

			var svg = d3.select(this).append("svg")
				.attr("class", "graph")
				.attr("width", width)
				.attr("height", height);

			force
				.nodes(graph.nodes)
				.links(graph.links)
				.start();


			// Création des arcs

			var links = svg.selectAll(".link").data(graph.links).enter()
				.append("line")
				.attr("class", "link");

			var linksLabels = svg.selectAll("text").data(graph.links).enter()
				.append("text")
				.attr("fill", settings.linksLabelsColor)
				.attr("text-anchor", "middle")
				.text(function(d) {
					return (Math.floor(d.val * 100 * 1000) / 1000);
				}); // arrondi à trois chiffres


			// Création des noeuds

			var nodes = svg.selectAll(".node").data(graph.nodes).enter()
				.append("g")
				.attr("class", "node")
				.attr("r", 5)
				.call(force.drag);

			nodes.append("circle")
				.attr("r", 8)
				.attr("fill", function(d) {
					if (d.type == "movie") return "#4caf50";
					if (d.type == "link") return "#f44336";
					return "black";
				});

			nodes.append("a")
				.attr("xlink:href", function(d) {
					return d.name
				})
				.attr("target", "_blank")
				.append("text")
				.attr("fill", settings.labelsColor)
				.attr("text-anchor", "middle")
				.attr("dy", "1.5em")
				.text(function(d) {
					return d.name;
				});

			force.on("tick", function() {
				links
					.attr("x1", function(d) {
						return d.source.x;
					})
					.attr("y1", function(d) {
						return d.source.y;
					})
					.attr("x2", function(d) {
						return d.target.x;
					})
					.attr("y2", function(d) {
						return d.target.y;
					});

				linksLabels
					.attr("x", function(d) {
						return d.source.x + (d.target.x - d.source.x) / 2;
					})
					.attr("y", function(d) {
						return d.source.y + (d.target.y - d.source.y) / 2;
					});

				nodes.attr("transform", function(d) {
					return "translate(" + d.x + "," + d.y + ")";
				});
			});

		});

	};

}(jQuery));
