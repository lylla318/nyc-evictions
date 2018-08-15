

$(document).ready(function() {

  d3.csv("output_data/east_harlem_evictions_cleaned.csv",function(evictions){
    formatData(evictions);
  });

  function formatData(evictions) {

    var evictionDict = {};
    var evictionBins = [],
        //commercialEvictionBins = [],
        evictionCounts = {};

    for (var i = 0 ; i < evictions.length ; i++) {
      // if(evictions[i]["executed_date"].charAt(9) == "8") {       // } 
      
      evictionBins.push(parseInt(evictions[i].bin_no) )

      evictionDict[evictions[i].bin_no] = evictions[i]
      if( Object.keys(evictionCounts).includes(evictions[i].bin_no) ) {
        evictionCounts[evictions[i].bin_no] += 1
      } else {
        evictionCounts[evictions[i].bin_no] = 1
      }
      
    }

    d3.json("map_data/east_harlem_buildings.json",function(data){
      d3.json("map_data/east_harlem_streets.json",function(data2){
        drawInwood(data, data2, evictionBins, evictionDict, evictionCounts);
      });
    });
  }


  function drawInwood(east_harlem_buildings, east_harlem_streets, evictionBins, evictionDict, evictionCounts) {

    var margin = {top: 5, right: 5, bottom: 5, left: 5};
    var width = 1200 - margin.left - margin.right,
        height = 1500 - margin.top - margin.bottom;
    var strokeColor = "#000"

    var eastHarlemBuildingFeatures = topojson.feature(east_harlem_buildings,east_harlem_buildings.objects.east_harlem_buildings);
    var eastHarlemStreetFeatures = topojson.feature(east_harlem_streets,east_harlem_streets.objects.east_harlem_streets);

    var max_area   = d3.max( eastHarlemBuildingFeatures.features, function(d) { 
      return d.properties.shape_area; 
    });

    var svg = d3.select(".map")
        .append("svg")
          .attr("class", "map")
          .attr("width", width + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom)
    g = svg.append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    g.append("text")             
      .attr("transform",
            "translate(" + (width/2-10) + " ," + -40 + ")")
      .style("text-anchor", "middle")
      .style("font-size", 16)
      .style("font-weight", "bold")
      .style("font-family","MarkPro")
      .style("fill","black")
      .text("UPPER EAST" );

    var tool_tip = d3.tip()
      .attr("class", "d3-tip")
      .offset([-8, 0])
      .html(function(d) { 
        address = "";
        if(d.properties.hnum_hi === d.properties.hnum_lo) {
          address = d.properties.hnum_lo + " " + d.properties.str_name;
        } else if (! d.properties.hnum_hi || !d.properties.hnum_lo) {
          address = d.properties.str_name;
        } else {
          address = d.properties.hnum_lo + "-" + d.properties.hnum_hi + " " + d.properties.str_name;
        }
        // console.log(d)
        return "Block: " + d.properties.block 
        + "<br>" + "Lot: " + d.properties.lot  
        + "<br>" + "BIN: " + d.properties.bin 
        + "<br>" + "Address: " + address 
        + "<br>" + "# Evictions: " + d.properties.eviction_count; 
      });

    svg.append("rect")
      .attr("width","100%")
      .attr("height","100%")
      .attr("fill","#FFFFFF")
      .style("cursor","pointer")
    
    svg.call(tool_tip);

    var projection = d3.geoAlbersUsa().fitSize([width-margin.top, height-margin.top], eastHarlemBuildingFeatures);
    
    var path = d3.geoPath()
        .projection(projection);

    addData(evictionDict);

   function addData(evictionDict) {

      // ADD THE SCRAPED DATA //
      var fields = ["bbl", "block", "lot", "bin_no", "hnum_lo", "hnum_hi", "str_name", "condo_no", "coop_no"]
      for(var i = 0 ; i < eastHarlemBuildingFeatures.features.length ; i++) {
        for (var j = 0 ; j < fields.length ; j++ ) {
          var key = fields[j]
          var tmp = eastHarlemBuildingFeatures.features[i].properties
          if(Object.keys(evictionDict).includes(String(tmp.bin))) {
            evictionData = evictionDict[String(tmp.bin)]
            for(let key of Object.keys(evictionData)) {
              (eastHarlemBuildingFeatures.features[i].properties)[key] = evictionData[key]
            }
            eastHarlemBuildingFeatures.features[i].properties["eviction_count"] = evictionCounts[String(tmp.bin)]
          }

          // if(tmp && tmp.bin && dataByBin[tmp.bin] && dataByBin[tmp.bin][key]) {
          //   gramercyFeatures.features[i].properties[key] = dataByBin[tmp.bin][key];
          // }          
        }

      }

      addFeatures();

    }

    function addFeatures() {

      var inwoodBuildingPaths = svg.selectAll(".inwood-buildings")
      .data(eastHarlemBuildingFeatures.features)
      .enter().append("path")
        .attr("id","building")
        .attr("d", function(d) { 
          return path(d); })
        .style("stroke-width", 0)
        .style("stroke", "#ddd")
        .style("cursor", "pointer")
        .style("fill", function(d) {
          if( evictionBins.includes(parseInt(d.properties.bin) ) )  {
            if(evictionCounts[d.properties.bin] === 1) {
              return "#fed976";
            } else if (evictionCounts[d.properties.bin] > 1 && evictionCounts[d.properties.bin] <= 5) {
              return "#fd8d3c";
            } else if (evictionCounts[d.properties.bin] > 5 && evictionCounts[d.properties.bin] < 10){
              return "#e31a1c" //"#e50000"; //"#4c0000";
            } else {
              return "#800026"
            }
            // }
          } else {
            return "#ddd"
          }
        })
        .on("mouseover", function(d) {
          tool_tip.show(d)
        })
        .on("mouseout", tool_tip.hide);

      var inwoodStreetPaths = svg.selectAll(".inwood-streets")
      .data(eastHarlemStreetFeatures.features)
      .enter().append("path")
        .attr("id","street")
        .attr("d", function(d) { 
          return path(d); 
        })
        .style("stroke-width", 1)
        .style("stroke", "#FFD700")
        .style("cursor", "pointer")
        .style("fill", "none");

      }

  }

});

