let table_name = "#__name__-table";
let header = [
        {
            'rowHandle': true,
            'formatter': "handle",
            'headerSort': false,
            'frozen': true,
            'width': 30,
            'minWidth': 30
        },
        {'title': 'Identifier', 'field': 'key', 'editor': 'input'},
        {'title': 'Value', 'field': 'value', 'editor': 'input'}
    ];

var data_count = 0;
var table = new Tabulator(table_name, {
    data: [],
    index: "key",
    movableRows: true,
    addRowPos: "bottom",
    layout: "fitDataFill",
    height: "311px",
    columns: header
});

document.getElementById("add-row").addEventListener("click", function(){
    table.addRow({'key': data_count});
    data_count++;
});