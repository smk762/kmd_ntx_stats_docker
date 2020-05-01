

// Create series
function createColumnSeries(x_field, y_field, name) {
  var series = chart.series.push(new am4charts.ColumnSeries());
  series.dataFields.valueY = y_field;
  series.dataFields.categoryX = x_field;
  series.name = name;
  series.tooltipText = "{name}: [b]{valueY}[/]";
  series.strokeWidth = 3;
  series.xAxis = x_categoryAxis;
  series.columns.template.width = am4core.percent(60);
    
  var bullet = series.bullets.push(new am4charts.CircleBullet());
  bullet.circle.stroke = am4core.color("#fff");
  bullet.circle.opacity = 0;
  
  var label = bullet.createChild(am4core.Label);
  label.text = "{value}";
  label.horizontalCenter = "middle";
  label.verticalCenter = "bottom";
  label.strokeWidth = 3;
  
  series.bulletsContainer.hide();
}

// Create series
function createLineSeries(x_field, y_field, name) {
  var series = chart.series.push(new am4charts.LineSeries());
  series.dataFields.valueY = y_field;
  series.dataFields.categoryX = x_field;
  series.name = name;
  series.tooltipText = "{name}: [b]{valueY}[/]";
  series.strokeWidth = 1;
  series.stroke = am4core.color("#fff");
  series.xAxis = x_categoryAxis;
  series.yAxis = pct_valAxis;
    
  var bullet = series.bullets.push(new am4charts.CircleBullet());
  bullet.circle.stroke = am4core.color("#fff");
  bullet.circle.strokeWidth = 3;
  
  var label = bullet.createChild(am4core.Label);
  label.text = "{value}";
  label.horizontalCenter = "middle";
  label.verticalCenter = "bottom";
  label.strokeWidth = 3;
  
  series.bulletsContainer.hide();
}