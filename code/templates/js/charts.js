<!-- charts.js -->
<script>
    // ChartJS functions

    function drawBarGraph(data, id, y_axis_text, max_tick=5) { 
        var labels = data.labels; 
        var chartLabel = data.chartLabel; 
        var chartdata = data.chartdata; 
        var bg_color = data.bg_color; 
        var border_color = data.border_color; 
        var ctx = document.getElementById(id).getContext('2d'); 
        var myChart = new Chart(ctx, { 
            type: 'bar', 
            data: { 
              labels: labels, 
              datasets: [{ 
                label: chartLabel, 
                data: chartdata, 
                backgroundColor: bg_color,
                borderColor: border_color, 
                borderWidth: 1 
              }] 
            }, 
            options: { 
                responsive: true,
                tooltips: {
                    position: 'nearest',
                    mode: 'index',
                    intersect: true,
                },
                legend: {
                    display: false,
                    labels: {
                        fontColor: '#B7BBBF'
                    }
                },
                scales: { 
                    yAxes: [{
                        beginAtZero: true,
                        scaleLabel: {
                            display: true,
                            labelString: y_axis_text,
                            fontColor: '#B7BBBF'
                        },
                        type: 'logarithmic',
                        position: 'left',
                        ticks: {
                            fontColor: '#41EAD4',
                            min: 0, //minimum tick
                            max: max_tick, //maximum tick
                            callback: function (value, index, values) {
                                return Number(value.toString());//pass tick values as a string into Number function
                            }
                        },
                        afterBuildTicks: function (chartObj) { //Build ticks labelling as per your need
                            chartObj.ticks = [];
                            chartObj.ticks.push(0);
                            chartObj.ticks.push(0.25);
                            chartObj.ticks.push(0.5);
                            chartObj.ticks.push(1);
                            chartObj.ticks.push(2.5);
                            chartObj.ticks.push(5);
                            chartObj.ticks.push(10);
                            chartObj.ticks.push(50);
                            chartObj.ticks.push(100);
                            chartObj.ticks.push(500);
                            chartObj.ticks.push(1000);
                            chartObj.ticks.push(5000);
                            chartObj.ticks.push(10000);
                        }
                    }],
                    xAxes: [{
                        position: 'nearest',
                        padding: 0,
                        ticks: {
                            fontColor: '#41EAD4'
                        }
                    }]
                } 
            } 
        }); 
    } 

    function drawLineGraph(data, id) { 
        var labels = data.labels; 
        var chartLabel = data.chartLabel; 
        var chartdata = data.chartdata; 
        var ctx = document.getElementById(id).getContext('2d'); 
        var chart = new Chart(ctx, { 
            type: 'line', 
              data: { 
              labels: labels, 
              datasets: [{ 
                label: chartLabel, 
                backgroundColor: 'rgb(255, 100, 200)', 
                borderColor: 'rgb(55, 99, 132)', 
                data: chartdata, 
              }] 
            }, 
      
            // Configuration options go here 
            options: { 
                scales: { 
                    xAxes: [{ 
                        display: true 
                    }], 
                    yAxes: [{ 
                        ticks: { 
                            beginAtZero: true 
                        } 
                    }] 
                } 
            } 
        }); 
    } 

    function drawPieGraph(data, id) { 
        var labels = data.labels; 
        var chartLabel = data.chartLabel; 
        var chartdata = data.chartdata; 
        var ctx = document.getElementById(id).getContext('2d'); 
        var chart = new Chart(ctx, { 
            type: 'pie',
            data: { 
              labels: labels, 
              datasets: [{ 
                label: chartLabel, 
                backgroundColor: ['rgb(51, 153, 255)', 'rgb(249, 177, 21)', 'rgb(70, 56, 194)', 'rgb(46, 184, 92)', 'rgb(31, 63, 219)'], 
                borderColor: ['rgb(58, 58, 58)', 'rgb(58, 58, 58)', 'rgb(58, 58, 58)', 'rgb(58, 58, 58)', 'rgb(58, 58, 58)', 'rgb(58, 58, 58)'], 
                data: chartdata
              }] 
            }, 
      
            // Configuration options go here 
            options: { 
                legend: {
                    display: true,
                    position: 'left',
                    labels: {
                        fontColor: '#B7BBBF'
                    }
                },
                scales: { 
                    xAxes: [{ 
                        display: false 
                    }], 
                    yAxes: [{ 
                        display: false,
                        ticks: { 
                            beginAtZero: true 
                        } 
                    }] 
                } 
            } 
        }); 
    } 


    function get_versionData(url) {
        $.getJSON( url, {
          format: "json",
        })
        .done(function(data) {
            console.log(">>> version data updated")
            let notary_colors = data.chart_data.colors_dict
            for (notary in notary_colors) {
                notary_colors[notary] = notary_colors[notary].reverse()
            }
            let hour_labels = data.chart_data.hours_list.reverse()

            let local_hour_labels = []

            
            for (i in hour_labels) {
                local_hour_labels[i] = local_date_str(hour_labels[i])
                console.log(local_hour_labels[i])
                if (local_hour_labels[i].split(" ")[1] == "00:00:00") {
                    local_hour_labels[i] = local_hour_labels[i].split(" ")[0]
                } else {
                    local_hour_labels[i] = local_hour_labels[i].split(" ")[1].substring(0, 5)
                }
            }

            data_1 = [
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1
                ]
            data_0 = [
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0
                ]

            var datasets = []
            var notary_labels = []
            for (let i = 0; i < local_hour_labels.length; i++) {
                let backgroundColor = []
                let j = 0
                for (notary in notary_colors) {
                    if (i == 0) {
                        notary_labels[j] = notary
                    }
                    color = notary_colors[notary][i]
                    backgroundColor[j] = color;
                    j++;
                }
                datasets[i] = {
                axis: 'y',
                data: _data = ((i == 0) ? data_0 : data_1),
                backgroundColor: backgroundColor,
                fill: false,
                  borderColor: backgroundColor,
                  borderWidth: 0,
                  borderRadius: 10
                }
            }
            const config = {
              type: 'horizontalBar',
              data : {
                  labels: notary_labels,
                  datasets: datasets,
                },
              options: {
                maintainAspectRatio: false,
                legend: {
                    display: false
                },
                tooltips: {
                    callbacks: {
                        label: function(tooltipItem, data) {
                            var label = local_hour_labels[tooltipItem.datasetIndex]
                            return label;
                        }
                    }
                },
                scales: {
                    xAxes: [
                        {
                            position: 'top',
                            type: 'category',
                            labels: local_hour_labels,
                            gridLines: {
                                display: true,
                                drawBorder: false,
                                offsetGridLines: true,
                                color: '#33333300'
                            },
                            stacked: true,
                            ticks: {
                                autoSkip: false,
                                maxRotation: 90,
                                minRotation: 90,
                                display: true,
                                beginAtZero: true,
                                fontFamily: "Helvetica, sans-serif",
                                fontSize: 13,
                                min: 0,
                                max: 24
                            },

                        },
                        {
                            position: 'bottom',
                            type: 'category',
                            labels: local_hour_labels,
                            gridLines: {
                                display: true,
                                drawBorder: false,
                                color: '#33333399'
                            },
                            scaleLabel: {
                                display: false
                            },
                            stacked: true,
                            ticks: {
                                autoSkip: false,
                                maxRotation: 90,
                                minRotation: 90,
                                display: true,
                                beginAtZero: true,
                                fontFamily: "Helvetica, sans-serif",
                                fontSize: 13,
                                min: 0,
                                max: 25
                            },
                        }
                    ],
                    yAxes: [
                        {
                            gridLines: {
                                display: true,
                                drawBorder: false
                            },
                            scaleLabel: {
                                display: false
                            },
                            stacked: true,
                            ticks: {
                                autoSkip: false,
                                display: true,
                                fontFamily: "Helvetica, sans-serif",
                                fontSize: 14
                            }
                        }
                    ]
                },
              }
            };
            var ctx = document.getElementById("myChart");
            myChart = new Chart(ctx, config);

        })
    }

    function update_chart() {
        var start = Date.parse($('#start').datetimepicker('getValue'))/1000;
        var end = Date.parse($('#end').datetimepicker('getValue'))/1000;
        myChart.destroy()
        console.log(start)
        console.log(end)
        url = "/api/atomicdex/version_stats_by_hour/?chart=1&start="+start+"&end="+end
        get_versionData(url)
    }


	function make_graph(graphtype, url, id) {
	    $.ajax({ 
			method: "GET", 
			url: '/api/graph_json/balances/?coin={{ coin }}', 
			success: function(data) { 
				//document.getElementById('graph_title').innerHTML = data.chartLabel;
				if (graphtype == 'line') {
					drawLineGraph(data, 'myChartline');
				}
				else if (graphtype == 'bar') {
					drawBarGraph(data, 'myChartBar');
				}
			}, 
			error: function(error_data) { 
				console.log(error_data); 
			} 
	    }) 
	}

</script>