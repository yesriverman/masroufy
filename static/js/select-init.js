document.addEventListener('DOMContentLoaded', function () {
  // 🗂️ Initialize Tom Select
  document.querySelectorAll('.tom-select').forEach(select => {
    if (!select.tomselect) {
      new TomSelect(select, {
        maxOptions: 10,
        dropdownClass: 'dropdown-menu',
        controlInput: '<input>',
      });
    }
  });

  // 📅 Initialize Flatpickr
  flatpickr('.flatpickr', {
    dateFormat: 'Y-m-d',
    locale: 'ar',
    disableMobile: true,
  });
});

new TomSelect('select[name="year"]', {
  maxOptions: 10,
  dropdownClass: 'dropdown-menu',
  controlInput: '<input>',
});





// document.addEventListener('DOMContentLoaded', function () {
//   const selects = document.querySelectorAll('.select2, .tom-select');
//   selects.forEach(select => {
//     new TomSelect(select, {
//       maxOptions: 10,
//       dropdownClass: 'dropdown-menu',
//       controlInput: '<input>',
//       render: {
//         option: function(data, escape) {
//           return `<div class="text-truncate">${escape(data.text)}</div>`;
//         }
//       }
//     });
//   });
// });


// document.addEventListener('DOMContentLoaded', function () {
//   flatpickr("#id_date", {
//     dateFormat: "Y-m-d",
//     locale: "ar", // optional for Arabic
//     disableMobile: true, // forces desktop-style picker on mobile
//   });
// });
