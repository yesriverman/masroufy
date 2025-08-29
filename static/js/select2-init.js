document.addEventListener('DOMContentLoaded', function () {
  $('.select2').select2({
    width: '100%',
    dir: 'rtl',
    minimumResultsForSearch: Infinity, // disables search if not needed
    placeholder: '-- اختر المجموعة --',
    allowClear: true
  });
});
