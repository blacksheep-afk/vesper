// Presentation controls only. There is no approval, execution or network action.
document.querySelectorAll('[data-view]').forEach(button => {
  button.addEventListener('click', () => {
    const split = button.dataset.view === 'split';
    document.getElementById('split-view').hidden = !split;
    document.getElementById('unified-view').hidden = split;
    document.querySelectorAll('[data-view]').forEach(item => {
      item.setAttribute('aria-pressed', String(item === button));
    });
  });
});
document.getElementById('print-report').addEventListener('click', () => window.print());
document.querySelectorAll('.nav-item').forEach(link => {
  link.addEventListener('click', () => {
    document.querySelectorAll('.nav-item').forEach(item => item.classList.toggle('active', item === link));
  });
});
