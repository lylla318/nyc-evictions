

$(document).ready(function() {

  d3.csv("output_data/inwood_evictions_cleaned.csv",function(evictions){
    formatData(evictions);
  });

  function formatData(evictions) {

    var evictionDict = {};
    var residentialEvictionBins = [],
        evictionBins = [],
        evictionCounts = {};
    var inwood_count = 0
    console.log("EVICTIONS LEN", evictions.length)
    for (var i = 0 ; i < evictions.length ; i++) {
      // if(evictions[i]["executed_date"].charAt(9) == "8") {       // } 

      // if(evictions[i]["residential_commercial_ind"] === "Residential") {
      //   residentialEvictionBins.push(parseInt(evictions[i].bin_no) )
      // } else if (evictions[i]["residential_commercial_ind"] === "Commercial") {
      //   commercialEvictionBins.push(parseInt(evictions[i].bin_no) )
      // }
      if(evictions[i]["eviction_zip"] === "10034") {
        inwood_count += 1
      }

      evictionDict[evictions[i].bin_no] = evictions[i]
      if( Object.keys(evictionCounts).includes(evictions[i].bin_no) ) {
        evictionCounts[evictions[i].bin_no] += 1
      } else {
        evictionCounts[evictions[i].bin_no] = 1
      }

      evictionBins.push(parseInt(evictions[i].bin_no) )
            
    }

    console.log("INWOOD COUNT: ", inwood_count);

    d3.json("map_data/inwood_buildings.json",function(data){
      d3.json("map_data/inwood_streets.json",function(data2){
        drawInwood(data, data2, evictionBins, evictionDict, evictionCounts);
      });
    });
  }


  function drawInwood(inwood_buildings, inwood_streets, evictionBins, evictionDict, evictionCounts) {

    var margin = {top: 5, right: 5, bottom: 5, left: 5};
    var width = 800 - margin.left - margin.right,
        height = 1000 - margin.top - margin.bottom;
    var strokeColor = "#000"

    var inwoodBuildingFeatures = topojson.feature(inwood_buildings,inwood_buildings.objects.inwood_buildings);
    var inwoodStreetFeatures = topojson.feature(inwood_streets,inwood_streets.objects.inwood_streets);

    var max_area   = d3.max( inwoodBuildingFeatures.features, function(d) { 
      return d.properties.shape_area; 
    });

    // console.log(evictionCounts)

    var svg = d3.select(".map")
        .append("svg")
          .attr("class", "map")
          .attr("width", width + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

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
        console.log(d)
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

    var projection = d3.geoAlbersUsa().fitSize([width-margin.top, height-margin.top], inwoodBuildingFeatures);
    
    var path = d3.geoPath()
        .projection(projection);

    addData(evictionDict);

   function addData(evictionDict) {

      // ADD THE SCRAPED DATA //
      var fields = ["bbl", "block", "lot", "bin_no", "hnum_lo", "hnum_hi", "str_name", "condo_no", "coop_no"]
      for(var i = 0 ; i < inwoodBuildingFeatures.features.length ; i++) {
        for (var j = 0 ; j < fields.length ; j++ ) {
          var key = fields[j]
          var tmp = inwoodBuildingFeatures.features[i].properties
          if(Object.keys(evictionDict).includes(String(tmp.bin))) {
            evictionData = evictionDict[String(tmp.bin)]
            for(let key of Object.keys(evictionData)) {
              (inwoodBuildingFeatures.features[i].properties)[key] = evictionData[key]
            }
            inwoodBuildingFeatures.features[i].properties["eviction_count"] = evictionCounts[String(tmp.bin)]
          }

          // if(tmp && tmp.bin && dataByBin[tmp.bin] && dataByBin[tmp.bin][key]) {
          //   gramercyFeatures.features[i].properties[key] = dataByBin[tmp.bin][key];
          // }          
        }

      }

      addFeatures();

    }

    function addFeatures() {

      var evict = 0, noEvict = 0;

      var inwoodBuildingPaths = svg.selectAll(".inwood-buildings")
      .data(inwoodBuildingFeatures.features)
      .enter().append("path")
        .attr("id","building")
        .attr("d", function(d) { 
          return path(d); })
        .style("stroke-width", 0)
        .style("stroke", "#ddd")
        .style("cursor", "pointer")
        .style("fill", function(d) {

          if( evictionBins.includes(parseInt(d.properties.bin) ) )  {
            if(d.properties.eviction_zip === "10034" ) {
              evict += 1
              // console.log(d)
            }
            if(evictionCounts[d.properties.bin] === 1) {
              return "#fed976";
            } else if (evictionCounts[d.properties.bin] > 1 && evictionCounts[d.properties.bin] <= 5) {
              return "#fd8d3c";
            } else if (evictionCounts[d.properties.bin] > 5 && evictionCounts[d.properties.bin] <= 10){
              return "#e31a1c" //"#e50000"; //"#4c0000";
            } else {
              return "#800026"
            }
          } else {
            noEvict += 1;
            return "#ddd";
          }
        })
        .on("mouseover", function(d) {
          tool_tip.show(d)
        })
        .on("mouseout", tool_tip.hide);

      console.log("EVICT: ", evict)
      console.log("NO EVICT: ",noEvict)

      var inwoodStreetPaths = svg.selectAll(".inwood-streets")
      .data(inwoodStreetFeatures.features)
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

      svg.append("text")             
        .attr("x", 300)
        .attr("y",200)
        .style("text-anchor", "middle")
        .style("font-size", 22)
        .style("font-weight", "bold")
        .style("font-family","MarkPro")
        .style("fill","black")
        .text("Evictions in Inwood" );

      svg.append("text")             
        .attr("x",300)
        .attr("y",220)
        .style("text-anchor", "middle")
        .style("font-size", 14)
        .style("font-weight", "regular")
        .style("font-family","MarkPro")
        .style("fill","black")
        .text("January 2017 - August 2018" );

      var legend = ["#fed976", "#fd8d3c", "#e31a1c", "#800026"],
          scale  = ["1", "5", "10", ">10"]

      var yPadding = 240, xPadding = 240;

      for(var i = 0 ; i <=3 ; i++) {

        svg.append("rect")
          .attr("x",xPadding + i*25)
          .attr("y",yPadding)
          .attr("width",25)
          .attr("height",15)
          .style("fill",legend[i])

        svg.append("text")
          .attr("x", function() {
            if(i == 0 || i == 1) {
              return xPadding+15 + i*25; 
            } else if (i == 2) {
              return xPadding+20 + i*25;
            } else {
              return xPadding+23 + i*25;
            }
          })
          .attr("y",yPadding + 15)
          .attr("dy", "1em")
          .style("text-anchor", "end")
          .style("font-size", 12)
          .style("font-family","MarkPro")
          .text(scale[i])

      }

  }


});


















  // d3.csv("output_data/evictions_by_bin.csv",function(evictions){
  //   formatData(evictions);
  // });

  // function formatData(evictions) {

  //   var evictionBins = []
  //   for (var i = 0 ; i < evictions.length ; i++) {
  //     // console.log(evictions[i].count >= 5)
  //     if(parseInt(evictions[i].count) >= 5) {
  //       evictionBins.push(parseInt(evictions[i].bin))
  //     }
  //   }

  //   d3.json("map_data/inwood_buildings.json",function(data){
  //     d3.json("map_data/inwood_streets.json",function(data2){
  //       drawInwood(data, data2, evictionBins);
  //     });
  //   });
  // }