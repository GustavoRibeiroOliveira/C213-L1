const tabs = document.querySelectorAll('.tab');
const contentBox = document.getElementById('box-content');

function switchTab(index) {
    tabs.forEach((tab, i) => {
        tab.classList.toggle('active', i === index);
    });

    if (index === 0) {
        contentBox.textContent = 'Conteúdo da Aba 1';
    } else {
        contentBox.textContent = 'Conteúdo da Aba 2';
    }
}
