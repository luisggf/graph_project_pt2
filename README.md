**README da Ferramenta de Análise de Gráficos**

Este README fornece uma visão geral da Ferramenta de Análise de Gráficos, suas funcionalidades, instalações necessárias e instruções de uso.

## Visão Geral

A Ferramenta de Análise de Gráficos é um aplicativo Python com interface gráfica construída usando a biblioteca `tkinter`. Ela permite aos usuários realizar análises em dados de gráficos, visualizar medidas de centralidade, gerar mapas de calor e plotar gráficos ponderados com base em parâmetros definidos pelo usuário.

## Funcionalidades

1. **Análise de Dados**: A ferramenta lê dados de arquivos CSV contendo informações sobre relacionamentos entre entidades (por exemplo, políticos) ao longo de vários anos.

2. **Visualização de Gráficos**: Os usuários podem optar por visualizar medidas de centralidade, gerar mapas de calor e plotar gráficos ponderados com base em parâmetros selecionados.

3. **Filtragem de Gráficos**: Os usuários podem filtrar dados com base no ano, partidos e valores de limite para personalizar sua análise.

4. **Seleção de Partidos**: Os usuários podem selecionar e alternar entre partidos, com os partidos selecionados sendo destacados e marcados.

## Instalações Necessárias

1. **Python**: Certifique-se de ter o Python instalado em seu sistema. Você pode baixá-lo no [site oficial do Python](https://www.python.org/downloads/).

2. **Ambiente Virtual (Opcional)**: É altamente recomendado criar um ambiente virtual para isolar as dependências deste projeto. No terminal, execute:
   ```
   python -m venv nome_do_ambiente
   ```

3. **Bibliotecas Necessárias**: Certifique-se de ter as seguintes bibliotecas instaladas em seu ambiente virtual:
   ```
   pip install pandas networkx matplotlib
   ```

4. **tkinter**: Geralmente, a biblioteca `tkinter` está incluída nas instalações do Python. Se não estiver, talvez seja necessário instalá-la manualmente.

5. **Pacote de Dicas de Ferramenta**: A ferramenta usa um pacote de dicas de ferramenta personalizado para fornecer informações de ajuda. Certifique-se de ter esse pacote instalado.

## Instruções de Uso

1. Clone ou faça o download deste repositório para sua máquina local.

2. Abra um terminal e navegue até o diretório do projeto.

3. Ative seu ambiente virtual (caso tenha criado um):
   - No Windows:
     ```
     nome_do_ambiente\Scripts\activate
     ```
   - No macOS e Linux:
     ```
     source nome_do_ambiente/bin/activate
     ```

4. Execute o seguinte comando para instalar as dependências necessárias:
   ```
   pip install -r requirements.txt
   ```

5. Execute o aplicativo executando o seguinte comando:
   ```
   python main.py
   ```

6. A interface gráfica da Ferramenta de Análise de Gráficos aparecerá. Siga as instruções na interface para realizar suas análises.

7. Para sair do ambiente virtual após o uso, no terminal, execute:
   ```
   deactivate
   ```

## Personalização

Você pode personalizar e estender ainda mais a Ferramenta de Análise de Gráficos modificando o código nos arquivos Python fornecidos. Sinta-se à vontade para aprimorar suas funcionalidades, melhorar a interface do usuário ou integrar funcionalidades adicionais conforme necessário.

## Contribuições

Contribuições são bem-vindas! Se encontrar algum erro ou desejar adicionar novos recursos, sinta-se à vontade para abrir um problema ou enviar um pull request no repositório GitHub do projeto.

