function removeSeparators () {
  var numeric = $(this).attr("value");
  numeric = numeric.replace(/,/g, "");
  $(this).attr("value", numeric);
}
function addSeparators () {
  var numeric = $(this).attr("value");
  var dot = numeric.lastIndexOf('.');
  var commapart = "";
  if (dot != -1) {
    commapart = numeric.substring(dot);
    numeric = numeric.substring(0, dot);
  }
  newnumeric = "";
  while (numeric.length > 3) {
    newnumeric = "," + numeric.substr(numeric.length - 3, 3) + newnumeric;
    numeric = numeric.substring(0, numeric.length - 3);
  }
  numeric = numeric + newnumeric + commapart;
  $(this).attr("value", numeric);
}

$(document).ready(function () {
  $(".numeric").focus(removeSeparators);
  $(".numeric").blur(addSeparators);
  $("form").submit(function () {
    $(".numeric").focus();
  });
});
