# 📦 Projeto Prático C213 - Sistemas Embarcados

## 🚀 Tecnologias utilizadas

- [Python 3.12](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/)
- [PyWebView](https://pywebview.flowrl.com/)
- [NumPy](https://numpy.org/)
- [Matplotlib](https://matplotlib.org/)
- [PyInstaller](https://www.pyinstaller.org/)

## 📥 Instalação

Siga os passos abaixo para instalar e executar o projeto localmente:

### 1. Clone o repositório

```bash
git clone https://github.com/GustavoRibeiroOliveira/C213-L1.git
cd C213-L1
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
source venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute a aplicação

```bash
python main.py
```

## 📦 Build com PyInstaller

Para empacotar a aplicação como um executável standalone:

```bash
pyinstaller main.spec
```

O executável será gerado na pasta `dist/`.
Após ser gerado, basta mover o executável para a area de trabalho e rodar.


> Feito por [Gustavo Ribeiro de Oliveira](https://github.com/GustavoRibeiroOliveira)
