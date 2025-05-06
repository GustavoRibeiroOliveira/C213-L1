document.addEventListener("DOMContentLoaded", () => {

});

function switchTab(index) {
    const tabs = document.querySelectorAll('.tab');
    const boxContent = document.getElementById('box-content');
    tabs.forEach((tab, i) => {
        tab.classList.toggle('active', i === index);
    });

    // Esconder todos os conteúdos
    const allContent = document.querySelectorAll('[id^="tab-"]');
    allContent.forEach(content => {
        content.style.display = 'none';
    });

    // Mostrar o conteúdo da aba selecionada
    const contentId = `tab-${index}-content`;
    document.getElementById(contentId).style.display = 'block';

    // Mostrar ou esconder os botões de PID
    const pidButtons = document.getElementById('pid-buttons');
    if (index === 1) {
        pidButtons.style.display = 'flex';
    } else {
        pidButtons.style.display = 'none';
    }

    if (index === 1){
        document.getElementById('zn').click()
        boxContent.style['margin-right'] = '120px';
    }
    else {
        boxContent.style['margin-right'] = '0px';
    }
}


function gerarPID(method) {
    const k = document.getElementById('k').innerText;
    const tau = document.getElementById('tau').innerText;
    const theta = document.getElementById('theta').innerText;
    const lastTime = document.getElementById('last_time').innerText;

    if (method === 'manual') {
        abrirModal();
        return;
    }

    coloca_botao_pid_como_ativo(method)

    axios.post("/gerar_pid", {
        k: k,
        tau: tau,
        theta: theta,
        method: method,
        last_time: lastTime
    }).then(response => {
        const imgBase64 = response.data.image;
        const kp = response.data.kp.toFixed(3);
        const ti = response.data.ti.toFixed(3);
        const td = response.data.td.toFixed(3);
        const overshoot = response.data.overshoot.toFixed(2);

        const html = `
            <div class="inputs-container">
                <div class="item"><span><strong>Kp:</strong> ${kp}<span></div>
                <div class="item"><span><strong>Ti:</strong> ${ti}</span></div>
                <div class="item"><span><strong>Td:</strong> ${td}</span></div>
                <div class="item"><span><strong>Overshoot:</strong> ${overshoot}%</span></div>
            </div>
            <img id="pid-img" src="data:image/png;base64,${imgBase64}" alt="Resposta PID" style="max-width: 100%;">
        `;

        document.getElementById('pid-resultados').innerHTML = html;

        // // Mostrar botão de download
        // const downloadBtn = document.getElementById('download-btn');
        // downloadBtn.style.display = 'inline-block';
        //
        // // Atualizar função do botão para baixar a imagem
        // downloadBtn.onclick = () => {
        //     const a = document.createElement('a');
        //     a.href = `data:image/png;base64,${imgBase64}`;
        //     a.download = `grafico_pid_${method}.png`;
        //     document.body.appendChild(a);
        //     a.click();
        //     document.body.removeChild(a);
        // };

    }).catch(error => {
        console.error("Erro ao gerar PID:", error);
        alert("Erro ao gerar o gráfico PID.");
    });
}

function coloca_botao_pid_como_ativo(method) {
    const buttons = document.querySelectorAll('#pid-buttons .btn');

    buttons.forEach(btn => {
        if (btn.id !== 'download-btn') {
            btn.classList.toggle('active', btn.id === method);
        }
    });
}

function abrirModal() {
    document.getElementById('manual-modal').style.display = 'flex';
}

function fecharModal() {
    document.getElementById('manual-modal').style.display = 'none';
}

function gerarPidManual(kp, ti, td) {
    const k = document.getElementById('k').innerText;
    const tau = document.getElementById('tau').innerText;
    const theta = document.getElementById('theta').innerText;
    const lastTime = document.getElementById('last_time').innerText;

    coloca_botao_pid_como_ativo('manual')

    axios.post("/gerar_pid", {
        k: k,
        tau: tau,
        theta: theta,
        method: 'manual',
        kp: kp,
        ti: ti,
        td: td,
        last_time: lastTime
    }).then(response => {
        const imgBase64 = response.data.image;
        const kp = response.data.kp.toFixed(3);
        const ti = response.data.ti.toFixed(3);
        const td = response.data.td.toFixed(3);
        const overshoot = response.data.overshoot.toFixed(2);

        const html = `
            <div class="inputs-container">
                <div class="item"><span><strong>Kp:</strong> ${kp}<span></div>
                <div class="item"><span><strong>Ti:</strong> ${ti}</span></div>
                <div class="item"><span><strong>Td:</strong> ${td}</span></div>
                <div class="item"><span><strong>Overshoot:</strong> ${overshoot}%</span></div>
            </div>
            <img id="pid-img" src="data:image/png;base64,${imgBase64}" alt="Resposta PID" style="max-width: 100%;">
        `;

        document.getElementById('pid-resultados').innerHTML = html;

        // // Mostrar botão de download
        // const downloadBtn = document.getElementById('download-btn');
        // downloadBtn.style.display = 'inline-block';
        //
        // // Atualizar função do botão para baixar a imagem
        // downloadBtn.onclick = () => {
        //     const a = document.createElement('a');
        //     a.href = `data:image/png;base64,${imgBase64}`;
        //     a.download = `grafico_pid_${method}.png`;
        //     document.body.appendChild(a);
        //     a.click();
        //     document.body.removeChild(a);
        // };

        fecharModal();

    }).catch(error => {
        console.error("Erro ao gerar PID:", error);
        alert("Erro ao gerar o gráfico PID.");
    });
}

function confirmarManual() {
    const kp = parseFloat(document.getElementById('manual-kp').value);
    const ti = parseFloat(document.getElementById('manual-ti').value);
    const td = parseFloat(document.getElementById('manual-td').value);

    if (isNaN(kp) || isNaN(ti) || isNaN(td)) {
        alert("Por favor, preencha todos os campos corretamente.");
        return;
    }
    gerarPidManual(kp, ti, td);
}