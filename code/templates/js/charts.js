
        // ChartJS functions
        <script>
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
        </script>