# Calculadora Financeira Educacional Interativa 📊💡

## Desmistifique as Finanças, Um Cálculo de Cada Vez!

Já se sentiu perdido(a) com as complexidades das calculadoras financeiras? Deseja dominar conceitos como o Valor do Dinheiro no Tempo, NPV, IRR, Amortizações e muito mais, mas os manuais parecem escritos noutra língua?

Esta aplicação web interativa foi criada a pensar em si! Quer seja estudante a preparar-se para exames, um profissional a necessitar de refrescar conhecimentos, ou simplesmente alguém curioso sobre o mundo das finanças, esta ferramenta é o seu ponto de partida ideal.

O nosso objetivo não é apenas dar-lhe o resultado final, mas sim **ensinar *como* chegar lá**, explicando a lógica e os conceitos por detrás de cada cálculo, de forma semelhante à funcionalidade encontrada em muitas calculadoras financeiras avançadas.

**Aprenda fazendo, com explicações claras e cálculos interativos!**

---

## ⚠️ Exclusão de Responsabilidade Importante ⚠️

**Esta aplicação é fornecida estritamente para fins educacionais e de demonstração.**

Embora tenham sido envidados esforços para assegurar a precisão dos cálculos e das explicações apresentadas, **não é oferecida qualquer garantia**, expressa ou implícita, quanto à exatidão, completude, fiabilidade ou adequação dos resultados para qualquer propósito específico.

**É possível que existam erros, bugs, imprecisões nas fórmulas implementadas ou diferenças significativas** em relação aos algoritmos, convenções de arredondamento e funcionalidades específicas de calculadoras financeiras comerciais ou software profissional. Os cálculos complexos, como o Yield de obrigações, são aproximações que podem ter limitações.

**Esta ferramenta NÃO constitui aconselhamento financeiro, de investimento, legal, contabilístico ou de qualquer outra natureza profissional.** As decisões financeiras comportam riscos e devem basear-se numa análise cuidada e, idealmente, na consulta com profissionais qualificados.

O utilizador assume **total responsabilidade** pela verificação e utilização da informação e dos cálculos fornecidos por esta aplicação. **Em nenhuma circunstância será o autor responsável** por quaisquer perdas, danos (diretos, indiretos, consequenciais ou outros) ou decisões tomadas com base na utilização desta ferramenta.

**Utilize por sua conta e risco.** Verifique sempre os resultados com fontes fidedignas antes de os aplicar em situações reais.

---

## Funcionalidades em Destaque ✨

Explore e pratique um vasto leque de conceitos financeiros essenciais:

* **Valor do Dinheiro no Tempo (TVM):** Calcule qualquer variável (N, I/Y, PV, PMT, FV) para cenários de empréstimos, poupanças, anuidades, etc.
* **Tabelas de Amortização:** Visualize o detalhe de cada pagamento, separando juros e capital, e acompanhe a evolução do saldo devedor com gráficos.
* **Análise de Fluxos de Caixa:** Avalie investimentos com fluxos de caixa desiguais usando o Valor Atual Líquido (NPV) e a Taxa Interna de Rentabilidade (IRR).
* **Conversão de Taxas de Juro:** Compreenda e converta facilmente entre taxas nominais (NOM) e efetivas (EFF).
* **Margem de Lucro:** Calcule rapidamente custos, preços de venda ou margens percentuais.
* **Ponto de Equilíbrio (Breakeven):** Analise a relação entre custos fixos, variáveis, preço e quantidade para determinar a rentabilidade.
* **Depreciação de Ativos:** Calcule a depreciação anual, valor contabilístico e valor depreciável restante usando métodos comuns (Linha Reta, Soma dos Dígitos dos Anos, Saldo Decrescente).
* **Cálculos com Datas:** Determine o número de dias entre duas datas (métodos Actual ou 360) ou encontre uma data futura/passada.
* **Análise de Obrigações (Bonds):** Calcule o Preço (PRI), os Juros Corridos (AI) e a Rendibilidade (YLD) até à maturidade ou call (*Nota: O cálculo de YLD usa métodos numéricos iterativos*).
* **Análise Estatística:** Realize análises descritivas e de regressão (Linear, Logarítmica, Exponencial, Potência) para dados de uma ou duas variáveis.

---

## Objetivo Educacional 🎯

Mais do que uma simples ferramenta de cálculo, esta aplicação tem uma forte componente pedagógica:

* **Explicações Detalhadas:** Cada módulo inclui uma secção "Explicação" que desmistifica os conceitos financeiros, define as variáveis e explica como interpretar os resultados.
* **Interface Interativa:** Introduza os seus próprios valores e veja como os resultados se alteram, facilitando a aprendizagem por experimentação.
* **Foco no Processo:** O objetivo é que compreenda *como* as funções financeiras operam, construindo uma base sólida para aplicar estes conhecimentos.

---

## Tecnologias Utilizadas 💻

Esta aplicação foi desenvolvida em Python, utilizando as seguintes bibliotecas principais:

* **Streamlit:** Para criar a interface web interativa de forma rápida e elegante.
* **Pandas:** Para manipulação e apresentação de dados (tabelas).
* **NumPy & NumPy Financial:** Para cálculos numéricos e financeiros eficientes.
* **SciPy:** Para cálculos científicos, incluindo os *solvers* numéricos usados na análise de obrigações (Yield) e funções estatísticas avançadas.
* **Matplotlib:** Para a geração dos gráficos de amortização.

---

## Como Executar Localmente 🚀

É fácil experimentar a aplicação no seu próprio computador:

1.  **Clonar o Repositório:**
    ```bash
    git clone [https://github.com/SEU_UTILIZADOR/NOME_DO_REPOSITORIO.git](https://github.com/SEU_UTILIZADOR/NOME_DO_REPOSITORIO.git)
    cd NOME_DO_REPOSITORIO
    ```
    *(Substitua `SEU_UTILIZADOR/NOME_DO_REPOSITORIO` pelo URL real)*

2.  **Criar um Ambiente Virtual (Recomendado):**
    ```bash
    python -m venv .venv
    # Windows
    .\.venv\Scripts\activate
    # MacOS/Linux
    source .venv/bin/activate
    ```

3.  **Instalar as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Executar a Aplicação Streamlit:**
    ```bash
    streamlit run nome_do_seu_script.py
    ```
    *(Substitua `nome_do_seu_script.py` pelo nome do seu ficheiro Python principal, ex: `app.py`)*

5.  A aplicação deverá abrir automaticamente no seu navegador web!

---

## Limitações e Avisos ⚠️

* **Simulação vs. Realidade:** Esta aplicação é uma ferramenta educacional que simula funcionalidades comuns. Devido à complexidade inerente a certas convenções financeiras (contagem de dias, feriados, etc.) e algoritmos específicos de calculadoras físicas, os resultados podem apresentar ligeiras diferenças em casos mais complexos, especialmente na análise de obrigações.
* **Cálculo de Yield (Obrigações):** A funcionalidade de cálculo de YLD utiliza *solvers* numéricos padrão (como `scipy.optimize.newton`). Embora robustos, estes métodos podem ter limitações de convergência em certos cenários ou requerer ajustes nas estimativas iniciais.

---

## Contribuições

Sinta-se à vontade para fazer *fork* do projeto, sugerir melhorias, reportar bugs ou submeter *pull requests*!

---

## Licença 📜

Copyright © 2025 Luís Simões da Cunha.

<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/"><img alt="Licença Creative Commons" style="border-width:0" src="https://i.creativecommons.org/l/by-nc/4.0/88x31.png" /></a><br />Esta obra está licenciada sob a Licença <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/">Creative Commons Atribuição-NãoComercial 4.0 Internacional</a>.

Isto significa que é livre de:

* **Partilhar** — copiar e redistribuir o material em qualquer suporte ou formato
* **Adaptar** — remixar, transformar e criar a partir do material

Sob as seguintes condições:

* **Atribuição** — Você deve dar o crédito apropriado (neste caso, a Luís Simões da Cunha), fornecer um link para a licença e indicar se foram feitas alterações. Você pode fazê-lo de qualquer maneira razoável, mas não de uma forma que sugira que o licenciante o apoia a si ou ao seu uso.
* **NãoComercial** — Você não pode usar o material para fins comerciais.

Para ver uma cópia completa desta licença, visite:
[http://creativecommons.org/licenses/by-nc/4.0/](http://creativecommons.org/licenses/by-nc/4.0/)

---