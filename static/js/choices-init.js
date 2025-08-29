document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.choices-select').forEach(function (el) {
    new Choices(el, {
      searchEnabled: false,
      itemSelectText: '',
      shouldSort: false,
      classNames: {
        containerInner: 'form-select-sm',
      }
    });
  });
});
