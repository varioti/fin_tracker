$(document).ready(function() {
    let resume = document.getElementById("resume");
    let today = new Date();

    // compute start date
    let week = new Date(today - 7 * 24 * 60 * 60 * 1000);
    let month = new Date(today - 31 * 24 * 60 * 60 * 1000);
    let month3 = new Date(today - 92 * 24 * 60 * 60 * 1000);
    let month6 = new Date(today - 183 * 24 * 60 * 60 * 1000);
    let year = new Date(today - 365 * 24 * 60 * 60 * 1000);

    // compute values
    let orders = document.getElementById("orders");

    let total_week = {"buy":0, "sell":0};
    let total_month = {"buy":0, "sell":0};
    let total_month3 = {"buy":0, "sell":0};
    let total_month6 = {"buy":0, "sell":0};
    let total_year = {"buy":0, "sell":0};
    let total_all = {"buy":0, "sell":0};

    let mean_week = {"buy":0, "sell":0};
    let mean_month = {"buy":0, "sell":0};
    let mean_month3 = {"buy":0, "sell":0};
    let mean_month6 = {"buy":0, "sell":0};
    let mean_year = {"buy":0, "sell":0};
    let mean_all = {"buy":0, "sell":0};

    let date, mean, total, type
    for (let i = 1; i < orders.rows.length; i++) {
        date = new Date(orders.rows[i].cells[6].innerHTML);
        mean = Number(orders.rows[i].cells[4].innerHTML.slice(0, -2));
        total = Number(orders.rows[i].cells[3].innerHTML.slice(0, -2));

        // keep orders filled
        if (orders.rows[i].cells[4].innerHTML != "NULL") {

            // check if order is SELL or BUY
            if (orders.rows[i].cells[1].innerHTML == "BUY") {
                type = "buy";
            } else {
                type = "sell";
            }

            // keep last week orders
            if (date >= week) {
                if (total_week[type] == 0) {
                    mean_week[type] = mean;
                } else {
                    mean_week[type] = (total_week[type]*mean_week[type] + total*mean) / (total_week[type] + total);
                }
                total_week[type] += total;
            }

            // keep last month orders
            if (date >= month) {
                if (total_month[type] == 0) {
                    mean_month[type] = mean;
                } else {
                    mean_month[type] = (total_month[type]*mean_month[type] + total*mean) / (total_month[type] + total);
                }
                total_month[type] += total;
            }

            // keep last 3 months orders
            if (date >= month3) {
                if (total_month3[type] == 0) {
                    mean_month3[type] = mean;
                } else {
                    mean_month3[type] = (total_month3[type]*mean_month3[type] + total*mean) / (total_month3[type] + total);
                }
                total_month3[type] += total;
            }

            // keep last 6 months orders
            if (date >= month6) {
                if (total_month6[type] == 0) {
                    mean_month6[type] = mean;
                } else {
                    mean_month6[type] = (total_month6[type]*mean_month6[type] + total*mean) / (total_month6[type] + total);
                }
                total_month6[type] += total;
            }

            // keep last year orders
            if (date >= year) {
                if (total_year[type] == 0) {
                    mean_year[type] = mean;
                } else {
                    mean_year[type] = (total_year[type]*mean_year[type] + total*mean) / (total_year[type] + total);
                }
                total_year[type] += total;
            }

            // all orders
            if (total_all[type] == 0) {
                mean_all[type] = mean;
            } else {
                mean_all[type] = (total_all[type]*mean_all[type] + total*mean) / (total_all[type] + total);
            }
            total_all[type] += total;
        }
    }

    // update values week
    resume.rows[2].cells[2].innerHTML = Math.round(total_week["buy"] * 100) / 100;
    resume.rows[1].cells[2].innerHTML = Math.round(mean_week["buy"] * 100) / 100;
    resume.rows[4].cells[2].innerHTML = Math.round(total_week["sell"] * 100) / 100;
    resume.rows[3].cells[2].innerHTML = Math.round(mean_week["sell"] * 100) / 100;

    // update values month
    resume.rows[2].cells[3].innerHTML = Math.round(total_month["buy"] * 100) / 100;
    resume.rows[1].cells[3].innerHTML = Math.round(mean_month["buy"] * 100) / 100;
    resume.rows[4].cells[3].innerHTML = Math.round(total_month["sell"] * 100) / 100;
    resume.rows[3].cells[3].innerHTML = Math.round(mean_month["sell"] * 100) / 100;

    // update values 3 months
    resume.rows[2].cells[4].innerHTML = Math.round(total_month3["buy"] * 100) / 100;
    resume.rows[1].cells[4].innerHTML = Math.round(mean_month3["buy"] * 100) / 100;
    resume.rows[4].cells[4].innerHTML = Math.round(total_month3["sell"] * 100) / 100;
    resume.rows[3].cells[4].innerHTML = Math.round(mean_month3["sell"] * 100) / 100;

    // update values 6 months
    resume.rows[2].cells[5].innerHTML = Math.round(total_month6["buy"] * 100) / 100;
    resume.rows[1].cells[5].innerHTML = Math.round(mean_month6["buy"] * 100) / 100;
    resume.rows[4].cells[5].innerHTML = Math.round(total_month6["sell"] * 100) / 100;
    resume.rows[3].cells[5].innerHTML = Math.round(mean_month6["sell"] * 100) / 100;

    // update values year
    resume.rows[2].cells[6].innerHTML = Math.round(total_year["buy"] * 100) / 100;
    resume.rows[1].cells[6].innerHTML = Math.round(mean_year["buy"] * 100) / 100;
    resume.rows[4].cells[6].innerHTML = Math.round(total_year["sell"] * 100) / 100;
    resume.rows[3].cells[6].innerHTML = Math.round(mean_year["sell"] * 100) / 100;

    // update values all
    resume.rows[2].cells[7].innerHTML = Math.round(total_all["buy"] * 100) / 100;
    resume.rows[1].cells[7].innerHTML = Math.round(mean_all["buy"] * 100) / 100;
    resume.rows[4].cells[7].innerHTML = Math.round(total_all["sell"] * 100) / 100;
    resume.rows[3].cells[7].innerHTML = Math.round(mean_all["sell"] * 100) / 100;

});