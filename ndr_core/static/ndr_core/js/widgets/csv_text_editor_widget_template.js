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

    table.on("dataLoaded", function(data){
        data_count = data.length;
    });

    table.on("cellEdited", function(cell){
        let table_data = table.getData();
        let table_data_json = JSON.stringify(table_data);
        let text_area = $('#'+name);
        text_area.val(table_data_json);

    });

    document.getElementById("add-row").addEventListener("click", function(){
        data_count++;
        table.addRow({'key': data_count});
    });

}, error: function(result){
    console.log(result);
    }, dataType: 'json'});
