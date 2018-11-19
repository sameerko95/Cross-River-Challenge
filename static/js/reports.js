function getStats(){
    $("[name='aggregations']").html("");
    $("[name='aggregations']").html("<div class='loader'></div>");

    $("#monthly").html("");
    $("#monthly").html("<div class='loader'></div>");

    $("#credit-based").html("");
    $("#credit-based").html("<div class='loader'></div>");

    $.ajax({
        url : "https://oc5eswj57b.execute-api.us-east-1.amazonaws.com/version-1/get-loan-stats",
        type : "GET",
        contentType : "application/json",
        data: {
            "year" : $('#year').val()
        },
        success : function(data) {
            $("[name='aggregations']").html("");
            $('#applied')[0].innerHTML = "$" + data.loan_amnt.toLocaleString();
            $('#funded')[0].innerHTML = "$" + data.funded_amnt.toLocaleString();
            $('#committed')[0].innerHTML = "$" + data.funded_amnt_inv.toLocaleString();
        },
        error : function(request, error) {
            console.log("Error function" + JSON.stringify(request));
            console.log("Error function" + JSON.stringify(error));
        }
    });

    $.ajax({
        url : "https://oc5eswj57b.execute-api.us-east-1.amazonaws.com/version-1/get-graph-data",
        type : "GET",
        contentType : "application/json",
        data: {
            "year" : $('#year').val()
        },
        success : function(data) {
            var monthlyVolume = data["monthlyVolume"];
            var creditBased = data["creditBasedAvg"];
            var data = [
                {
                  x: Object.keys(monthlyVolume),
                  y: Object.values(monthlyVolume),
                  type: 'bar'
                }
            ];
            
            var layout = {
                title:'Monthly Loan Volume for Year ' + $('#year').val(),
                width: 550,
                height: 450
            };
            $("#monthly").html("");

            var trace_x = ['Dec', 'Nov', 'Oct', 'Sep', 'Aug', 'July', 'June', 'May', 'Apr', 'Mar', 'Feb', 'Jan'];

            Plotly.newPlot('monthly', data, layout);

            var creditBasedGraphData = [];
            var gradeWiseEntries = Object.entries(creditBased);
            
            for(index=0; index<gradeWiseEntries.length; index++){
                var grade = gradeWiseEntries[index][0];
                var monthWise = gradeWiseEntries[index][1];

                var trace_y = [];
                for(key in monthWise){
                    console.log(key, monthWise[key]);
                    trace_y.push(monthWise[key]);
                }

                var trace = {
                    x: trace_x,
                    y: trace_y,
                    mode: 'lines+markers',
                    name: grade
                };
                creditBasedGraphData.push(trace);
            }
            6
            var layout = {
                title:'Loans Issued By Credit Score',
                width: 600,
                height: 450
            };
            $("#credit-based").html("");
            Plotly.newPlot('credit-based', creditBasedGraphData, layout);

        },
        error : function(request, error) {
            console.log("Error function" + JSON.stringify(request));
            console.log("Error function" + JSON.stringify(error));
        }
    });
}

$(document).ready(function(){
    getStats();
})