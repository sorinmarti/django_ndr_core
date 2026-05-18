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

    // Get the initial data from the textarea
    let text_area = $('#'+name);
    let initial_data = [];
    try {
        let textarea_value = text_area.val();
        if (textarea_value && textarea_value.trim() !== '') {
            initial_data = JSON.parse(textarea_value);
        }
    } catch (e) {
        console.log("Error parsing initial data, will load from AJAX:", e);
    }

    let using_ajax = initial_data.length === 0;

    // Initialize table with data from textarea, or use AJAX as fallback
    let table = new Tabulator(table_name, {
        data: !using_ajax ? initial_data : undefined,
        ajaxURL: using_ajax ? ajax_url : undefined,
        index: "key",
        movableRows: true,
        addRowPos: "bottom",
        layout: "fitDataFill",
        height: "311px",
        columns: result
    });

    function cellEdited(){
        let data = table.getData();
        text_area.val(JSON.stringify(data));
    }

    // For local data: set count from initial_data; textarea is already correct from server render.
    // For AJAX data: update textarea once data arrives from the server.
    table.on("tableBuilt", function(){
        if (!using_ajax) {
            data_count = initial_data.length;
        }
    });

    table.on("dataLoaded", function(data){
        data_count = data.length;
        if (using_ajax) {
            // Only sync textarea from AJAX-loaded data; local data is already in the textarea.
            cellEdited();
        }
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
