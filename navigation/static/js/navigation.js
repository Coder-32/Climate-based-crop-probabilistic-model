document.addEventListener('DOMContentLoaded', function () {
  const navCards = document.querySelectorAll('.nav-card');

  navCards.forEach(card => {
    card.addEventListener('click', function () {
      card.classList.add('active-card');
      setTimeout(() => card.classList.remove('active-card'), 220);
    });
  });
});
