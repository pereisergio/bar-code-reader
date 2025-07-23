# bar_code_reader

Bem-vindo ao **bar_code_reader**! Este aplicativo permite ler e decodificar códigos de barras de boletos bancários de forma simples e rápida.

---

## 📦 Instalação

Siga os passos abaixo para instalar o programa no Windows usando [uv](https://github.com/astral-sh/uv):

1. **Instale o gerenciador uv** (caso ainda não tenha):
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
2. **Sincronize e instale as dependências do projeto:**
   ```powershell
   uv sync
   ```

---

## ▶️ Como Usar

1. Execute o programa principal:
   ```powershell
   uv run src/bar_code_reader/main.py
   ```
2. Siga as instruções na tela para carregar ou escanear o código de barras.

---

## 🛠️ Gerar Executável (Opcional)

Se quiser criar um arquivo executável (.exe) para facilitar o uso:

1. Instale o PyInstaller:
   ```powershell
   uv add pyinstaller
   ```
2. Gere o executável com o comando abaixo (execute na raiz do projeto):
   ```powershell
   uv run pyinstaller `
      --name="Code Bar Reader" `
      --onefile `
      --noconsole `
      --clean `
      --icon="..\files\barcode-scan.png" `
      --add-data="..\src;src" `
      --add-data="..\files;files" `
      --workpath "output\build" `
      --distpath "output\dist" `
      --specpath "output\" `
      --collect-binaries pyzbar `
      --log-level=WARN `
      src\bar_code_reader\main.py
   ```
   O executável será criado na pasta `./dist`.

---

## ❓ Dúvidas Frequentes

- **Não tenho Python instalado!**
  - Baixe em: https://www.python.org/downloads/
- **Erro ao ativar o ambiente virtual?**
  - Certifique-se de estar usando o PowerShell ou Prompt de Comando na pasta correta.
- **Problemas ao rodar o executável?**
  - Verifique se todos os arquivos necessários estão na pasta `files`.

---

## 📄 Documentação

- Exemplos de boletos e padrões de código de barras estão na pasta `docs/`.

---

## 🤝 Contribuição

Sugestões e melhorias são bem-vindas! Abra uma issue ou envie um pull request.