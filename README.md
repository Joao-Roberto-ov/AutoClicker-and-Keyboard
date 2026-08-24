# 🖱️ Auto Clicker & Keyboard Macro

[![Versão](https://img.shields.io/github/v/release/Joao-Roberto-ov/AutoClicker-and-Keyboard?color=blue&label=vers%C3%A3o)](https://github.com/Joao-Roberto-ov/AutoClicker-and-Keyboard/releases)
[![Python](https://img.shields.io/badge/python-3.8%2B-green.svg)](https://www.python.org/)
[![Releases](https://img.shields.io/badge/📦_Baixar-Releases-ff69b4?style=for-the-badge&logo=github)](https://github.com/Joao-Roberto-ov/AutoClicker-and-Keyboard/releases)

Um programa robusto e automatizador em Python com interface gráfica moderna (PyQt6) criado para **gravar, gerenciar e reproduzir macros de mouse e teclado**. Ele automatiza tarefas repetitivas com precisão matemática, suportando repetições personalizadas e intervalos configuráveis.

---

## 🚀 Download e Atualizações (Releases)

Para baixar a versão compilada (pronta para usar, sem precisar instalar o Python), acesse nossa página de Releases:

👉 **[CLIQUE AQUI PARA BAIXAR AS RELEASES DO PROGRAMA](https://github.com/Joao-Roberto-ov/AutoClicker-and-Keyboard/releases)** 👈

> 💡 **Nota:** O programa possui um **Auto-Updater** inteligente! Sempre que você abri-lo, ele verificará essa mesma página do GitHub em busca de novas versões. Se houver uma atualização, você será notificado para baixar a nova versão instantaneamente.

---

## ✨ Recursos

- **Gravação de Alta Precisão:** Registra movimentos do mouse, cliques (direito, esquerdo, meio) e toques no teclado.
- **Interface Gráfica Intuitiva:** Gerencie, renomeie, exclua e visualize os comandos dos seus macros através de uma UI feita em PyQt6.
- **Teclas de Atalho Globais (Hotkeys):**
  - `F8`: Iniciar Gravação
  - `F9`: Parar (Gravação ou Reprodução)
  - `F10`: Executar Macro
- **Automação de Compilação & Instalação:** Se executado via script `.py` sem as bibliotecas, ele instala as dependências automaticamente e oferece a opção de gerar o executável (`.exe`) via PyInstaller.
- **Opções de Repetição:** Execute macros uma quantidade específica de vezes ou em **loop infinito**, definindo o intervalo de tempo entre as repetições.
- **Importação/Exportação Segura:** Compartilhe seus macros! Eles são salvos em formato `.json` padronizado.

---

## 🛠️ Como Usar (Para Desenvolvedores / Código Fonte)

Caso queira rodar diretamente do código fonte ou compilar você mesmo:

1. Clone o repositório

2. Execute o script principal (`autoclicker.py`):

3. **Bootstrap Mágico:** O script verificará se você possui `PyQt6`, `pynput`, `requests` e `pyinstaller`. Se não tiver, **ele vai perguntar se deseja instalar automaticamente**.
4. **Auto-Compilador:** Após as dependências, o programa perguntará se você quer gerar o arquivo `.exe`. Se disser que sim, ele fará o build e salvará na pasta `dist/`.

---

## 🎮 Guia de Uso do Programa

1. **Selecione a Pasta:** Ao abrir o programa, clique em "📁 Selecionar Pasta de Macros" para definir onde seus macros `.json` serão salvos.
2. **Grave um Macro:** Pressione `F8` ou clique no botão de gravar e espere 2 segundos para o programa começar a gravar (notificação em laranja na parte central inferior). Faça as ações desejadas.
3. **Pare a Gravação:** Pressione `F9`. Escolha um nome para o seu macro na janela que aparecer.
4. **Reproduza:** Selecione o macro na lista à esquerda, configure a quantidade de repetições e clique em "▶️ Executar" (ou aperte `F10`).
5. **Acompanhamento ao Vivo:** A tela de log exibe cada tecla pressionada e clique feito durante a gravação!

---

## 📝 Estrutura dos Macros (JSON)

Os macros são gerados e lidos no formato JSON com suporte à contagem de tempo exata (delay) entre cada movimento, garantindo que a execução ocorra no mesmo ritmo da gravação original.

## 📄 Licença

Sinta-se à vontade para clonar, modificar e utilizar este projeto para facilitar suas automações do dia a dia.
