function showall(type) {
    let table;
    if (type == 'd') {
        table = document.getElementById("dep_table");
    } else {
        table = document.getElementById("pf_table");
    }

    for (var i = 0, row; row = table.rows[i]; i++) {
             row.style.display = null;
    }
}

function showless(type) {
    let table;
    if (type == 'd') {
        table = document.getElementById("dep_table");
    } else {
        table = document.getElementById("pf_table");
    }

    for (var i = 6, row; row = table.rows[i]; i++) {
             row.style.display = "none";
    }
}