var width = 960,
	height = 500;

var color = d3.scale.category20();

var force = d3.layout.force()
	.charge(-120)
	.linkDistance(75)
	.size([width, height]);

var svg = d3.select("body").append("svg")
	.attr("width", width)
	.attr("height", height);

d3.json("data.json", function(error, graph) {
	if (error) throw error;

	force
		.nodes(graph.nodes)
		.links(graph.links)
		.start();

		
	// Création des arcs
		
	var links = svg.selectAll(".link").data(graph.links).enter()
		.append("line")
			.attr("class", "link")
			.style("stroke-width", function(d) { return Math.sqrt(d.value); });
	
	var linksLabels = svg.selectAll("text").data(graph.links).enter()
		.append("text")
			.attr("x", function(d) { return d.source.x + (d.target.x - d.source.x) / 2; })
			.attr("y", function(d) { return d.source.y + (d.target.y - d.source.y) / 2; })
			.text(function(d) { return "text"; });


	// Création des noeuds
	
	function overNode(){
		d3.select(this).transition()
			.duration(150)
			.attr("fill", "red")
			.attr("r", 16);
	}
	
	function outNode(){
		d3.select(this).transition()
			.duration(150)
			.attr("fill", "black")
			.attr("r", 8);
	}
	
	var nodes = svg.selectAll(".node").data(graph.nodes).enter()
		.append("g")
			.attr("class", "node")
			.attr("r", 5)
			.call(force.drag);
			
	nodes.append("circle")
		//.on("mouseover", overNode)
		//.on("mouseout", outNode)
		.attr("r", 8);
		
	nodes.append("text")
		.attr("x", 12)
		.attr("dy", ".35em")
		.text(function(d) { return d.name; });

	force.on("tick", function() {
		links.attr("x1", function(d) { return d.source.x; })
			.attr("y1", function(d) { return d.source.y; })
			.attr("x2", function(d) { return d.target.x; })
			.attr("y2", function(d) { return d.target.y; });

		linksLabels
			.attr("x", function(d) { return d.source.x + (d.target.x - d.source.x) / 2; })
			.attr("y", function(d) { return d.source.y + (d.target.y - d.source.y) / 2; });
			
		nodes.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
	});
});