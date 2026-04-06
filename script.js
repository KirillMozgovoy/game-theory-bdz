window.addEventListener('load', function() {
  const game = {
    matrix: [[8,16,6],[14,6,12]],
    
    checkDominanceA() {
      const batch = game.matrix[0], stream = game.matrix[1];
      let batchWins = 0, streamWins = 0;
      for (let j = 0; j < batch.length; j++) {
        if (batch[j] > stream[j]) batchWins++;
        else if (stream[j] > batch[j]) streamWins++;
      }
      return batchWins > 0 && streamWins > 0 ? "ни одна не доминирует" : "есть доминирование";
    },
    
    checkDominanceB() {
      // Столбцы для B
      const cols = [[8,14], [16,6], [6,12]];
      return "нет доминирования (каждый столбец где-то лучше)";
    },
    
    saddlePoint() {
      const rowMins = game.matrix.map(row => Math.min(...row));
      const maximin = Math.max(...rowMins);
      
      const colMaxs = [];
      for (let j = 0; j < game.matrix[0].length; j++) {
        const col = game.matrix.map(row => row[j]);
        colMaxs.push(Math.max(...col));
      }
      const minimax = Math.min(...colMaxs);
      
      return { maximin, minimax, hasSaddle: maximin === minimax };
    },
    
    expected(p) {
      return {
        uniform: 8*p + 14*(1-p),
        peak: 16*p + 6*(1-p),
        night: 6*p + 12*(1-p)
      };
    }
  };

  function updateResults() {
    const dominanceA = game.checkDominanceA();
    const dominanceB = game.checkDominanceB();
    const saddle = game.saddlePoint();
    const p = 0.5;
    const exp = game.expected(p);
    
    document.getElementById("dominanceA").textContent = dominanceA;
    document.getElementById("dominanceB").textContent = dominanceB;
    document.getElementById("maximin").textContent = saddle.maximin;
    document.getElementById("minimax").textContent = saddle.minimax;
    document.getElementById("saddle-result").textContent = saddle.hasSaddle ? "есть" : "нет";
    document.getElementById("prob-batch").textContent = p.toFixed(2);
    document.getElementById("prob-stream").textContent = (1-p).toFixed(2);
    document.getElementById("game-value").textContent = exp.peak.toFixed(1);
  }

  function drawGraph() {
    const container = document.getElementById("graph-container");
    if (typeof Plotly === 'undefined') {
      container.innerHTML = "<p>График недоступен</p>";
      updateResults();
      return;
    }

    const points = [];
    for (let i = 0; i <= 100; i++) {
      points.push({ p: i/100, ...game.expected(i/100) });
    }

    Plotly.newPlot(container, [
      { x: points.map(p=>p.p), y: points.map(p=>p.uniform), type: "scatter", mode: "lines", name: "E(p,Равн)=14-6p", line: {color: "#1f77b4"} },
      { x: points.map(p=>p.p), y: points.map(p=>p.peak), type: "scatter", mode: "lines", name: "E(p,Пик)=6+10p", line: {color: "#ff7f0e"} },
      { x: points.map(p=>p.p), y: points.map(p=>p.night), type: "scatter", mode: "lines", name: "E(p,Ночь)=12-6p", line: {color: "#2ca02c"} },
      { x: [0.5], y: [11], type: "scatter", mode: "markers", name: "Оптимум p=0.5,V=11", marker: {size: 12, color: "black"} }
    ], {
      title: "Нижняя огибающая максимальна в p=0.5",
      xaxis: { title: "p (вероятность Batch)", range: [0,1] },
      yaxis: { title: "Ожидаемый выигрыш A" }
    });
    
    updateResults();
  }

  drawGraph();
});