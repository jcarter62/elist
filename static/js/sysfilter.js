
// Loop through table rows
// https://stackoverflow.com/a/3065389

function applyfilter() {
    // lookup the filter string
    let e = document.getElementById('filtervalue');
    let filter = e.value.toLowerCase();

    let hide_class = 'hiderow';
    let show_class = 'showrow';
    // if filter string is empty, then show all rows
    let table = document.getElementById("system_table");
    let row_elem;
    for (let i = 0, row; row = table.rows[i]; i++) {
        let showrow = false;
        let rowid = row.id;
        for (var j = 0, col; col = row.cells[j]; j++) {
            var txt = col.textContent.toLowerCase();
            if (txt.includes(filter)) {
                showrow = true;
            }
        }
        if (rowid > '') {
            // rowid must be not be an empty string in order
            // to have a row of data.
            row_elem = document.getElementById(rowid);
            if (showrow) {
                row_elem.setAttribute('class', show_class);
            } else {
                row_elem.setAttribute('class', hide_class);
            }
        }
    }
}