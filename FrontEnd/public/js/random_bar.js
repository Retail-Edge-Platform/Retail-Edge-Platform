
/* html
    <div class="tain">
        <svg class="bar" id="chart"></svg>
    </div>
    <div class="tain">
        <svg class="bar" id="chart1"></svg>
    </div>
*/

/* css
    .bar rect {
        fill: orange;
    }

    .bar text {
        fill: black;
        font: 10px Helvetica;
        text-anchor: end;
    }

    .tain {
    padding: 20px;
    }
*/

/* Create two charts
    random_barchart('#chart');
    random_barchart('#chart1');
*/

// From stackoverflow
function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function bars(bar_count, max_value) {
    let data = [];
    for (let i=0; i < bar_count; i++) {
        let v = getRandomInt(3, max_value);
  	    data.push(v);
    }
	return data;
}

function random_barchart(where) {
    var width = 100;
    var barHeight = 20;
    var number_of_bars = 5;
    var max_value = 60;
    random_barchart_comp(where, width, barHeight, number_of_bars, max_value);
}

function random_barchart_comp(where, width, barHeight, number_of_bars, max_value, titles=[]) {
    // From Tommy Chen Fiddle
    var data = bars(number_of_bars, max_value);

    var x = d3.scale.linear()
        .domain([0, d3.max(data)])
        .range([0, width]);

    var chart = d3.select(where)
        .attr('width', width)
        .attr('height', barHeight * data.length);

    var bar = chart.selectAll('g')
        .data(data)
        .enter()
        .append('g')
        .attr('transform', function(d, i){
            return 'translate(0,' + barHeight * i + ')';
        });

    bar.append('rect')
        .attr('width', x)
        .attr('height', barHeight - 1);

    bar.append('text')
        .attr('x', function(d){
            return x(d) - 3;
        })
        .attr('y', barHeight / 2)
        .attr('dy', '.35em')
        .text(function(d){
            return d;
        });
}

function random_barchart_comp_text(where, width, barHeight, number_of_bars, max_value, titles=[]) {
    var text_offset = 120;
    // From Tommy Chen Fiddle
    var data = bars(number_of_bars, max_value);

    var x = d3.scale.linear()
        .domain([0, d3.max(data)])
        .range([0, width]);

    var chart = d3.select(where)
        .attr('width', width + text_offset)
        .attr('height', barHeight * data.length);

    var bar = chart.selectAll('g')
        .data(data)
        .enter()
        .append('g')
        .attr('transform', function(d, i){
            return 'translate(' + text_offset + ',' + barHeight * i + ')';
        });

    bar.append('rect')
        .attr('width', x)
        .attr('height', barHeight - 1);

    bar.append('text')
        .attr('x', function(d){
            return (-5) ;
            //return x(d) - 3;
        })
        .attr('y', barHeight / 2)
        .attr('dy', '.35em')
        .text(function(d, i){
            //console.log(titles);
            return titles[i];
            //return d;
        });
}
