const searchInputs = document.querySelectorAll('[data-search]');

searchInputs.forEach((input) => {
  const target = input.getAttribute('data-search');
  const table = document.querySelector(`[data-table="${target}"] tbody`);
  if (!table) return;

  input.addEventListener('input', () => {
    const term = input.value.trim().toLowerCase();
    const rows = table.querySelectorAll('tr');

    rows.forEach((row) => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(term) ? '' : 'none';
    });
  });
});
