# Leitor de Código de Barras e QR Code com Python

Este projeto implementa um **Leitor de Código de Barras e QR Code** utilizando a linguagem **Python**, combinando a interface gráfica desenvolvida com `PySide6` e a leitura/decodificação dos códigos com a biblioteca `pyzbar`.

## Funcionalidades:
- **Interface Gráfica Intuitiva**: Desenvolvida com `PySide6`, a interface permite carregar imagens ou realizar leitura em tempo real com a câmera.
- **Leitura de Diversos Tipos de Códigos**:
  1. **Código de Barras de Arrecadação**: Reconhece e extrai informações de contas de serviços e tributos.
  2. **Boletos Bancários**: Lê códigos de barras padrão para boletos bancários, facilitando a extração da linha digitável.
  3. **QR Code e PIX**: Decodifica QR Codes comuns e `chaves PIX`, como `CPF/CNPJ`, telefone, e-mail ou chave aleatória.
- **Suporte a Imagens e Câmera**: Aceita imagens já existentes ou realiza captura em tempo real utilizando a câmera.

## Bibliotecas Utilizadas:
1. **PySide6**: Para criação da interface gráfica do usuário (GUI).
2. **pyzbar**: Para leitura e decodificação de códigos de barras e QR Codes.

## Aplicações:
- **Leitura de Boletos e Contas**: Facilita a extração automática de códigos de barras de boletos bancários e arrecadações.
- **Pagamentos PIX**: Decodifica chaves PIX e QR Codes de pagamento para agilidade em transações.
- **Inventário e Controle**: Leitura rápida de códigos de barras de produtos ou serviços.
- **Eventos e Validação**: Utilização de QR Codes para acesso e controle.

## Instalação 

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Criando Executável

Para criar um arquivo executável para a aplicação, você precisa instalar a biblioteca `pyinstaller`. Além disso, inclua a biblioteca específica `pyzbar` durante a compilação usando o seguinte comando:

```
pip install pyinstaller

pyinstaller --name="Code Bar Reader" \
            --onefile \
            --icon="../src/files/barcode-scan.png" \
            --noconsole \
            --clean \
            --add-data="../src/files/:files" \
            --log-level=WARN \
            --distpath="output/dist" \
            --workpath="output/build" \
            --specpath="output/" \
            --collect-binaries pyzbar \
            main.py
```