$(document).ready(function () {
  //Datepicker from https://jqueryui.com/datepicker/
  $(".datepicker").datepicker({
    dateFormat: "dd MM, yy"
  });

  //Bootstrap tab buttons from https://getbootstrap.com/docs/4.6/components/navs/#javascript-behavior
  $(".button-goal").click(function(){
    $('#nav-goal-tab').tab('show')
  });
  $(".button-reality").click(function(){
    $('#nav-reality-tab').tab('show')
  });
  $(".button-options").click(function(){
    $('#nav-options-tab').tab('show')
  });
  $(".button-wayforward").click(function(){
    $('#nav-wayforward-tab').tab('show')
  });
  
});