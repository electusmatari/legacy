function humaneint (num) {
    if (num < 0) {
        prefix = "-";
        num *= -1;
    } else {
        prefix = "";
    }
    num = num + "";
    s = "";
    while (num.length > 3) {
        if (s.length > 0) {
            s = "," + s;
        }
        s = num.substr(num.length - 3) + s;
        num = num.substr(0, num.length - 3);
    }
    if (num.length > 0) {
        if (s.length > 0) {
            s = num + "," + s;
        } else {
            s = num;
        }
    }
    return prefix + s;
}

function humane (num) {
    num = num.toFixed(2) + "";
    postcomma = num.substr(-2);
    precomma = num.substr(0, num.length - 3);
    return humaneint(precomma) + "." + postcomma;
}

function calculator (result, search, data, table) {
    quantities = [];
    for (i in table) {
        quantities[i] = 0;
    }
    function write_table () {
        needle = new RegExp(search.val(), "i");
        html = '<table class="data">';
        html += '<tr><th>Qty</th><th>Typename</th><th>Price</th></tr>';
        rowi = 0;
        for (row in table) {
            typename = table[row][0];
            if (typename.search(needle) == -1) {
                continue;
            }
            if (rowi % 2) {
                cls = "odd";
            } else {
                cls = "even";
            }
            rowi += 1;
            if (quantities[row]) {
                qty = quantities[row];
            } else {
                qty = "";
            }
            html += ('<tr id="tr' + row + '" class="' + cls + '">' +
                     '<td class="qty">' +
                     '<input type="text" size="3" name="qty' + row + '" ' +
                     'value="' + qty + '" autocomplete="off" />' +
                     '</td>' +
                     '<td class="typename">' + table[row][0] + "</td>" +
                     '<td class="price">' + humane(table[row][1]) + "</td>" +
                     '</tr>');
        }
        html += '</table>';
        data.html(html);
        data.find("input").blur(write_results_from_data);
        data.find("input").keydown(update_results_from_data);
    }

    function update_table () {
        needle = search.val();
        if (needle.length == 0 || needle.length >= 3) {
            write_table();
        }
    }

    function write_results () {
        total = 0;
        html = '<table class="result">';
        html += '<tr><th>Quantity</th><th>Type</th><th>p.u.</th>';
        html += '<th>Price</th></tr>';
        for (rowi in table) {
            qty = quantities[rowi];
            if (qty) {
                if (rowi % 2) {
                    cls = "odd";
                } else {
                    cls = "even";
                }
                i = $(this).attr("name").substr(3);
                typename = table[rowi][0];
                price = table[rowi][1];
                html += ('<tr class="' + cls + '">' +
                         '<td class="quantity">' +
                         '<input type="text" size="2" ' + 
                         'name="qty' + rowi + '" ' +
                         'value="' + qty + '" autocomplete="off" />' +
                         humaneint(parseInt(qty)) +
                         '</td>' +
                         '<td class="name">' + typename + '</td>' +
                         '<td class="singleprice">' + humane(price) +
                         '</td>' +
                         '<td class="sumprice">' + humane(qty*price) +
                         '</td>' +
                         '</tr>');
                total += qty*price;
            }
        }
        $(".calcmod").each(function () {
                if ($(this).attr("checked")) {
                    total *= parseFloat($(this).attr("value"));
                }
            });
        html += '<tr class="total"><th colspan="3">Total:</td>';
        html += '<td class="totalprice">' + humane(total) + '</td>';
        html += "</table>";
        result.html(html);
        result.find("input").blur(write_results_from_results);
        result.find("input").keydown(update_results_from_results);
    }

    function update_results_from_data (e) {
        if (e.keyCode == 13) {
            write_results_from_data();
            return false;
        }
    }

    function write_results_from_results () {
        result.find("input").each(function () {
                qty = $(this).val();
                rowi = parseInt($(this).attr("name").substr(3));
                data.find("input[name=qty" + rowi + "]").val(qty);
                if (!qty) {
                    qty = 0;
                }
                quantities[rowi] = qty;
            });
        write_results();
    }

    function write_results_from_data () {
        data.find("input").each(function (i) {
                qty = $(this).val();
                if (!qty) {
                    qty = 0;
                }
                rowi = parseInt($(this).attr("name").substr(3));
                quantities[rowi] = qty;
            });
        write_results();
    }

    function update_results_from_results (e) {
        if (e.keyCode == 13) {
            write_results_from_results();
            return false;
        }
    }


    timeout = null;
    function search_changed () {
        if (timeout) {
            clearTimeout(timeout);
        }
        timeout = setTimeout(update_table, 10);
    }

    search.attr("autocomplete", "off");
    search.keydown(search_changed);
    search.focus();
    write_table();
    write_results();
    $(".calcmod").change(write_results);
}
