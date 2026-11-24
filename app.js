// Small helpers for the form. The app still works without JavaScript.
(function () {
  var form = document.getElementById('check-form');
  var button = document.getElementById('submit-btn');

  // Bio character counter
  document.querySelectorAll('[data-count-for]').forEach(function (el) {
    var field = form.querySelector('[name=' + el.dataset.countFor + ']');
    var update = function () { el.textContent = field.value.length + ' / ' + field.maxLength; };
    field.addEventListener('input', update); update();
  });

  // Basic checks before sending
  if (form) {
    form.addEventListener('submit', function (e) {
      var problems = [];
      if (!form.username.value.trim()) problems.push('Enter the username.');
      ['followers', 'following', 'posts', 'age_months'].forEach(function (n) {
        var v = form[n].value;
        if (v === '' || Number(v) < 0) problems.push('Fill in a number (0 or more) for ' + n.replace('_', ' ') + '.');
      });
      if (problems.length) { e.preventDefault(); alert(problems.join('\n')); return; }
      button.disabled = true; button.textContent = 'Checking...';
    });
  }
})();
