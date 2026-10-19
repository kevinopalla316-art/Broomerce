document.addEventListener('DOMContentLoaded', function () {
  const toggleButtons = document.querySelectorAll('.toggle-password');

  toggleButtons.forEach((button) => {
    button.addEventListener('click', function () {
      const targetInput = document.getElementById(button.dataset.target);
      if (!targetInput) return;

      const isPassword = targetInput.type === 'password';
      targetInput.type = isPassword ? 'text' : 'password';

      if (isPassword) {
        button.setAttribute('aria-label', 'Hide password');
        button.setAttribute('title', 'Hide password');
        button.innerHTML = `
          <svg class="eye-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M3 3l18 18" fill="none" stroke="currentColor" stroke-width="2"/>
            <path d="M10.6 10.6a3 3 0 0 0 4.2 4.2" fill="none" stroke="currentColor" stroke-width="2"/>
            <path d="M9.88 5.08A10.94 10.94 0 0 1 12 5c6.5 0 10 7 10 7a18.05 18.05 0 0 1-2.62 3.2" fill="none" stroke="currentColor" stroke-width="2"/>
            <path d="M6.5 6.5C4.7 7.9 3.3 9.5 2 12s3.5 6 10 6c1.34 0 2.58-.2 3.7-.56" fill="none" stroke="currentColor" stroke-width="2"/>
          </svg>`;
      } else {
        button.setAttribute('aria-label', 'Show password');
        button.setAttribute('title', 'Show password');
        button.innerHTML = `
          <svg class="eye-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12z" fill="none" stroke="currentColor" stroke-width="2"/>
            <circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="2"/>
          </svg>`;
      }
    });
  });

  const forms = document.querySelectorAll('form');
  forms.forEach((form) => {
    form.addEventListener('submit', function (event) {
      const requiredFields = form.querySelectorAll('[required]');
      let valid = true;

      requiredFields.forEach((field) => {
        if (!field.value.trim()) {
          valid = false;
          field.style.borderColor = '#d05d5d';
        } else {
          field.style.borderColor = '';
        }
      });

      if (!valid) {
        event.preventDefault();
      }
    });
  });
});
