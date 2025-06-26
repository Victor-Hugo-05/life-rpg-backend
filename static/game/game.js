document.getElementById('startGameBtn').addEventListener('click', function () {
  document.getElementById('game').classList.remove('hidden');
  document.getElementById('startGameBtn').classList.add('hidden');
});

let clicks = 0;
let xp = 0;

document.getElementById('clickBtn').addEventListener('click', function () {
  clicks++;
  document.getElementById('clicks').innerText = clicks;

  if (clicks >= 10) {
    xp += 10;  // Ganha 10 XP após 10 cliques
    document.getElementById('message').innerText = "Você levantou o peso! +10 XP de Força!";
    document.getElementById('xp').innerText = xp;
    clicks = 0;  // Reseta os cliques
  }
});
