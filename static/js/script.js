$(document).ready(function () {
  //Datepicker from https://jqueryui.com/datepicker/
  $("#target_date").datepicker({
    dateFormat: "dd MM, yy"
  });
  
  //Accordion from https://jqueryui.com/accordion/
  $("#accordion").accordion({
    collapsible: true,
    active: false,
    header: "h4"
  });
  
});