let header_url = "__header_url__";
let ajax_url = "__ajax_url__";
let table_name = "#__name__-table";
let name = "__name__";

$.ajax({url: header_url, success: function(result){
    let header = result;
    header[header.length -1]['cellClick'] = function(e, cell){
        if(confirm('Are you sure you want to delete this entry?')){
            cell.getRow().delete();
        }
    };

    let data_count = 0;
    let table = new Tabulator(table_name, {
        ajaxURL: ajax_url,
        index: "key",
        movableRows: true,
        addRowPos: "bottom",
        layout: "fitDataFill",
        height: "311px",
        columns: result
    });

    function cellEdited(){
        let data = table.getData();
        let text_area = $('#'+name);
        text_area.val(JSON.stringify(data));
    }

    table.on("dataLoaded", function(data){
        data_count = data.length;
        cellEdited();
    });

    table.on("cellEdited", function(cell){
        cellEdited();
    });

    document.getElementById("add-row").addEventListener("click", function(){
        data_count++;
        table.addRow({'key': data_count});
    });

    document.getElementById("export-data").addEventListener("click", function() {
        let data = table.getData()
        let data_json = JSON.stringify(data, null, 2);
        let blob = new Blob([data_json], {type: "text/plain;charset=utf-8"});

        let url = window.URL.createObjectURL(blob);
        let link = document.createElement('a');
        link.href = url;
        link.download = "data.json"; // Name of the file to download
        document.body.appendChild(link); // Append link to body
        link.click(); // Simulate click to download file
        document.body.removeChild(link); // Remove the link after downloading
        window.URL.revokeObjectURL(url); // Free up storage--optional but recommended
    });


    document.getElementById("clear-data").addEventListener("click", function() {
        if(confirm('Are you sure you want to clear all entries?')){
            table.clearData();
            cellEdited();
        }
    });

}, error: function(result){
    console.log(result);
    }, dataType: 'json'});
