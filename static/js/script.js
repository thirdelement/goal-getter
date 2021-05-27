$(document).ready(function () {
  //Datepicker from https://jqueryui.com/datepicker/
  $(".datepicker").datepicker({
    dateFormat: "dd MM, yy"
  });

  //Bootstrap tab buttons from https://getbootstrap.com/docs/4.6/components/navs/#javascript-behavior
  $(".button-goal").click(function () {
    $('#nav-goal-tab').tab('show')
  });
  $(".button-reality").click(function () {
    $('#nav-reality-tab').tab('show')
  });
  $(".button-options").click(function () {
    $('#nav-options-tab').tab('show')
  });
  $(".button-wayforward").click(function () {
    $('#nav-wayforward-tab').tab('show')
  });

  //Add validity message from https://stackoverflow.com/questions/32829776/setting-custom-html5-validity-message-property-ignores-pattern-regex
  $('textarea, input').on('input', function () {
    $(this).get(0).reportValidity();
  });

  //Check add_goal form for validity and display message when click submit.  Credit: https://stackoverflow.com/questions/45789010/how-to-use-html-form-checkvalidity/45789752
  $("#submit-add_goal").click(function (action) {
    var forms = document.getElementById('form-add_goal')
    if (!forms.checkValidity()) {
      document.getElementById('notification').style.display = 'block';
      document.getElementById('alert').style.display = 'block';
    }
  });

  //Check edit_goal form for validity and display message when click on submit buttons.
  $(".submit").click(function (action) {
    var forms = document.getElementById('form-edit_goal')
    if (!forms.checkValidity()) {
      document.getElementById('notification').style.display = 'block';
      document.getElementById('alert').style.display = 'block';
    }
  });
});