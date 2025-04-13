import streamlit as st
import numpy as np
import numpy_financial as npf
import pandas as pd
import matplotlib.pyplot as plt

import scipy as sp # Adicionado para garantir que está importado para Estatística

import datetime # Adicionado para garantir que está importado para Datas/Obrigações
from scipy import stats # Adicionado para garantir que está importado para Estatística

# --- Configuração da Página ---
st.set_page_config(layout="wide", page_title="Calculadora Financeira Educacional")


st.title("Calculadora Financeira Educacional")
st.caption("Uma ferramenta para aprender e usar conceitos financeiros.")

# --- Funções Auxiliares ---

def plot_amortization(schedule_df):
    """Gera um gráfico do saldo devedor ao longo do tempo."""
    fig, ax = plt.subplots()
    ax.plot(schedule_df['Período'], schedule_df['Saldo Final'], marker='o', linestyle='-')
    ax.set_xlabel("Período")
    ax.set_ylabel("Saldo Devedor (€)")
    ax.set_title("Evolução do Saldo Devedor")
    ax.grid(True)
    # Formatar o eixo Y para moeda
    from matplotlib.ticker import FuncFormatter
    def currency_formatter(x, pos):
        return f'€{x:,.2f}'
    ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))
    st.pyplot(fig)

# --- Função calculate_breakeven (CORRIGIDA da resposta anterior) ---
def calculate_breakeven(known_vars):
    target = known_vars['Target']
    try:
        p = known_vars['P']
        vc = known_vars['VC']
        fc = known_vars['FC']
        pft = known_vars['PFT']
        q = known_vars['Q']

        required_for = {
            'Q': ['FC', 'PFT', 'P', 'VC'],
            'PFT': ['FC', 'Q', 'P', 'VC'],
            'FC': ['PFT', 'Q', 'P', 'VC'],
            'P': ['FC', 'PFT', 'Q', 'VC'],
            'VC': ['FC', 'PFT', 'Q', 'P']
        }

        for var_name in required_for[target]:
            if known_vars[var_name] is None:
                return f"Erro: Input '{var_name}' não pode ser None para calcular '{target}'."
            if not isinstance(known_vars[var_name], (int, float)):
                 return f"Erro: Input '{var_name}' deve ser numérico."

        if target == 'Q':
            p = known_vars['P']
            vc = known_vars['VC']
            fc = known_vars['FC']
            pft = known_vars['PFT']
            margin_contribution = p - vc
            if margin_contribution <= 0: return "Erro: Preço (P) deve ser maior que Custo Variável (VC)."
            result = (fc + pft) / margin_contribution
        elif target == 'PFT':
            p = known_vars['P']
            vc = known_vars['VC']
            fc = known_vars['FC']
            q = known_vars['Q']
            margin_contribution = p - vc
            result = (margin_contribution * q) - fc
        elif target == 'FC':
            p = known_vars['P']
            vc = known_vars['VC']
            pft = known_vars['PFT']
            q = known_vars['Q']
            margin_contribution = p - vc
            result = (margin_contribution * q) - pft
        elif target == 'P':
            fc = known_vars['FC']
            vc = known_vars['VC']
            pft = known_vars['PFT']
            q = known_vars['Q']
            if q <= 0: return "Erro: Quantidade (Q) deve ser > 0."
            result = (fc + (vc * q) + pft) / q
        elif target == 'VC':
            p = known_vars['P']
            fc = known_vars['FC']
            pft = known_vars['PFT']
            q = known_vars['Q']
            if q <= 0: return "Erro: Quantidade (Q) deve ser > 0."
            result = ((p * q) - fc - pft) / q
        else:
            return "Erro: Variável alvo ('Target') desconhecida."
        return result
    except ZeroDivisionError:
         return f"Erro: Divisão por zero ao calcular {target} (verifique se Q ou (P-VC) são zero onde aplicável)."
    except TypeError as te:
         return f"Erro de Tipo: Verifique se todos os inputs necessários são números válidos. Detalhe: {te}"
    except Exception as e:
         return f"Erro inesperado ao calcular {target}: {e}"

# --- Seleção da Funcionalidade ---
main_tabs = st.tabs([
    "Introdução", # Índice 0
    "Valor do Dinheiro no Tempo (TVM) & Amortização", # Índice 1
    "Fluxo de Caixa (NPV & IRR)", # Índice 2
    "Conversão de Taxas de Juro", # Índice 3
    "Margem de Lucro", # Índice 4
    "Ponto de Equilíbrio (Breakeven)", # Índice 5
    "Depreciação", # Índice 6
    "Datas", # Índice 7
    "Obrigações (Bonds)", # Índice 8
    "Estatística" # Índice 9
])

# --- Aba: Introdução ---
with main_tabs[0]:
    st.header("Bem-vindo!")

    # --- AVISO IMPORTANTE INSERIDO AQUI ---
    st.warning("""
    ### ⚠️ Aviso Importante

    **Fins Educacionais:**
    Esta aplicação foi desenvolvida com propósitos **puramente educacionais** para auxiliar na compreensão de conceitos financeiros e na simulação de funcionalidades de calculadoras financeiras.

    **Sem Garantias:**
    O autor **não oferece qualquer garantia** quanto à exatidão, fiabilidade ou adequação dos cálculos e resultados apresentados. Podem existir erros, omissões, ou diferenças em relação a calculadoras financeiras standard ou software profissional.

    **Não é Aconselhamento Financeiro:**
    A informação e as ferramentas aqui disponibilizadas **não constituem aconselhamento financeiro, de investimento, legal ou fiscal**. Qualquer decisão baseada nos resultados desta aplicação é da exclusiva responsabilidade do utilizador.

    **Verificação Independente:**
    Recomenda-se vivamente a **verificação independente** de todos os cálculos e resultados através de fontes fidedignas ou consultores profissionais antes de tomar qualquer decisão financeira.
    """)
    # --- FIM DO AVISO ---

    # Resto do conteúdo original da Introdução
    st.markdown("""
    Esta aplicação foi criada para ajudar a compreender e utilizar os conceitos financeiros fundamentais,
    muitas vezes calculados com calculadoras como a Texas Instruments BA II Plus.

    **Navegação:**
    * Use as abas acima para selecionar a funcionalidade financeira que deseja explorar.
    * Dentro de cada funcionalidade, encontrará geralmente duas sub-abas:
        * **Explicação:** Descreve os conceitos, as variáveis e como interpretar os resultados.
        * **Calculadora:** Permite inserir os seus próprios valores e realizar os cálculos.

    **Convenção de Sinais (Importante!):**
    Assim como na BA II Plus, usamos uma convenção de sinais para fluxos de caixa:
    * **Entradas de Caixa (Dinheiro Recebido):** Valores positivos (+). [source: 203, 225]
    * **Saídas de Caixa (Dinheiro Pago/Investido):** Valores negativos (-). [source: 203, 226, 342]
    * Por exemplo, ao contrair um empréstimo, o Valor Presente (PV) é positivo (recebe o dinheiro), e as Prestações (PMT) são negativas (paga o dinheiro). Ao investir, o PV é negativo (investe) e o FV pode ser positivo (resgata).

    **Comece por explorar as abas!**
    """)
    


# --- Aba: TVM & Amortização ---
with main_tabs[1]:
    st.header("Valor do Dinheiro no Tempo (TVM) e Amortização")

    tvm_tabs = st.tabs(["Explicação", "Calculadora TVM", "Amortização"])

    with tvm_tabs[0]:
        st.subheader("O que é o Valor do Dinheiro no Tempo?")
        st.markdown("""
        O conceito fundamental de TVM é que **um euro hoje vale mais do que um euro amanhã**. Isto deve-se ao potencial de ganho (juros) desse euro ao longo do tempo.
        As funções TVM ajudam a analisar fluxos de caixa *regulares e iguais* ao longo do tempo, como empréstimos, hipotecas, anuidades, poupanças, etc.

        **Variáveis Principais:**
        * **N (Número de Períodos):** O número total de períodos de pagamento ou composição (ex: meses, anos).
        * **I/Y (Taxa de Juro Anual):** A taxa de juro nominal *anual*. A calculadora converte-a internamente para uma taxa por período com base em P/Y e C/Y.
        * **PV (Valor Presente):** O valor do dinheiro no início do período (tempo = 0). Ex: o montante de um empréstimo.
        * **PMT (Prestação/Pagamento):** O montante de cada pagamento periódico igual.
        * **FV (Valor Futuro):** O valor do dinheiro no final do período N. Ex: o saldo final de uma poupança, ou o saldo remanescente de um empréstimo (geralmente 0).

        **Configurações Adicionais:**
        * **P/Y (Pagamentos por Ano):** Quantas prestações são feitas por ano (ex: 12 para mensal, 4 para trimestral).
        * **C/Y (Períodos de Composição por Ano):** Quantas vezes os juros são calculados (capitalizados) por ano. Frequentemente igual a P/Y.
        * **END/BGN (Fim/Início do Período):**
            * **END (Ordinary Annuity):** Os pagamentos ocorrem no *fim* de cada período (ex: maioria dos empréstimos).
            * **BGN (Annuity Due):** Os pagamentos ocorrem no *início* de cada período (ex: maioria dos leases/alugueres, algumas poupanças).

        **Convenção de Sinais:** Lembre-se de usar valores negativos para saídas de caixa (pagamentos feitos, investimentos iniciais) e positivos para entradas de caixa (empréstimos recebidos, valor final resgatado).

        **Amortização:** Após calcular uma variável TVM (geralmente PMT), a função de amortização permite ver como cada pagamento é dividido entre juros e capital (principal), e qual o saldo remanescente após um certo número de pagamentos.
        """)

    with tvm_tabs[1]:
        st.subheader("Calculadora TVM")

        # Layout em colunas
        col1, col2, col3 = st.columns(3)

        with col1:
            n = st.number_input("N (Número Total de Períodos)", min_value=0, value=360, step=1, help="Ex: 30 anos * 12 meses = 360")
            i_y = st.number_input("I/Y (Taxa de Juro Anual %)", min_value=0.0, value=5.5, step=0.1, format="%.4f", help="Insira a taxa anual nominal. Ex: 5.5 para 5.5%")
            pv = st.number_input("PV (Valor Presente)", value=75000.0, step=100.0, format="%.2f", help="Montante inicial. Positivo se recebe (empréstimo), negativo se paga (investimento).")

        with col2:
            pmt = st.number_input("PMT (Prestação Periódica)", value=-425.84, step=10.0, format="%.2f", help="Pagamento por período. Negativo se paga, positivo se recebe.")
            fv = st.number_input("FV (Valor Futuro)", value=0.0, step=100.0, format="%.2f", help="Valor no final dos N períodos. Geralmente 0 para empréstimos totalmente pagos.")
            p_y = st.number_input("P/Y (Pagamentos por Ano)", min_value=1, value=12, step=1, help="Ex: 12 para mensal, 1 para anual")

        with col3:
            # C/Y por defeito igual a P/Y, mas permite alteração
            c_y_default = p_y
            c_y = st.number_input("C/Y (Composições por Ano)", min_value=1, value=c_y_default, step=1, help="Normalmente igual a P/Y.")
            pmt_mode = st.radio("Modo de Pagamento (BGN/END)", ('END', 'BGN'), index=0, help="END=Fim do período, BGN=Início do período")
            when = 'begin' if pmt_mode == 'BGN' else 'end'

        st.divider()

        # Botões de Cálculo
        st.write("**Calcular Variável Desconhecida:**")
        calc_col1, calc_col2, calc_col3, calc_col4, calc_col5 = st.columns(5)

        # Estado para armazenar o último resultado calculado
        if 'last_tvm_result' not in st.session_state:
            st.session_state.last_tvm_result = None

        if calc_col1.button("Calcular N"):
            try:
                rate_per_period = (i_y / 100) / c_y # Ajuste para taxa periódica consistente com npf
                rate_for_nper = (i_y / 100) / p_y # Usar p_y para consistência com pagamentos
                result = npf.nper(rate_for_nper, pmt, pv, fv, when)
                st.success(f"N = {result:.4f}")
                st.session_state.last_tvm_result = {'N': result, 'I/Y': i_y, 'PV': pv, 'PMT': pmt, 'FV': fv, 'P/Y': p_y, 'C/Y': c_y, 'Mode': pmt_mode}
            except Exception as e:
                st.error(f"Erro ao calcular N: {e}. Verifique os inputs e a convenção de sinais.")
                st.warning("Causas comuns: Taxa de juro (I/Y) inválida, ou PV, PMT, FV com sinais incorretos (ex: todos positivos/negativos).")

        if calc_col2.button("Calcular I/Y"):
            try:
                rate_per_period = npf.rate(n, pmt, pv, fv, when)
                result_annual = rate_per_period * p_y * 100
                st.success(f"I/Y Anual = {result_annual:.4f} %")
                st.session_state.last_tvm_result = {'N': n, 'I/Y': result_annual, 'PV': pv, 'PMT': pmt, 'FV': fv, 'P/Y': p_y, 'C/Y': c_y, 'Mode': pmt_mode}
            except Exception as e:
                st.error(f"Erro ao calcular I/Y: {e}. Verifique os inputs e a convenção de sinais.")
                st.warning("Causas comuns: N inválido, ou PV, PMT, FV com sinais incorretos.")

        if calc_col3.button("Calcular PV"):
            try:
                rate_per_period = (i_y / 100) / p_y
                result = npf.pv(rate_per_period, n, pmt, fv, when)
                st.success(f"PV = {result:.2f}")
                st.session_state.last_tvm_result = {'N': n, 'I/Y': i_y, 'PV': result, 'PMT': pmt, 'FV': fv, 'P/Y': p_y, 'C/Y': c_y, 'Mode': pmt_mode}
            except Exception as e:
                st.error(f"Erro ao calcular PV: {e}. Verifique os inputs.")

        if calc_col4.button("Calcular PMT"):
            try:
                rate_per_period = (i_y / 100) / p_y
                result = npf.pmt(rate_per_period, n, pv, fv, when)
                st.success(f"PMT = {result:.2f}")
                st.session_state.last_tvm_result = {'N': n, 'I/Y': i_y, 'PV': pv, 'PMT': result, 'FV': fv, 'P/Y': p_y, 'C/Y': c_y, 'Mode': pmt_mode}
            except Exception as e:
                st.error(f"Erro ao calcular PMT: {e}. Verifique os inputs.")

        if calc_col5.button("Calcular FV"):
            try:
                rate_per_period = (i_y / 100) / p_y
                result = npf.fv(rate_per_period, n, pmt, pv, when)
                st.success(f"FV = {result:.2f}")
                st.session_state.last_tvm_result = {'N': n, 'I/Y': i_y, 'PV': pv, 'PMT': pmt, 'FV': result, 'P/Y': p_y, 'C/Y': c_y, 'Mode': pmt_mode}
            except Exception as e:
                st.error(f"Erro ao calcular FV: {e}. Verifique os inputs.")

        if st.button("Limpar Campos TVM"):
            st.info("Funcionalidade de reset completo dos campos ainda em desenvolvimento. Por favor, reintroduza os valores ou reinicie a página.")
            st.session_state.last_tvm_result = None


    with tvm_tabs[2]:
        st.subheader("Gerar Tabela de Amortização")
        st.markdown("""
        Use os resultados do cálculo TVM (especialmente PV, I/Y, PMT, N e P/Y) para gerar uma tabela de amortização.
        Insira o período inicial (P1) e final (P2) para ver o detalhe nesse intervalo.
        * **BAL:** Saldo remanescente após o pagamento do período P2.
        * **PRN:** Principal total pago entre P1 e P2 (inclusive).
        * **INT:** Juros totais pagos entre P1 e P2 (inclusive).
        """)

        if 'last_tvm_result' in st.session_state and st.session_state.last_tvm_result:
            st.info("Usando os últimos resultados TVM calculados:")
            # Limitar json para evitar excesso de output se houver muitos dados
            display_result = {k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in st.session_state.last_tvm_result.items()}
            st.json(str(display_result)) # Mostrar como string para evitar problemas de formatação

            tvm_data = st.session_state.last_tvm_result
            try:
                 pv_amort = float(tvm_data.get('PV', 0))
                 iy_amort = float(tvm_data.get('I/Y', 0))
                 pmt_amort = float(tvm_data.get('PMT', 0))
                 n_amort = int(tvm_data.get('N', 0))
                 py_amort = int(tvm_data.get('P/Y', 1))
                 # cy_amort = int(tvm_data.get('C/Y', 1)) # Pode ser necessário se C/Y != P/Y
                 # mode_amort = tvm_data.get('Mode', 'END') # Pode ser necessário para lógica BGN
                 valid_amort_data = True
            except (ValueError, TypeError):
                 st.warning("Dados TVM inválidos ou incompletos para gerar amortização.")
                 valid_amort_data = False


            if valid_amort_data and not all([n_amort > 0, py_amort > 0]):
                 st.warning("Dados TVM N ou P/Y inválidos para gerar amortização.")
                 valid_amort_data = False

            if valid_amort_data:
                rate_per_period_amort = (iy_amort / 100.0) / py_amort

                amort_col1, amort_col2 = st.columns(2)
                with amort_col1:
                    p1 = st.number_input("Período Inicial (P1)", min_value=1, max_value=n_amort, value=1, step=1, key="amort_p1")
                with amort_col2:
                    p2 = st.number_input("Período Final (P2)", min_value=p1, max_value=n_amort, value=min(12, n_amort), step=1, key="amort_p2")

                if st.button("Gerar Amortização"):
                    if p1 > p2:
                        st.error("P1 não pode ser maior que P2.")
                    else:
                        schedule = []
                        current_balance = pv_amort
                        total_principal_paid = 0.0
                        total_interest_paid = 0.0
                        balance_at_p2 = current_balance # Inicializar

                        # Gerar toda a tabela até P2 para obter o saldo correcto
                        for period in range(1, n_amort + 1):
                            if current_balance <= 0 and abs(pmt_amort)>0: # Parar se saldo já é zero (exceto se PMT for 0)
                                 if period <= p2: # Garantir que balance_at_p2 fica zero se acontecer antes
                                     balance_at_p2 = 0.0
                                 break

                            interest_payment = current_balance * rate_per_period_amort
                            principal_payment = pmt_amort - interest_payment

                            # Evitar que o principal pago exceda o saldo (caso de último pagamento)
                            if abs(principal_payment) > abs(current_balance):
                                principal_payment = -current_balance # Pagar exatamente o saldo
                                # Recalcular PMT para este último período? Não, assumimos PMT constante
                                interest_payment = pmt_amort - principal_payment # Juro é o que sobra
                                # Se pmt_amort for 0, isto não funciona bem, tratar separadamente

                            new_balance = current_balance + principal_payment

                            # Armazenar na tabela se estiver no intervalo P1-P2
                            if p1 <= period <= p2:
                                schedule.append({
                                    'Período': period,
                                    'Saldo Inicial': current_balance,
                                    'Pagamento (PMT)': abs(pmt_amort),
                                    'Juros Pagos': abs(interest_payment),
                                    'Principal Pago': abs(principal_payment),
                                    'Saldo Final': max(0, new_balance) # Mostrar zero se ficar ligeiramente negativo por arredondamento
                                })
                                total_principal_paid += abs(principal_payment)
                                total_interest_paid += abs(interest_payment)

                            # Atualizar saldo para próxima iteração
                            current_balance = new_balance

                            # Guardar o saldo no final do período P2
                            if period == p2:
                                balance_at_p2 = max(0, current_balance)

                            # Parar a iteração cedo se já passamos P2 e só queremos totais
                            if period >= p2 and period >= n_amort : break


                        if schedule:
                            st.subheader(f"Detalhes da Amortização (Períodos {p1} a {p2})")
                            schedule_df = pd.DataFrame(schedule)
                            st.dataframe(schedule_df.style.format({
                                'Saldo Inicial': '{:,.2f} €',
                                'Pagamento (PMT)': '{:,.2f} €',
                                'Juros Pagos': '{:,.2f} €',
                                'Principal Pago': '{:,.2f} €',
                                'Saldo Final': '{:,.2f} €',
                            }))

                            st.subheader("Sumário do Intervalo")
                            summary_col1, summary_col2, summary_col3 = st.columns(3)
                            summary_col1.metric("Saldo Final (após P2)", f"{balance_at_p2:,.2f} €")
                            summary_col2.metric("Total Principal Pago (P1-P2)", f"{total_principal_paid:,.2f} €")
                            summary_col3.metric("Total Juros Pagos (P1-P2)", f"{total_interest_paid:,.2f} €")

                            # Gráfico
                            st.subheader("Gráfico do Saldo Devedor")
                            full_schedule_plot = []
                            balance_plot = pv_amort
                            for period_plot in range(1, n_amort + 1):
                                if balance_plot <= 0 and abs(pmt_amort)>0:
                                    # Adicionar ponto zero final se ainda não estiver
                                    if not full_schedule_plot or full_schedule_plot[-1]['Saldo Final'] > 0:
                                         full_schedule_plot.append({'Período': period_plot, 'Saldo Final': 0.0})
                                    break
                                interest_plot = balance_plot * rate_per_period_amort
                                principal_plot = pmt_amort - interest_plot
                                if abs(principal_plot) > abs(balance_plot):
                                    principal_plot = -balance_plot
                                balance_plot += principal_plot
                                full_schedule_plot.append({'Período': period_plot, 'Saldo Final': max(0, balance_plot)})

                            plot_df = pd.DataFrame(full_schedule_plot)
                            if not plot_df.empty:
                                 plot_amortization(plot_df)
                            else:
                                 st.warning("Não foi possível gerar dados para o gráfico.")


                        else:
                            st.warning("Nenhum período encontrado no intervalo P1-P2 especificado.")
        else:
            st.warning("Calcule primeiro uma variável TVM para ativar a funcionalidade de Amortização.")


# --- Aba: Fluxo de Caixa (NPV & IRR) ---
with main_tabs[2]:
    st.header("Análise de Fluxo de Caixa (NPV & IRR)")

    cf_tabs = st.tabs(["Explicação", "Calculadora NPV/IRR"])

    with cf_tabs[0]:
        st.subheader("O que são NPV e IRR?")
        st.markdown("""
        Estas ferramentas são usadas para analisar projetos de investimento com fluxos de caixa **desiguais** ao longo do tempo.

        **Variáveis Principais:**
        * **CF0 (Fluxo de Caixa Inicial):** O investimento inicial no tempo 0. Geralmente um valor negativo (saída de caixa).
        * **Cnn (Fluxo de Caixa n):** O montante do fluxo de caixa no período 'nn' (C01, C02,...). Pode ser positivo (receita) ou negativo (custo).
        * **Fnn (Frequência do Fluxo n):** Quantas vezes consecutivas o fluxo Cnn ocorre. Permite agrupar fluxos iguais.
        * **I (Taxa de Desconto %):** A taxa de juro usada para descontar os fluxos de caixa futuros para o seu valor presente. Representa o custo de oportunidade do capital ou a taxa de retorno exigida.

        **Cálculos:**
        * **NPV (Net Present Value / Valor Atual Líquido):** É a soma de todos os fluxos de caixa (incluindo CF0) descontados para o presente, usando a taxa 'I'.
            * **Interpretação:**
                * NPV > 0: O projeto gera mais valor do que custa; potencialmente aceitável.
                * NPV < 0: O projeto destrói valor; potencialmente rejeitável.
                * NPV = 0: O projeto retorna exatamente a taxa de desconto exigida.
        * **IRR (Internal Rate of Return / Taxa Interna de Rentabilidade):** É a taxa de desconto que faz com que o NPV do projeto seja igual a zero.
            * **Interpretação:** Representa a taxa de rentabilidade intrínseca do projeto. Compara-se a IRR com a taxa de desconto (custo de capital):
                * IRR > Taxa de Desconto: Projeto potencialmente aceitável.
                * IRR < Taxa Desconto: Projeto potencialmente rejeitável.

        **Notas Importantes sobre IRR:**
        * A IRR assume que os fluxos de caixa intermédios são reinvestidos à própria IRR, o que pode não ser realista.
        * Pode não existir IRR ou existir múltiplas IRRs se os fluxos de caixa mudarem de sinal mais do que uma vez.
        * Pode ocorrer erro se não houver mudança de sinal (Error 5).
        """)

    with cf_tabs[1]:
        st.subheader("Calculadora NPV / IRR")

        # Input CF0
        cf0 = st.number_input("CF0 (Investimento Inicial)", value=-7000.0, format="%.2f", help="Normalmente negativo.", key="cf0_input")

        st.markdown("**Fluxos de Caixa Subsequentes (Cnn) e Frequências (Fnn):**")
        st.caption("Use Fnn > 1 para agrupar fluxos de caixa iguais consecutivos.")

        # Usar st.data_editor para entrada flexível
        if 'cf_data' not in st.session_state:
             st.session_state.cf_data = pd.DataFrame([
                {"Fluxo (Cnn)": 3000.0, "Frequência (Fnn)": 1},
                {"Fluxo (Cnn)": 5000.0, "Frequência (Fnn)": 4},
                {"Fluxo (Cnn)": 4000.0, "Frequência (Fnn)": 1},
             ])

        edited_df = st.data_editor(
            st.session_state.cf_data,
            num_rows="dynamic", # Permite adicionar/remover linhas
            column_config={
                "Fluxo (Cnn)": st.column_config.NumberColumn(format="%.2f", required=True),
                "Frequência (Fnn)": st.column_config.NumberColumn(min_value=1, step=1, default=1, required=True)
            },
            key="cf_editor_main"
        )
        # Atualizar o estado se o dataframe for editado
        st.session_state.cf_data = edited_df

        # Input Taxa de Desconto
        discount_rate = st.number_input("I (Taxa de Desconto % por Período)", value=20.0, format="%.4f", help="Taxa usada para descontar os fluxos. Deve corresponder à periodicidade dos fluxos.", key="discount_rate_input")

        st.divider()

        # Botões Calcular
        cf_calc_col1, cf_calc_col2 = st.columns(2)

        if cf_calc_col1.button("Calcular NPV", key="npv_button"):
            try:
                cash_flows = [cf0]
                valid_input = True
                # Usar o dataframe do session_state que foi atualizado
                current_cf_df = st.session_state.cf_data
                if current_cf_df.empty:
                     st.warning("Tabela de fluxos de caixa está vazia.")
                     valid_input = False

                for index, row in current_cf_df.iterrows():
                    if not valid_input: break
                    try:
                         cf = float(row['Fluxo (Cnn)'])
                         freq = int(row['Frequência (Fnn)'])
                         if freq < 1 :
                             st.error(f"Frequência inválida na linha {index+1}: {freq}. Deve ser >= 1.")
                             valid_input = False
                             break
                         cash_flows.extend([cf] * freq)
                    except (ValueError, TypeError):
                        st.error(f"Valor inválido na linha {index+1}. Verifique 'Fluxo' e 'Frequência'.")
                        valid_input = False
                        break

                if valid_input and len(cash_flows) > 1: # Precisa pelo menos CF0 e mais um
                    rate = discount_rate / 100.0
                    npv_result = npf.npv(rate, cash_flows)
                    st.success(f"NPV = {npv_result:,.2f}")
                elif valid_input:
                     st.warning("Insira pelo menos um fluxo de caixa subsequente (C01).")

            except Exception as e:
                st.error(f"Erro ao calcular NPV: {e}")

        if cf_calc_col2.button("Calcular IRR", key="irr_button"):
            try:
                cash_flows = [cf0]
                valid_input = True
                current_cf_df = st.session_state.cf_data # Usar estado atualizado
                if current_cf_df.empty:
                     st.warning("Tabela de fluxos de caixa está vazia.")
                     valid_input = False

                for index, row in current_cf_df.iterrows():
                    if not valid_input: break
                    try:
                        cf = float(row['Fluxo (Cnn)'])
                        freq = int(row['Frequência (Fnn)'])
                        if freq < 1 :
                            st.error(f"Frequência inválida na linha {index+1}: {freq}. Deve ser >= 1.")
                            valid_input = False
                            break
                        cash_flows.extend([cf] * freq)
                    except (ValueError, TypeError):
                         st.error(f"Valor inválido na linha {index+1}. Verifique 'Fluxo' e 'Frequência'.")
                         valid_input = False
                         break

                if valid_input and len(cash_flows) > 1:
                    sign_changes = sum(1 for i in range(len(cash_flows) - 1) if cash_flows[i] * cash_flows[i+1] < 0)
                    if sign_changes == 0:
                        st.error("Não é possível calcular IRR: Não há mudança de sinal nos fluxos de caixa (Error 5).")
                    else:
                        # Usar try-except dentro do cálculo da IRR para capturar erros específicos
                        try:
                             irr_result = npf.irr(cash_flows)
                             if np.isnan(irr_result): # Verificar se npf.irr retornou NaN
                                 st.error("Não foi possível encontrar uma solução para IRR (pode ser devido a múltiplas IRRs ou problema de convergência - Error 7).")
                             else:
                                 st.success(f"IRR = {irr_result * 100:,.4f} %")
                                 if sign_changes > 1:
                                     st.warning("Múltiplas mudanças de sinal detetadas. A IRR apresentada pode ser uma de várias possíveis. Interprete com cautela.")
                        except ValueError as irr_ve:
                             # npf.irr pode levantar ValueError se não encontrar solução
                             st.error(f"Erro ao calcular IRR: {irr_ve}. Verifique a sequência de fluxos.")

                elif valid_input:
                     st.warning("Insira pelo menos um fluxo de caixa subsequente (C01).")

            except Exception as e:
                 st.error(f"Erro inesperado ao preparar para calcular IRR: {e}")


# --- Aba: Conversão de Taxas ---
with main_tabs[3]:
    st.header("Conversão de Taxas de Juro")

    conv_tabs = st.tabs(["Explicação", "Calculadora"])

    with conv_tabs[0]:
        st.subheader("Taxa Nominal vs. Taxa Efetiva")
        st.markdown("""
        Esta função converte taxas de juro entre a taxa **Nominal Anual (NOM)** e a taxa **Efetiva Anual (EFF)**.

        * **NOM (Nominal Rate):** A taxa de juro anual declarada, também conhecida como APR (Annual Percentage Rate). Não leva em conta o efeito da capitalização dentro do ano.
        * **EFF (Effective Rate):** A taxa de juro anual que é *realmente* ganha ou paga após considerar o efeito da capitalização ao longo do ano.
        * **C/Y (Compounding Periods per Year):** O número de vezes que os juros são capitalizados por ano (ex: 12 para mensal, 4 para trimestral, 1 para anual).

        **Porquê converter?**
        Comparar investimentos apenas pela taxa nominal pode ser enganoso se tiverem diferentes períodos de capitalização. A taxa efetiva (EFF) fornece uma base de comparação mais justa.
        Por exemplo, 12% nominal capitalizado mensalmente resulta numa taxa efetiva maior do que 12% nominal capitalizado anualmente.

        **Fórmulas (Conceptuais):**
        * `EFF = (1 + NOM / C/Y)^(C/Y) - 1`
        * `NOM = C/Y * ((1 + EFF)^(1 / C/Y) - 1)`
        (As taxas NOM e EFF nas fórmulas são decimais, ex: 10% = 0.10)
        """)

    with conv_tabs[1]:
        st.subheader("Calculadora de Conversão")

        conv_col1, conv_col2, conv_col3 = st.columns(3)

        with conv_col1:
            nom_conv = st.number_input("NOM (Taxa Nominal Anual %)", min_value=0.0, value=15.0, format="%.4f", help="Ex: 15 para 15%", key="nom_conv_input")
        with conv_col2:
            eff_conv = st.number_input("EFF (Taxa Efetiva Anual %)", min_value=0.0, value=15.87, format="%.4f", help="Ex: 15.87 para 15.87%", key="eff_conv_input")
        with conv_col3:
            c_y_conv_input = st.number_input("C/Y (Capitalizações por Ano)", min_value=1, value=4, step=1, help="Ex: 4 para trimestral", key="cy_conv_input")

        st.divider()
        calc_conv_col1, calc_conv_col2 = st.columns(2)

        if calc_conv_col1.button("Calcular EFF a partir de NOM", key="calc_eff_button"):
            if c_y_conv_input <= 0:
                st.error("C/Y deve ser maior que zero.")
            else:
                try:
                    eff_calc = ((1 + (nom_conv / 100.0) / c_y_conv_input)**c_y_conv_input - 1) * 100.0
                    st.success(f"EFF = {eff_calc:.4f} %")
                except Exception as e:
                    st.error(f"Erro ao calcular EFF: {e}")

        if calc_conv_col2.button("Calcular NOM a partir de EFF", key="calc_nom_button"):
             if c_y_conv_input <= 0:
                st.error("C/Y deve ser maior que zero.")
             elif eff_conv < -100.0: # Matematicamente (1+EFF/100) deve ser > 0
                  st.error("Taxa Efetiva (EFF) demasiado baixa para calcular NOM.")
             else:
                try:
                    # Lidar com potencial expoente complexo se (1+eff/100) for negativo
                    base = 1 + eff_conv / 100.0
                    if base < 0:
                         st.error("Não é possível calcular NOM para esta taxa efetiva negativa (resultaria em raiz de número negativo).")
                    else:
                         nom_calc = c_y_conv_input * (base**(1.0 / c_y_conv_input) - 1.0) * 100.0
                         st.success(f"NOM = {nom_calc:.4f} %")
                except Exception as e:
                    st.error(f"Erro ao calcular NOM: {e}")


# --- Aba: Margem de Lucro ---
with main_tabs[4]:
    st.header("Margem de Lucro (Profit Margin)")

    margin_tabs = st.tabs(["Explicação", "Calculadora"])

    with margin_tabs[0]:
        st.subheader("Custo, Preço de Venda e Margem")
        st.markdown("""
        Esta função calcula a relação entre o Custo (CST), o Preço de Venda (SEL), e a Margem de Lucro Bruta (MAR).

        * **CST (Cost):** O custo original do item.
        * **SEL (Selling Price):** O preço pelo qual o item é vendido.
        * **MAR (Margin):** A margem de lucro bruta, expressa como uma *percentagem do preço de venda*.

        **Fórmula:**
        `MAR = ((SEL - CST) / SEL) * 100`

        **Diferença entre Margem e Markup:**
        É crucial não confundir Margem (Margin) com Markup.
        * **Margem (Margin):** Lucro como percentagem do **Preço de Venda**.
        * **Markup:** Lucro como percentagem do **Custo**. (Para Markup, use a folha de cálculo de Percent Change/Compound Interest).

        Pode calcular qualquer uma das três variáveis (CST, SEL, MAR) se conhecer as outras duas.
        """)

    with margin_tabs[1]:
        st.subheader("Calculadora de Margem de Lucro")

        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            cst_m = st.number_input("Custo (CST)", min_value=0.0, value=100.0, format="%.2f", key="cst_m_input")
        with m_col2:
            sel_m = st.number_input("Preço Venda (SEL)", min_value=0.0, value=125.0, format="%.2f", key="sel_m_input")
        with m_col3:
            # CORREÇÃO APLICADA AQUI: min_value e max_value definidos como None
            mar_m = st.number_input("Margem (MAR %)", min_value=None, max_value=None, value=20.0, format="%.2f", key="mar_m_input", help="Pode ser negativa se Custo > Preço Venda.")

        st.divider()
        st.write("**Calcular Variável Desconhecida:**")
        calc_m_col1, calc_m_col2, calc_m_col3 = st.columns(3)

        if calc_m_col1.button("Calcular Custo (CST)", key="calc_cst_m_button"):
            if sel_m <= 0 and mar_m != 0 : # Se mar=0, custo = sel
                st.error("Preço de Venda (SEL) deve ser positivo para calcular Custo se a Margem não for zero.")
            else:
                try:
                    cst_calc = sel_m * (1.0 - mar_m / 100.0)
                    st.success(f"Custo (CST) = {cst_calc:.2f}")
                except Exception as e:
                    st.error(f"Erro ao calcular Custo: {e}")

        if calc_m_col2.button("Calcular Preço Venda (SEL)", key="calc_sel_m_button"):
             if abs(1.0 - mar_m / 100.0) < 1e-9: # Evitar divisão por zero se MAR = 100%
                  st.error("Margem não pode ser 100%.")
             elif cst_m < 0:
                  st.error("Custo (CST) não pode ser negativo.")
             else:
                 try:
                    sel_calc = cst_m / (1.0 - mar_m / 100.0)
                    st.success(f"Preço Venda (SEL) = {sel_calc:.2f}")
                 except ZeroDivisionError:
                      st.error("Margem não pode ser 100%.")
                 except Exception as e:
                    st.error(f"Erro ao calcular Preço Venda: {e}")

        if calc_m_col3.button("Calcular Margem (MAR)", key="calc_mar_m_button"):
            if sel_m == 0: # Evitar divisão por zero
                st.error("Preço de Venda (SEL) não pode ser zero para calcular a Margem.")
            else:
                try:
                    mar_calc = ((sel_m - cst_m) / sel_m) * 100.0
                    st.success(f"Margem (MAR) = {mar_calc:.2f} %")
                except Exception as e:
                    st.error(f"Erro ao calcular Margem: {e}")


# --- Aba: Ponto de Equilíbrio (Breakeven) ---
with main_tabs[5]:
    st.header("Análise do Ponto de Equilíbrio (Breakeven)")

    be_tabs = st.tabs(["Explicação", "Calculadora"])

    with be_tabs[0]:
        st.subheader("O que é o Ponto de Equilíbrio?")
        st.markdown("""
        A análise do ponto de equilíbrio (breakeven) ajuda a determinar a quantidade de vendas necessária para cobrir todos os custos (fixos e variáveis), resultando em lucro zero. É o ponto onde as receitas totais igualam os custos totais.

        **Variáveis:**
        * **FC (Fixed Costs):** Custos que não variam com a quantidade produzida/vendida (ex: renda, salários fixos).
        * **VC (Variable Cost per Unit):** Custo associado a cada unidade produzida/vendida (ex: matéria-prima, comissões por unidade).
        * **P (Price per Unit):** Preço de venda de cada unidade.
        * **Q (Quantity):** Número de unidades produzidas/vendidas.
        * **PFT (Profit):** Lucro total desejado. Para encontrar o ponto de equilíbrio *exato*, define-se PFT = 0.

        **Fórmula Fundamental:**
        `Receita Total = Custos Totais + Lucro`
        `P * Q = FC + (VC * Q) + PFT`

        Rearranjando para encontrar a quantidade (Q) necessária para um dado lucro (PFT):
        `Q = (FC + PFT) / (P - VC)`

        O termo `(P - VC)` é conhecido como **Margem de Contribuição por Unidade**.

        Pode usar esta folha de cálculo para encontrar qualquer uma das cinco variáveis se conhecer as outras quatro. Para encontrar a quantidade de equilíbrio (lucro zero), introduza PFT = 0 e calcule Q.
        """)

    with be_tabs[1]:
        st.subheader("Calculadora Breakeven")

        be_col1, be_col2 = st.columns(2)
        with be_col1:
            fc_be = st.number_input("Custos Fixos (FC)", min_value=0.0, value=3000.0, format="%.2f", key="fc_be_input")
            vc_be = st.number_input("Custo Variável por Unidade (VC)", min_value=0.0, value=15.0, format="%.2f", key="vc_be_input")
            p_be = st.number_input("Preço por Unidade (P)", min_value=0.0, value=20.0, format="%.2f", key="p_be_input")
        with be_col2:
            pft_be = st.number_input("Lucro Desejado (PFT)", value=0.0, format="%.2f", help="Insira 0 para calcular o ponto de equilíbrio.", key="pft_be_input")
            q_be = st.number_input("Quantidade (Q)", min_value=0.0, value=600.0, format="%.2f", key="q_be_input")

        # Validação P > VC
        if p_be <= vc_be and p_be is not None and vc_be is not None:
            st.warning("O Preço por Unidade (P) deve ser maior que o Custo Variável por Unidade (VC) para que o breakeven seja possível ou o lucro seja positivo.")

        st.divider()
        st.write("**Calcular Variável Desconhecida:**")
        calc_be_col1, calc_be_col2, calc_be_col3, calc_be_col4, calc_be_col5 = st.columns(5)

        # Botões usam a função calculate_breakeven definida no TOPO do script
        if calc_be_col1.button("Calcular FC", key="calc_fc_be"):
            result = calculate_breakeven({'VC': vc_be, 'P': p_be, 'PFT': pft_be, 'Q': q_be, 'Target': 'FC', 'FC': None})
            if isinstance(result, str): st.error(result)
            else: st.success(f"FC = {result:.2f}")

        if calc_be_col2.button("Calcular VC", key="calc_vc_be"):
             result = calculate_breakeven({'FC': fc_be, 'P': p_be, 'PFT': pft_be, 'Q': q_be, 'Target': 'VC', 'VC': None})
             if isinstance(result, str): st.error(result)
             else: st.success(f"VC = {result:.2f}")

        if calc_be_col3.button("Calcular P", key="calc_p_be"):
            result = calculate_breakeven({'FC': fc_be, 'VC': vc_be, 'PFT': pft_be, 'Q': q_be, 'Target': 'P', 'P': None})
            if isinstance(result, str): st.error(result)
            else: st.success(f"P = {result:.2f}")

        if calc_be_col4.button("Calcular PFT", key="calc_pft_be"):
            result = calculate_breakeven({'FC': fc_be, 'VC': vc_be, 'P': p_be, 'Q': q_be, 'Target': 'PFT', 'PFT': None})
            if isinstance(result, str): st.error(result)
            else: st.success(f"PFT = {result:.2f}")

        if calc_be_col5.button("Calcular Q", key="calc_q_be"):
            result = calculate_breakeven({'FC': fc_be, 'VC': vc_be, 'P': p_be, 'PFT': pft_be, 'Target': 'Q', 'Q': None})
            if isinstance(result, str): st.error(result)
            else: st.success(f"Q = {result:.2f}")


# --- Aba: Depreciação ---
with main_tabs[6]:
    st.header("Depreciação de Ativos")

    depr_tabs = st.tabs(["Explicação", "Calculadora"])

    with depr_tabs[0]:
        st.subheader("O que é Depreciação?")
        st.markdown("""
        A depreciação é a alocação sistemática do custo de um ativo tangível ao longo da sua vida útil. Representa a perda de valor do ativo devido ao uso, desgaste ou obsolescência.
        Existem vários métodos para calcular a despesa de depreciação anual.

        **Variáveis Principais:**
        * **Método:** O método de cálculo da depreciação (SL, SYD, DB, DBX).
        * **LIF (Life):** A vida útil estimada do ativo em anos.
        * **M01 (Starting Month):** O mês em que o ativo começa a ser depreciado (ex: 1 para Janeiro, 3.5 para meio de Março).
        * **CST (Cost):** O custo original de aquisição do ativo.
        * **SAL (Salvage Value):** O valor residual estimado do ativo no final da sua vida útil.
        * **YR (Year):** O ano específico para o qual se deseja calcular a depreciação.

        **Valores Calculados:**
        * **DEP (Depreciation):** A despesa de depreciação para o ano YR especificado.
        * **RBV (Remaining Book Value):** O valor contabilístico do ativo no final do ano YR (Custo - Depreciação Acumulada).
        * **RDV (Remaining Depreciable Value):** O valor ainda por depreciar no final do ano YR (RBV - Valor Residual).

        **Métodos Comuns (Simplificados):**
        * **SL (Straight-Line / Linha Reta):** Distribui o custo depreciável (Custo - Valor Residual) igualmente por cada ano da vida útil.
            * `Depreciação Anual = (CST - SAL) / LIF` (Ajustado para o primeiro e último ano com base em M01).
        * **SYD (Sum-of-the-Years' Digits / Soma dos Dígitos dos Anos):** Método acelerado que resulta em maior depreciação nos primeiros anos.
            * Calcula-se a soma dos dígitos dos anos (ex: 3 anos -> 1+2+3=6). A fração de depreciação para o ano `t` é `(LIF - t + 1) / SomaDosDígitos`.
        * **DB (Declining Balance / Saldo Decrescente):** Método acelerado que aplica uma taxa fixa ao valor contabilístico *restante* (RBV) de cada ano. Frequentemente usa-se o dobro da taxa da linha reta (DB 200%).
            * `Taxa DB = FactorDB / LIF` (FactorDB é geralmente 1.5 ou 2.0 para 150% ou 200%).
            * `Depreciação Anual = RBV_inicio_ano * Taxa DB`. A depreciação não pode levar RBV abaixo de SAL.
        * **DBX (Declining Balance with Crossover):** Igual ao DB, mas muda automaticamente para Linha Reta quando esta última resultar numa depreciação anual maior. (Este método é mais complexo de implementar aqui).

        **Nota:** As calculadoras financeiras podem arredondar resultados intermédios com base nas casas decimais definidas, o que pode levar a pequenas diferenças vs. cálculos sem arredondamento intermédio.
        """)

    with depr_tabs[1]:
        st.subheader("Calculadora de Depreciação")

        # Guardar estado para cálculo ano-a-ano
        if 'depr_state' not in st.session_state:
            st.session_state.depr_state = {
                'accumulated_depreciation': 0.0,
                'last_yr_calculated': 0,
                'current_rbv': 0.0,
                'current_rdv': 0.0,
                'last_inputs': {} # Guardar inputs para reset
            }

        depr_col1, depr_col2 = st.columns(2)

        with depr_col1:
            method_depr = st.selectbox("Método de Depreciação", ["SL", "SYD", "DB"], help="SL=Linha Reta, SYD=Soma dos Dígitos, DB=Saldo Decrescente", key="depr_method")
            lif_depr = st.number_input("Vida Útil (LIF - anos)", min_value=1, value=5, step=1, key="depr_lif")
            m01_depr = st.number_input("Mês Inicial (M01)", min_value=1.0, max_value=12.999, value=1.0, step=0.1, format="%.2f", help="Ex: 1.0 = Início Jan, 3.5 = Meio Março", key="depr_m01")
            db_factor = 0 # Inicializar
            if method_depr == "DB":
                db_factor_percent = st.number_input("Fator DB (%)", min_value=1.0, value=200.0, step=10.0, format="%.1f", help="Ex: 200.0 para Dobro Saldo Decrescente", key="depr_db_factor")
                db_factor = db_factor_percent / 100.0

        with depr_col2:
            cst_depr = st.number_input("Custo Inicial (CST)", min_value=0.0, value=10000.0, format="%.2f", key="depr_cst")
            sal_depr = st.number_input("Valor Residual (SAL)", min_value=0.0, value=1000.0, format="%.2f", key="depr_sal")
            yr_depr = st.number_input("Ano a Calcular (YR)", min_value=1, max_value=int(lif_depr) + 1, value=1, step=1, key="depr_yr")

        # Guardar inputs atuais para poder fazer reset
        current_inputs = {
             'method': method_depr, 'lif': lif_depr, 'm01': m01_depr, 'cst': cst_depr,
             'sal': sal_depr, 'db_factor': db_factor, 'yr': yr_depr
        }

        if sal_depr >= cst_depr:
            st.error("Valor Residual (SAL) não pode ser maior ou igual ao Custo (CST).")


        # Função de cálculo da depreciação (movida para fora do botão para reutilização)
        # --- Esta função foi definida anteriormente, não precisa redefinir ---
        # def calculate_depreciation_for_year(...): ...


        # Botão Calcular / Próximo Ano
        calc_depr_col1, calc_depr_col2 = st.columns(2)

        if calc_depr_col1.button(f"Calcular para Ano {yr_depr}", key="depr_calc_button"):
            # Verificar se inputs mudaram desde o último cálculo com sucesso
            if st.session_state.depr_state['last_yr_calculated'] > 0 and st.session_state.depr_state.get('last_inputs') != current_inputs:
                 st.warning("Inputs alterados. Histórico de cálculo reiniciado. A calcular do zero.")
                 st.session_state.depr_state = { # Reset state
                     'accumulated_depreciation': 0.0, 'last_yr_calculated': 0,
                     'current_rbv': cst_depr, 'current_rdv': max(0.0, cst_depr - sal_depr),
                     'last_inputs': {}
                 }


            accumulated_dep = 0.0
            results = {}
            error_msg = None
            rbv_start_of_target_year = cst_depr # Inicializar

            # Recalcular do início até ao ano YR para obter o estado correto
            for y_calc in range(1, yr_depr + 1):
                # --- Nova função interna para encapsular lógica ---
                def calculate_single_year(year_num, method, life, m01_frac, cost, salvage, db_rate, current_accum_dep):
                    depreciable_base = cost - salvage
                    if depreciable_base <= 0: return {'DEP': 0.0, 'RBV': salvage, 'RDV': 0.0, 'AccDep': cost - salvage}

                    first_year_factor = (13.0 - m01_frac) / 12.0
                    if m01_frac == int(m01_frac): first_year_factor = (12.0 - int(m01_frac) + 1) / 12.0
                    last_year_factor = 1.0 - first_year_factor # Simplificação

                    dep_year = 0.0
                    rbv_start = cost - current_accum_dep
                    if rbv_start <= salvage: return {'DEP': 0.0, 'RBV': salvage, 'RDV': 0.0, 'AccDep': cost - salvage}

                    if method == "SL":
                        annual_dep_full = depreciable_base / life if life > 0 else 0
                        if year_num == 1: dep_year = annual_dep_full * first_year_factor
                        elif year_num == int(life) + 1 and last_year_factor > 0 : dep_year = annual_dep_full * last_year_factor
                        elif year_num <= life: dep_year = annual_dep_full
                        else: dep_year = 0.0
                    elif method == "SYD":
                        syd_total = life * (life + 1) / 2.0
                        if syd_total == 0: return {'DEP': 0.0, 'RBV': rbv_start, 'RDV': max(0.0, rbv_start - salvage), 'AccDep': current_accum_dep}
                        # Abordagem simplificada para M01 - pode não ser perfeita
                        def syd_dep_full(k, base, total, life_int):
                             if k < 1 or k > life_int or total == 0: return 0
                             return base * (life_int - k + 1) / total

                        dep_full_prev = syd_dep_full(year_num - 1, depreciable_base, syd_total, int(life))
                        dep_full_curr = syd_dep_full(year_num, depreciable_base, syd_total, int(life))

                        year_start_fraction = (m01_frac - 1.0) / 12.0 if m01_frac > 1 else 0
                        year_end_fraction = 1.0 - year_start_fraction

                        if year_num == 1:
                             dep_year = dep_full_curr * first_year_factor
                        elif year_num <= life :
                             dep_year = (dep_full_prev * year_start_fraction) + (dep_full_curr * year_end_fraction)
                        elif year_num == int(life) + 1 and last_year_factor > 0:
                             dep_year = dep_full_prev * last_year_factor
                        else: dep_year = 0.0

                    elif method == "DB":
                        db_rate_eff = db_rate / life if life > 0 else 0
                        dep_provisional = rbv_start * db_rate_eff
                        if year_num == 1: dep_year = dep_provisional * first_year_factor
                        elif year_num <= life: dep_year = dep_provisional
                        else: dep_year = 0.0

                    # Ajuste final para não depreciar abaixo do valor residual
                    if rbv_start - dep_year < salvage:
                        dep_year = max(0.0, rbv_start - salvage)

                    new_accum_dep = current_accum_dep + dep_year
                    new_rbv = cost - new_accum_dep
                    new_rdv = max(0.0, new_rbv - salvage)

                    return {'DEP': dep_year, 'RBV': new_rbv, 'RDV': new_rdv, 'AccDep': new_accum_dep}
                # --- Fim da função interna ---

                # Chamar a função interna
                if y_calc == yr_depr: # Guardar RBV no início do ano alvo
                     rbv_start_of_target_year = cst_depr - accumulated_dep

                year_result = calculate_single_year(y_calc, method_depr, lif_depr, m01_depr, cst_depr, sal_depr, db_factor, accumulated_dep)

                if "error" in year_result:
                     error_msg = year_result["error"]
                     break
                # Atualizar depreciação acumulada para a próxima iteração
                accumulated_dep = year_result['AccDep']
                # Guardar o resultado do ano alvo
                if y_calc == yr_depr:
                     results = year_result

            # --- Fim do loop de cálculo ---

            if error_msg:
                 st.error(f"Erro ao calcular para o ano {y_calc if 'y_calc' in locals() else yr_depr}: {error_msg}")
                 # Limpar estado se houve erro
                 st.session_state.depr_state = {
                     'accumulated_depreciation': 0.0, 'last_yr_calculated': 0,
                     'current_rbv': cst_depr, 'current_rdv': max(0.0, cst_depr - sal_depr),
                     'last_inputs': {}
                 }
            elif results:
                st.session_state.depr_state['accumulated_depreciation'] = results['AccDep']
                st.session_state.depr_state['last_yr_calculated'] = yr_depr
                st.session_state.depr_state['current_rbv'] = results['RBV']
                st.session_state.depr_state['current_rdv'] = results['RDV']
                st.session_state.depr_state['last_inputs'] = current_inputs # Guardar inputs que deram este resultado

                st.success(f"Resultados para o Ano {yr_depr}:")
                res_col1, res_col2, res_col3 = st.columns(3)
                res_col1.metric("Depreciação (DEP)", f"{results['DEP']:,.2f} €")
                res_col2.metric("Valor Contabilístico Rest. (RBV)", f"{results['RBV']:,.2f} €")
                res_col3.metric("Valor Depreciável Rest. (RDV)", f"{results['RDV']:,.2f} €")
            else:
                 # Se results ficou vazio (ex: yr_depr=0?), mostrar aviso
                 st.warning("Não foi possível calcular. Verifique os inputs.")
                 st.session_state.depr_state = { # Reset state
                     'accumulated_depreciation': 0.0, 'last_yr_calculated': 0,
                     'current_rbv': cst_depr, 'current_rdv': max(0.0, cst_depr - sal_depr),
                     'last_inputs': {}
                 }


        # Botão para limpar estado
        if calc_depr_col2.button("Limpar Histórico de Cálculo", key="depr_clear_button"):
             st.session_state.depr_state = {
                'accumulated_depreciation': 0.0,
                'last_yr_calculated': 0,
                'current_rbv': cst_depr, # Reset RBV para Custo inicial
                'current_rdv': max(0.0, cst_depr - sal_depr), # Reset RDV para base depreciável
                'last_inputs': {}
             }
             st.rerun() # Recarrega para refletir a limpeza


        # Mostrar estado atual se houver
        if st.session_state.depr_state['last_yr_calculated'] > 0:
            st.caption(f"Último cálculo: Ano {st.session_state.depr_state['last_yr_calculated']}, Dep. Acumulada: {st.session_state.depr_state['accumulated_depreciation']:,.2f} €, RBV Final: {st.session_state.depr_state['current_rbv']:,.2f} €")


# --- Aba: Datas ---
with main_tabs[7]:
    st.header("Cálculo de Datas")

    date_tabs = st.tabs(["Explicação", "Calculadora"])

    with date_tabs[0]:
        st.subheader("Calcular Dias ou Datas")
        st.markdown("""
        Esta função permite calcular o número de dias entre duas datas ou determinar uma data futura/passada com base num número de dias.

        **Variáveis:**
        * **DT1 (Date 1):** A data inicial.
        * **DT2 (Date 2):** A data final.
        * **DBD (Days Between Dates):** O número de dias entre DT1 e DT2.
        * **Método Dia (Day-Count Method):** Como os dias são contados:
            * **ACT (Actual/Actual):** Usa o número real de dias em cada mês e considera anos bissextos.
            * **360 (30/360):** Assume que todos os meses têm 30 dias (total 360 dias por ano). Usado em alguns cálculos de juros de obrigações/mercado monetário.

        **Funcionalidades:**
        1.  **Calcular DBD:** Dados DT1 e DT2, calcula o número de dias entre elas usando o método ACT ou 360.
        2.  **Calcular DT2:** Dados DT1 e DBD, calcula a data DT2 (e o dia da semana correspondente). **Só funciona com o método ACT.**
        3.  **Calcular DT1:** Dados DT2 e DBD, calcula a data DT1 (e o dia da semana correspondente). **Só funciona com o método ACT.**

        **Notas:**
        * Algumas calculadoras financeiras (ex: BA II Plus) operam entre 1 de Janeiro de 1980 e 31 de Dezembro de 2079. Esta aplicação usa as capacidades do Python, que tem um alcance maior.
        * Ao calcular uma data (DT1 ou DT2), o dia da semana é mostrado.
        * O método 360 tem regras específicas para lidar com dias 31.
        """)

    with date_tabs[1]:
        st.subheader("Calculadora de Datas")

        date_col1, date_col2, date_col3 = st.columns(3)

        # Definir limites de data se quisermos replicar BAII, caso contrário None
        min_date_limit = datetime.date(1980, 1, 1)
        max_date_limit = datetime.date(2079, 12, 31)

        with date_col1:
             dt1_date = st.date_input("Data 1 (DT1)", value=datetime.date(2003, 9, 4), key="dt1_date_input") # Exemplo Guia p.64
        with date_col2:
             dt2_date = st.date_input("Data 2 (DT2)", value=datetime.date(2003, 11, 1), key="dt2_date_input") # Exemplo Guia p.64
        with date_col3:
             dbd_date = st.number_input("Dias Entre Datas (DBD)", min_value=0, value=58, step=1, key="dbd_date_input") # Exemplo Guia p.64

        day_count_method_date = st.selectbox("Método de Contagem de Dias", ["ACT", "360"], index=0, key="day_count_date")

        st.divider()
        st.write("**Calcular Variável Desconhecida:**")
        calc_date_col1, calc_date_col2, calc_date_col3 = st.columns(3)

        # Funções Auxiliares Datas
        def days_360(date1, date2):
            d1, m1, y1 = date1.day, date1.month, date1.year
            d2, m2, y2 = date2.day, date2.month, date2.year

            # Regras 30/360 US (simplificadas, conforme guia)
            if d1 == 31: d1 = 30
            if d2 == 31 and d1 == 30: d2 = 30

            if d1 < 0 or d2 < 0 or m1 < 0 or m2 < 0: # Basic check
                 raise ValueError("Componentes da data inválidos para cálculo 360")

            return (y2 - y1) * 360 + (m2 - m1) * 30 + (d2 - d1)

        # --- Botões de Cálculo ---
        if calc_date_col1.button("Calcular DBD", key="calc_dbd_button"):
            if dt1_date is None or dt2_date is None:
                st.error("Datas DT1 e DT2 devem ser fornecidas.")
            else:
                if day_count_method_date == "ACT":
                    try:
                         delta = dt2_date - dt1_date
                         dbd_calc = delta.days
                         st.success(f"DBD (ACT) = {dbd_calc} dias")
                    except Exception as e:
                         st.error(f"Erro ACT: {e}")
                else: # 360
                    try:
                         # Note: days_360 pode retornar negativo se dt1 > dt2
                         dbd_calc = days_360(dt1_date, dt2_date)
                         st.success(f"DBD (360) = {dbd_calc} dias")
                    except Exception as e:
                         st.error(f"Erro 360: {e}")

        if calc_date_col2.button("Calcular DT2", key="calc_dt2_button"):
            if day_count_method_date == "360":
                st.error("Não é possível calcular DT2 com o método 360.")
            elif dt1_date is None or dbd_date is None:
                st.error("DT1 e DBD devem ser fornecidos.")
            elif dbd_date < 0:
                 st.error("DBD deve ser não-negativo para calcular DT2.")
            else:
                try:
                    dt2_calc = dt1_date + datetime.timedelta(days=dbd_date)
                    day_name = dt2_calc.strftime("%A") # Nome do dia da semana em inglês por defeito
                    # Para português:
                    # import locale
                    # try:
                    #     locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8') # Ou 'Portuguese_Portugal.1252' no Windows
                    #     day_name = dt2_calc.strftime("%A")
                    # except locale.Error:
                    #      day_name = dt2_calc.strftime("%A") # Fallback para inglês
                    st.success(f"DT2 (ACT) = {dt2_calc.strftime('%Y-%m-%d')} ({day_name})")
                except OverflowError:
                     st.error("Erro: O cálculo da data resulta num valor fora do intervalo suportado.")
                except Exception as e:
                     st.error(f"Erro ao calcular DT2: {e}")

        if calc_date_col3.button("Calcular DT1", key="calc_dt1_button"):
             if day_count_method_date == "360":
                 st.error("Não é possível calcular DT1 com o método 360.")
             elif dt2_date is None or dbd_date is None:
                 st.error("DT2 e DBD devem ser fornecidos.")
             elif dbd_date < 0:
                 st.error("DBD deve ser não-negativo para calcular DT1.")
             else:
                 try:
                     dt1_calc = dt2_date - datetime.timedelta(days=dbd_date)
                     day_name = dt1_calc.strftime("%A")
                     # locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8') # Para dia em PT
                     # day_name = dt1_calc.strftime("%A")
                     st.success(f"DT1 (ACT) = {dt1_calc.strftime('%Y-%m-%d')} ({day_name})")
                 except OverflowError:
                      st.error("Erro: O cálculo da data resulta num valor fora do intervalo suportado.")
                 except Exception as e:
                      st.error(f"Erro ao calcular DT1: {e}")

# --- Aba: Obrigações (Bonds) ---
with main_tabs[8]: # Ajuste o índice se necessário
    st.header("Análise de Obrigações (Bonds)")

    bond_tabs = st.tabs(["Explicação", "Calculadora"])

    with bond_tabs[0]:
        # A explicação permanece a mesma da resposta anterior
        st.subheader("Calcular Preço, Yield e Juros Corridos")
        st.markdown("""
        Esta função ajuda a analisar obrigações (bonds), calculando o seu preço (Price), rendibilidade até à maturidade ou call (Yield), e juros corridos (Accrued Interest).

        **Variáveis Principais:**
        * **SDT (Settlement Date):** Data em que a obrigação é comprada/liquidada.
        * **CPN (Coupon Rate %):** Taxa de juro anual que a obrigação paga, como percentagem do valor nominal.
        * **RDT (Redemption Date):** Data em que a obrigação é reembolsada (maturidade ou data de call).
        * **RV (Redemption Value %):** Valor recebido no reembolso, como percentagem do valor nominal (normalmente 100% para maturidade, pode ser diferente para call).
        * **Método Dia (Day-Count):** ACT (Actual/Actual) ou 360 (30/360), para cálculo de juros corridos e períodos fracionários.
        * **Cupões/Ano:** Número de pagamentos de cupão por ano (1/Y ou 2/Y - semianual é comum).
        * **YLD (Yield %):** A taxa de retorno anualizada que um investidor obterá se mantiver a obrigação até RDT, considerando o preço pago e os cupões. É calculado a partir de PRI ou é input para calcular PRI.
        * **PRI (Price %):** O preço "limpo" da obrigação (sem juros corridos), expresso como percentagem do valor nominal. É calculado a partir de YLD ou é input para calcular YLD.
        * **AI (Accrued Interest %):** Juros que se acumularam desde o último pagamento de cupão até à data de liquidação (SDT). O comprador paga este valor ao vendedor, além do preço limpo (PRI). O preço total ("sujo") é PRI + AI.

        **Cálculos:**
        1.  **Calcular PRI e AI:** Dados SDT, CPN, RDT, RV, YLD, Método Dia e Cupões/Ano.
        2.  **Calcular YLD e AI:** Dados SDT, CPN, RDT, RV, PRI, Método Dia e Cupões/Ano. (Usa um solver iterativo).

        **Fórmulas (Complexas):** As fórmulas envolvem descontar os fluxos de caixa futuros (cupões e reembolso final) à taxa YLD, considerando os dias exatos entre as datas com base no método de contagem. Veja o apêndice do guia para detalhes.
        """)

    with bond_tabs[1]:
        from scipy.optimize import newton # Importar o solver
        import datetime

        st.subheader("Calculadora de Obrigações")

        # --- Funções Auxiliares Específicas para Obrigações ---

        @st.cache_data # Cache para evitar recalcular datas repetidamente
        def get_coupon_dates_list(rdt: datetime.date, sdt: datetime.date, coupons_per_year: int):
            """ Gera lista de datas de cupão relevantes à volta de sdt """
            if coupons_per_year <= 0: return []
            coupon_dates = []
            current_dt = rdt
            interval_months = 12 / coupons_per_year
            # Retroceder para gerar datas anteriores e futuras
            limit_date_past = sdt - datetime.timedelta(days=max(400, 400 / coupons_per_year)) # Olhar ~1 período+ para trás
            limit_date_future = rdt + datetime.timedelta(days=1) # Incluir RDT

            while current_dt >= limit_date_past:
                coupon_dates.append(current_dt)
                year, month = current_dt.year, current_dt.month
                new_month_float = month - interval_months
                new_year = year
                while new_month_float <= 0:
                    new_month_float += 12
                    new_year -= 1

                new_month = int(new_month_float)
                # Tentar manter o dia, ajustar se inválido
                day = current_dt.day
                try:
                    # Lidar com dia 29, 30, 31 em meses mais curtos
                    last_day_of_new_month = pd.Timestamp(year=new_year, month=new_month, day=1).days_in_month
                    day = min(day, last_day_of_new_month)
                    current_dt = datetime.date(new_year, new_month, day)
                except ValueError:
                     # Fallback extremo, parar se data inválida
                     break
                # Evitar loop infinito
                if len(coupon_dates) > 200: break # Limite arbitrário

            coupon_dates.sort()
            # Filtrar para ter apenas datas relevantes (um pouco antes de SDT até RDT)
            relevant_dates = [dt for dt in coupon_dates if dt <= limit_date_future and dt >= limit_date_past]
             # Garantir que RDT está na lista se for uma data de cupão teórica
            if rdt not in relevant_dates:
                 # Verificar se RDT coincide com uma data teórica
                 is_rdt_coupon_date = False
                 test_dt = relevant_dates[-1] if relevant_dates else rdt
                 while test_dt < rdt:
                      year, month = test_dt.year, test_dt.month
                      new_month_float = month + interval_months
                      new_year = year
                      while new_month_float > 12:
                           new_month_float -= 12
                           new_year += 1
                      new_month = int(new_month_float)
                      day = test_dt.day
                      try:
                           last_day_of_new_month = pd.Timestamp(year=new_year, month=new_month, day=1).days_in_month
                           day = min(day, last_day_of_new_month)
                           test_dt = datetime.date(new_year, new_month, day)
                           if test_dt == rdt:
                                is_rdt_coupon_date = True
                                break
                      except ValueError: break
                 if is_rdt_coupon_date and rdt not in relevant_dates:
                      relevant_dates.append(rdt)
                      relevant_dates.sort()


            return relevant_dates

        def days_360(date1: datetime.date, date2: datetime.date) -> int:
            """ Calcula dias entre datas usando 30/360 (aproximação do guia) """
            d1, m1, y1 = date1.day, date1.month, date1.year
            d2, m2, y2 = date2.day, date2.month, date2.year
            # Regras simplificadas 30/360
            if d1 == 31: d1 = 30
            if d2 == 31 and d1 == 30: d2 = 30
            # Adicionar verificação para fim de Fevereiro (regra comum, não explícita no guia)
            is_feb_end1 = (m1 == 2 and d1 == pd.Timestamp(date1).days_in_month)
            is_feb_end2 = (m2 == 2 and d2 == pd.Timestamp(date2).days_in_month)
            if is_feb_end1 and is_feb_end2: # Ambos fim de Fev
                 d2 = 30
            if is_feb_end1: # Apenas d1 fim de Fev
                 d1 = 30

            # Cálculo básico
            return (y2 - y1) * 360 + (m2 - m1) * 30 + (d2 - d1)

        def days_between(date1: datetime.date, date2: datetime.date, method: str) -> int:
            """ Calcula dias entre datas usando método ACT ou 360 """
            if method == "ACT":
                return (date2 - date1).days
            elif method == "360":
                # days_360 retorna negativo se date1 > date2
                return days_360(date1, date2)
            else:
                raise ValueError("Método de contagem de dias inválido")

        def calculate_accrued_interest(sdt, cpn_rate, coupons_per_year, day_count_method, coupon_dates_list):
            """ Calcula Juros Corridos (AI) """
            if cpn_rate == 0 or coupons_per_year == 0: return 0.0

            prev_coupon_date = None
            next_coupon_date = None
            for dt in reversed(coupon_dates_list): # Procurar para trás
                if dt <= sdt:
                    prev_coupon_date = dt
                    break
            for dt in coupon_dates_list: # Procurar para a frente
                 if dt > sdt:
                      next_coupon_date = dt
                      break

            if not prev_coupon_date or not next_coupon_date:
                # Pode acontecer se SDT for antes da primeira data de cupão gerada ou após RDT
                # Tentar encontrar o período teórico
                # Simplificação: retornar 0 se não encontrar período claro
                st.warning(f"Não foi possível determinar o período de cupão para SDT={sdt}. AI pode estar incorreto.")
                return 0.0 # Ou levantar um erro mais específico

            try:
                days_accrued = days_between(prev_coupon_date, sdt, day_count_method)
                days_in_period = days_between(prev_coupon_date, next_coupon_date, day_count_method)

                if days_in_period <= 0:
                     st.warning(f"Período de cupão inválido ({days_in_period} dias) entre {prev_coupon_date} e {next_coupon_date}. AI pode estar incorreto.")
                     return 0.0 # Evitar divisão por zero

                coupon_amount_per_period = (cpn_rate / 100.0) / coupons_per_year * 100.0 # Assume 100 par
                ai = (days_accrued / days_in_period) * coupon_amount_per_period
                return ai
            except Exception as e:
                st.error(f"Erro no cálculo de AI: {e}")
                return None

        def calculate_bond_price_dirty(yield_rate_annual, sdt, rdt, cpn_rate, rv_percent, coupons_per_year, day_count_method, coupon_dates_list):
            """ Calcula o Preço Sujo (Dirty Price = PV dos fluxos futuros @ yield) - Aproximado """
            if coupons_per_year == 0: # Caso de Zero Coupon Bond (simplificado)
                 yld_decimal = yield_rate_annual / 100.0
                 days_to_maturity = days_between(sdt, rdt, day_count_method)
                 # Usar composição anual ACT/365 para simplificar
                 years_to_maturity = days_between(sdt, rdt, "ACT") / 365.0
                 if (1 + yld_decimal) <= 0: return None # Evitar erro
                 dirty_price = (rv_percent / 100.0 * 100.0) / ((1 + yld_decimal)**years_to_maturity)
                 return dirty_price

            yld_per_period = (yield_rate_annual / 100.0) / coupons_per_year
            pv_total = 0.0
            par_value = 100.0 # Assumir par = 100

            # Encontrar datas futuras e período atual
            future_coupon_dates = [dt for dt in coupon_dates_list if dt > sdt and dt <= rdt]
            prev_coupon_date = next((dt for dt in reversed(coupon_dates_list) if dt <= sdt), None)
            next_coupon_date = next((dt for dt in coupon_dates_list if dt > sdt), None)

            if not next_coupon_date: # SDT é na ou após a última data de cupão antes de RDT?
                 next_coupon_date = rdt # O próximo fluxo relevante é o reembolso

            if not prev_coupon_date:
                 # Se não há cupão anterior, pode ser um bond novo ou período inicial estranho
                 # Simplificação: Usar SDT como início do período para cálculo de dias? Não ideal.
                 # Tentar estimar uma data anterior teórica
                 intervalo_dias = 365 / coupons_per_year
                 prev_coupon_date = next_coupon_date - datetime.timedelta(days=intervalo_dias)


            # Calcular dias DSC e E (usando ACT para períodos fracionários no desconto)
            try:
                # Usar ACT para o desconto fracionário é mais comum, mesmo se AI usa 360
                dsc = days_between(sdt, next_coupon_date, "ACT")
                e = days_between(prev_coupon_date, next_coupon_date, "ACT")
                if e <= 0: e = 365.0 / coupons_per_year # Fallback se datas inválidas
                w = dsc / e # Fração do período até próximo cupão
            except Exception:
                 st.warning("Erro ao calcular dias para desconto fracionário. Usando w=1.")
                 w = 1.0 # Simplificação se cálculo de dias falhar

            # Desconto base por período
            v = 1.0 / (1.0 + yld_per_period)

            # 1. Descontar Cupões Futuros
            coupon_amount = (cpn_rate / 100.0) / coupons_per_year * par_value
            if coupon_amount > 0:
                 for i, coupon_date in enumerate(future_coupon_dates):
                      # O expoente é k-1 + w (onde k=1 para next_coupon_date)
                      exponent = i + w
                      pv_coupon = coupon_amount * (v ** exponent)
                      pv_total += pv_coupon

            # 2. Descontar Valor de Reembolso (RV)
            # RV ocorre na data RDT. Se RDT for uma data de cupão, i = N-1 para essa data.
            # Encontrar o índice 'N' correspondente a RDT
            n_periods = 0
            temp_dt = next_coupon_date
            i = 0
            while temp_dt <= rdt:
                 n_periods = i + w # Expoente de desconto para RDT
                 if temp_dt == rdt: break
                 i += 1
                 # Avançar para a próxima data de cupão teórica
                 year, month = temp_dt.year, temp_dt.month
                 interval_months = 12 / coupons_per_year
                 new_month_float = month + interval_months
                 new_year = year
                 while new_month_float > 12:
                      new_month_float -= 12
                      new_year += 1
                 new_month = int(new_month_float)
                 day = temp_dt.day
                 try:
                      last_day_of_new_month = pd.Timestamp(year=new_year, month=new_month, day=1).days_in_month
                      day = min(day, last_day_of_new_month)
                      temp_dt = datetime.date(new_year, new_month, day)
                 except ValueError: break # Parar se data inválida
                 # Limite segurança
                 if i > 200 * coupons_per_year : break


            if n_periods == 0: # Se RDT <= next_coupon_date
                  n_periods = w # Descontar apenas fração

            redemption_amount = rv_percent / 100.0 * par_value
            pv_redemption = redemption_amount * (v ** n_periods)
            pv_total += pv_redemption

            return pv_total # Este é o Preço Sujo (Dirty Price)


        # --- Interface Streamlit ---
        bond_col1, bond_col2, bond_col3 = st.columns(3)

        with bond_col1:
            sdt_b = st.date_input("Data Liquidação (SDT)", value=datetime.date(2006, 6, 12), key="sdt_b_input_full")
            cpn_b = st.number_input("Taxa Cupão Anual (CPN %)", min_value=0.0, value=7.0, format="%.4f", key="cpn_b_input_full")
            rdt_b = st.date_input("Data Reembolso (RDT)", value=datetime.date(2007, 12, 31), key="rdt_b_input_full")

        with bond_col2:
            rv_b = st.number_input("Valor Reembolso (RV %)", min_value=0.0, value=100.0, format="%.2f", help="Percentagem do valor nominal", key="rv_b_input_full")
            # Permitir input de YLD ou PRI dependendo do que se quer calcular
            yld_b_input = st.number_input("Yield Anual (YLD %)", value=8.0, format="%.4f", help="Input para calcular Preço", key="yld_b_input_full")
            pri_b_input = st.number_input("Preço Mercado (PRI %)", value=98.56, format="%.4f", help="Preço Limpo. Input para calcular Yield.", key="pri_b_input_full")


        with bond_col3:
            day_count_b = st.selectbox("Método Dia", ["ACT", "360"], index=1, key="bond_day_count_select_full")
            coupons_per_year_b = st.selectbox("Cupões/Ano", [1, 2], index=1, key="bond_coupons_select_full")
            st.text("Resultados:")
            ai_result_text = st.empty() # Placeholder para AI
            calc_result_text = st.empty() # Placeholder para PRI ou YLD

        # --- Botões de Cálculo ---
        st.divider()
        calc_bond_col1, calc_bond_col2 = st.columns(2)

        # Obter lista de datas de cupão uma vez
        coupon_dates = []
        valid_dates = False
        if sdt_b and rdt_b and sdt_b < rdt_b:
             valid_dates = True
             coupon_dates = get_coupon_dates_list(rdt_b, sdt_b, coupons_per_year_b)
        elif sdt_b and rdt_b and sdt_b >= rdt_b:
             st.warning("SDT deve ser anterior a RDT.")


        if calc_bond_col1.button("Calcular PRI (dado YLD)", key="calc_pri_bond_button"):
             if not valid_dates:
                 st.error("Datas inválidas ou SDT >= RDT.")
             elif yld_b_input is None:
                  st.error("Yield (YLD) deve ser fornecido.")
             else:
                 try:
                     # 1. Calcular Juros Corridos
                     ai_calc = calculate_accrued_interest(sdt_b, cpn_b, coupons_per_year_b, day_count_b, coupon_dates)
                     if ai_calc is not None:
                          ai_result_text.info(f"Juros Corridos (AI) ≈ {ai_calc:.4f} %")
                     else:
                          ai_result_text.warning("AI não pôde ser calculado.")
                          ai_calc = 0 # Assumir 0 se não calculável

                     # 2. Calcular Preço Sujo
                     dirty_price_calc = calculate_bond_price_dirty(yld_b_input, sdt_b, rdt_b, cpn_b, rv_b, coupons_per_year_b, day_count_b, coupon_dates)

                     if dirty_price_calc is not None:
                          # 3. Calcular Preço Limpo (PRI)
                          pri_calc = dirty_price_calc - ai_calc
                          calc_result_text.success(f"Preço Limpo (PRI) ≈ {pri_calc:.4f} %")
                     else:
                          calc_result_text.error("Não foi possível calcular o Preço.")

                 except Exception as e:
                     st.error(f"Erro ao calcular PRI: {e}")
                     import traceback
                     st.error(traceback.format_exc())

        if calc_bond_col2.button("Calcular YLD (dado PRI)", key="calc_yld_bond_button"):
            if not valid_dates:
                st.error("Datas inválidas ou SDT >= RDT.")
            elif pri_b_input is None:
                st.error("Preço Mercado (PRI) deve ser fornecido.")
            else:
                 try:
                     # 1. Calcular Juros Corridos (necessário para a função objetivo)
                     ai_calc = calculate_accrued_interest(sdt_b, cpn_b, coupons_per_year_b, day_count_b, coupon_dates)
                     if ai_calc is None:
                          st.error("Não foi possível calcular AI, necessário para YLD.")
                          # Não continuar sem AI
                     else:
                          ai_result_text.info(f"Juros Corridos (AI) ≈ {ai_calc:.4f} %")

                          # 2. Definir função objetivo para o solver
                          def target_yield_function(yield_rate_annual_decimal, sdt, rdt, cpn, rv, coup_per_yr, day_count, coupon_list, target_clean_price, known_ai):
                              # Yield anual decimal como input
                              dirty_price = calculate_bond_price_dirty(yield_rate_annual_decimal * 100.0, sdt, rdt, cpn, rv, coup_per_yr, day_count, coupon_list)
                              if dirty_price is None:
                                   # Tentar devolver um valor grande para indicar erro ao solver
                                   return 1e10 # Ou raise ValueError?
                              calculated_clean_price = dirty_price - known_ai
                              return calculated_clean_price - target_clean_price

                          # 3. Chamar o solver (Newton)
                          # Estimativa inicial: taxa de cupão ou yield anterior? Usar cupão.
                          initial_yield_guess = cpn_b / 100.0
                          args_for_solver = (sdt_b, rdt_b, cpn_b, rv_b, coupons_per_year_b, day_count_b, coupon_dates, pri_b_input, ai_calc)

                          try:
                              # Usar maxiter e tol para controlo
                              solved_yield_decimal = newton(target_yield_function, initial_yield_guess, args=args_for_solver, tol=1e-6, maxiter=100)
                              solved_yield_percent = solved_yield_decimal * 100.0
                              calc_result_text.success(f"Yield (YLD) ≈ {solved_yield_percent:.4f} %")
                          except (RuntimeError, ValueError) as solver_error:
                               # Tentar Brentq se Newton falhar? Requer bracket.
                               calc_result_text.error(f"Solver não convergiu: {solver_error}. Tente um preço diferente ou verifique parâmetros.")
                          except Exception as general_solver_error:
                               calc_result_text.error(f"Erro inesperado no solver YLD: {general_solver_error}")


                 except Exception as e:
                     st.error(f"Erro ao preparar para calcular YLD: {e}")
                     import traceback
                     st.error(traceback.format_exc())
# --- Aba: Estatística ---
with main_tabs[9]:
    st.header("Análise Estatística")

    stats_tabs = st.tabs(["Explicação", "Calculadora"])

    with stats_tabs[0]:
        st.subheader("Análise de Dados de Uma e Duas Variáveis")
        st.markdown("""
        Esta função permite realizar análises estatísticas em conjuntos de dados de uma ou duas variáveis, incluindo o cálculo de estatísticas descritivas e a aplicação de modelos de regressão.

        **Entrada de Dados:**
        * Introduza os seus dados numa tabela com colunas para X e Y.
        * **Análise 1-Variável:** Introduza os valores na coluna X e a frequência (número de ocorrências) de cada valor na coluna Y. Se todos os valores tiverem frequência 1, pode deixar Y como 1.
        * **Análise 2-Variáveis:** Introduza os pares de dados (x, y) nas colunas X e Y. A frequência (Y para 1-Var) não é usada diretamente nos cálculos de regressão 2-Var (assume-se frequência 1 para cada par).
        * Como referência, a calculadora TI BA II Plus aceita até 50 pontos de dados.

        **Métodos de Análise:**
        * **1-V (One-Variable):** Calcula estatísticas descritivas para uma única variável (usando a coluna X e Y como frequência).
        * **LIN (Linear Regression):** Encontra a linha reta (Y = a + bX) que melhor se ajusta aos dados (X, Y).
        * **Ln (Logarithmic Regression):** Encontra a curva logarítmica (Y = a + b * ln(X)) que melhor se ajusta. Requer que todos os X sejam > 0.
        * **EXP (Exponential Regression):** Encontra a curva exponencial (Y = a * b^X, ou ln(Y) = ln(a) + ln(b)*X) que melhor se ajusta. Requer que todos os Y sejam > 0.
        * **PWR (Power Regression):** Encontra a curva de potência (Y = a * X^b, ou ln(Y) = ln(a) + b*ln(X)) que melhor se ajusta. Requer que todos os X e Y sejam > 0.

        **Resultados Principais:**
        * **n:** Número de pontos de dados (considerando frequências em 1-V).
        * **X̄ / Ȳ (ou v / y):** Média dos valores de X / Y.
        * **Sx / Sy:** Desvio padrão amostral (usa n-1 no denominador).
        * **σx / σy:** Desvio padrão populacional (usa n no denominador).
        * **Σx / Σy:** Soma dos valores de X / Y.
        * **Σx² / Σy²:** Soma dos quadrados dos valores de X / Y.
        * **(Regressão 2-Var):**
            * **a:** Intercepto da regressão.
            * **b:** Inclinação (slope) da regressão.
            * **r:** Coeficiente de correlação (-1 a +1). Mede a força e direção da relação linear (ou linearizada). Valores próximos de 1 ou -1 indicam um bom ajuste.
            * **Σxy:** Soma dos produtos X*Y.

        **Previsão (Regressão 2-Var):**
        * **Y' (dado X'):** Prevê o valor de Y para um determinado valor de X (X') usando a equação de regressão calculada.
        * **X' (dado Y'):** Prevê o valor de X que corresponderia a um determinado valor de Y (Y') usando a equação de regressão invertida (quando possível).
        """)

    with stats_tabs[1]:
        st.subheader("Calculadora Estatística")

        # Entrada de Dados
        st.markdown("**Introduza os Dados (X, Y):**")
        st.caption("Para análise 1-Var, coloque os valores em X e as suas frequências em Y.")

        if 'stats_data' not in st.session_state:
             st.session_state.stats_data = pd.DataFrame([
                 {'X': 1, 'Y': 10}, {'X': 2, 'Y': 12}, {'X': 3, 'Y': 15},
                 {'X': 4, 'Y': 18}, {'X': 5, 'Y': 20},
             ])

        edited_stats_df = st.data_editor(
            st.session_state.stats_data,
            num_rows="dynamic",
            column_config={
                "X": st.column_config.NumberColumn(format="%.4f", required=True),
                "Y": st.column_config.NumberColumn(format="%.4f", required=True, help="Valor Y (2-Var) ou Frequência (1-Var)")
            },
            key="stats_editor_main"
        )
        st.session_state.stats_data = edited_stats_df # Atualizar estado

        # Seleção do Método
        stat_method = st.selectbox(
            "Método de Análise Estatística",
            ["1-V", "LIN", "Ln", "EXP", "PWR"],
            index=1, # Default para LIN
            key="stat_method_select"
        )

        # Calcular Estatísticas
        if st.button("Calcular Estatísticas", key="stat_calc_button"):
            # Usar estado atualizado
            data = st.session_state.stats_data.copy().dropna() # Remover linhas com NaN
            results = {}
            error_msg = None

            if data.empty:
                 error_msg = "Não há dados válidos para analisar."

            try:
                if not error_msg:
                    n_total = 0
                    if stat_method == "1-V":
                        if not pd.api.types.is_numeric_dtype(data['Y']):
                             error_msg = "Erro (1-V): Coluna Y (frequência) deve ser numérica."
                        elif not data['Y'].ge(0).all():
                            error_msg = "Erro (1-V): Frequências (Y) devem ser não-negativas."
                        elif data['Y'].sum() <= 0:
                             error_msg = "Erro (1-V): Soma das frequências (Y) deve ser positiva."
                        else:
                            try:
                                 # Arredondar frequências para inteiros para usar repeat
                                 freqs = data['Y'].round().astype(int)
                                 if not freqs.ge(0).all(): raise ValueError("Frequências negativas após arredondar.")
                                 x_data_expanded = np.repeat(data['X'].values, freqs.values)
                                 n_total = len(x_data_expanded)
                            except (ValueError, TypeError) as e_rep:
                                 error_msg = f"Erro (1-V) ao processar frequências: {e_rep}"
                                 x_data_expanded = np.array([]) # Esvaziar para evitar erros abaixo

                            if n_total > 0 and not error_msg:
                                 results['n'] = n_total
                                 results['Mean X'] = np.mean(x_data_expanded)
                                 results['Sum X'] = np.sum(x_data_expanded)
                                 results['Sum X2'] = np.sum(x_data_expanded**2)
                                 if n_total > 1: results['Sx'] = np.std(x_data_expanded, ddof=1)
                                 else: results['Sx'] = 0
                                 results['σx'] = np.std(x_data_expanded, ddof=0)
                            elif not error_msg:
                                 error_msg = "Erro (1-V): Não há dados válidos após considerar frequências."

                    else: # Métodos 2-Variáveis
                        x_data = data['X'].astype(float).values
                        y_data = data['Y'].astype(float).values
                        n_total = len(x_data)
                        results['n'] = n_total

                        if n_total < 2:
                            error_msg = f"Erro ({stat_method}): São necessários pelo menos 2 pontos de dados para regressão."
                        else:
                            results['Mean X'] = np.mean(x_data)
                            results['Mean Y'] = np.mean(y_data)
                            results['Sum X'] = np.sum(x_data)
                            results['Sum Y'] = np.sum(y_data)
                            results['Sum X2'] = np.sum(x_data**2)
                            results['Sum Y2'] = np.sum(y_data**2)
                            results['Sum XY'] = np.sum(x_data * y_data)
                            results['Sx'] = np.std(x_data, ddof=1)
                            results['Sy'] = np.std(y_data, ddof=1)
                            results['σx'] = np.std(x_data, ddof=0)
                            results['σy'] = np.std(y_data, ddof=0)

                            x_reg, y_reg = x_data, y_data
                            valid_transform = True
                            try:
                                if stat_method == "Ln":
                                    if not (x_data > 0).all(): raise ValueError("Todos os X devem ser > 0.")
                                    x_reg = np.log(x_data)
                                elif stat_method == "EXP":
                                    if not (y_data > 0).all(): raise ValueError("Todos os Y devem ser > 0.")
                                    y_reg = np.log(y_data)
                                elif stat_method == "PWR":
                                     if not ((x_data > 0).all() and (y_data > 0).all()): raise ValueError("Todos X e Y devem ser > 0.")
                                     x_reg = np.log(x_data)
                                     y_reg = np.log(y_data)
                            except ValueError as ve:
                                error_msg = f"Erro ({stat_method}): {ve}"
                                valid_transform = False
                            except Exception as e_log:
                                error_msg = f"Erro ({stat_method}) na transformação Log: {e_log}"
                                valid_transform = False


                            if valid_transform:
                                # Verificar constantes após transformação
                                if np.allclose(x_reg, x_reg[0]) or np.allclose(y_reg, y_reg[0]):
                                      error_msg = f"Erro ({stat_method}): Os dados (possivelmente transformados) são constantes."
                                else:
                                    try:
                                        # Usar nan_policy='omit' para ignorar NaNs se houver
                                        slope, intercept, r_value, p_value, std_err = stats.linregress(x_reg, y_reg)

                                        if stat_method == "EXP":
                                            results['a (intercept)'] = np.exp(intercept)
                                            results['b (slope)'] = np.exp(slope)
                                        elif stat_method == "PWR":
                                            results['a (intercept)'] = np.exp(intercept)
                                            results['b (slope)'] = slope
                                        else: # LIN, Ln
                                            results['a (intercept)'] = intercept
                                            results['b (slope)'] = slope

                                        results['r (correlation)'] = r_value
                                        results['_raw_slope'] = slope
                                        results['_raw_intercept'] = intercept

                                    except ValueError as ve:
                                        error_msg = f"Erro ({stat_method}) na regressão: {ve}. Verifique dados."
                                    except Exception as e_reg:
                                        error_msg = f"Erro ({stat_method}) inesperado na regressão: {e_reg}."

            except Exception as e:
                 error_msg = f"Erro geral no processamento dos dados: {e}"


            # Mostrar Resultados ou Erro
            if error_msg:
                st.error(error_msg)
                st.session_state.stat_results = None
            elif results:
                 st.success(f"Cálculo Estatístico ({stat_method}) Concluído!")
                 st.session_state.stat_results = results
                 st.session_state.stat_method = stat_method

                 res_col1, res_col2 = st.columns(2)
                 with res_col1:
                    st.metric("n", results.get('n', 'N/A'))
                    if 'Mean X' in results: st.metric("Média X", f"{results['Mean X']:.4f}")
                    if 'Sx' in results: st.metric("Sx", f"{results['Sx']:.4f}")
                    if 'σx' in results: st.metric("σx", f"{results['σx']:.4f}")
                    if 'Sum X' in results: st.metric("Σx", f"{results['Sum X']:.4f}")
                    if 'Sum X2' in results: st.metric("Σx²", f"{results['Sum X2']:.4f}")

                 with res_col2:
                     if stat_method != "1-V":
                        if 'Mean Y' in results: st.metric("Média Y", f"{results['Mean Y']:.4f}")
                        if 'Sy' in results: st.metric("Sy", f"{results['Sy']:.4f}")
                        if 'σy' in results: st.metric("σy", f"{results['σy']:.4f}")
                        if 'Sum Y' in results: st.metric("Σy", f"{results['Sum Y']:.4f}")
                        if 'Sum Y2' in results: st.metric("Σy²", f"{results['Sum Y2']:.4f}")
                        if 'Sum XY' in results: st.metric("Σxy", f"{results['Sum XY']:.4f}")

                 if stat_method != "1-V" and 'a (intercept)' in results:
                      st.divider()
                      st.subheader(f"Regressão ({stat_method})")
                      reg_col1, reg_col2, reg_col3 = st.columns(3)
                      reg_col1.metric("a", f"{results['a (intercept)']:.4f}")
                      reg_col2.metric("b", f"{results['b (slope)']:.4f}")
                      reg_col3.metric("r", f"{results['r (correlation)']:.4f}")

                      equation = "Equação não disponível"
                      a_val = results['a (intercept)']
                      b_val = results['b (slope)']
                      if stat_method == "LIN": equation = f"Y \\approx {a_val:.4f} + ({b_val:.4f}) \\times X"
                      elif stat_method == "Ln": equation = f"Y \\approx {a_val:.4f} + ({b_val:.4f}) \\times \\ln(X)"
                      elif stat_method == "EXP": equation = f"Y \\approx {a_val:.4f} \\times ({b_val:.4f}) ^ X"
                      elif stat_method == "PWR": equation = f"Y \\approx {a_val:.4f} \\times X ^ ({b_val:.4f})"
                      st.latex(equation)


        # Secção de Previsão
        if 'stat_results' in st.session_state and st.session_state.stat_results and st.session_state.get('stat_method') != "1-V":
            st.divider()
            st.subheader(f"Previsão ({st.session_state.stat_method})")
            predict_col1, predict_col2 = st.columns(2)

            with predict_col1:
                x_prime = st.number_input("Valor X' para prever Y'", format="%.4f", value=6.0, key="x_prime_input")
                if st.button("Prever Y' (dado X')", key="predict_y_button"):
                    res = st.session_state.stat_results
                    method = st.session_state.stat_method
                    y_pred = None
                    valid_pred = True
                    error_pred = None
                    try:
                        raw_a = res['_raw_intercept']
                        raw_b = res['_raw_slope']
                        a_adj = res['a (intercept)'] # 'a' ajustado para EXP/PWR
                        b_adj = res['b (slope)']   # 'b' ajustado para EXP/PWR

                        if method == "LIN": y_pred = a_adj + b_adj * x_prime
                        elif method == "Ln":
                             if x_prime <= 0: error_pred = "X' deve ser > 0."; valid_pred = False
                             else: y_pred = a_adj + b_adj * np.log(x_prime)
                        elif method == "EXP": y_pred = a_adj * (b_adj ** x_prime)
                        elif method == "PWR":
                             if x_prime <= 0: error_pred = "X' deve ser > 0."; valid_pred = False
                             else: y_pred = a_adj * (x_prime ** b_adj)

                        if valid_pred and y_pred is not None: st.success(f"Y' ≈ {y_pred:.4f}")
                        elif error_pred: st.error(error_pred)
                        else: st.warning("Não foi possível prever Y'.")
                    except Exception as e: st.error(f"Erro previsão Y': {e}")

            with predict_col2:
                y_prime = st.number_input("Valor Y' para prever X'", format="%.4f", value=22.0, key="y_prime_input")
                if st.button("Prever X' (dado Y')", key="predict_x_button"):
                    res = st.session_state.stat_results
                    method = st.session_state.stat_method
                    x_pred = None
                    valid_pred = True
                    error_pred = None
                    try:
                        raw_a = res['_raw_intercept']
                        raw_b = res['_raw_slope']
                        a_adj = res['a (intercept)']
                        b_adj = res['b (slope)']

                        if abs(raw_b if method in ["LIN", "Ln"] else b_adj) < 1e-10: # Verificar inclinação relevante
                             error_pred = "Inclinação (b) ≈ 0. Não é possível prever X'."; valid_pred = False

                        if valid_pred:
                            if method == "LIN": x_pred = (y_prime - a_adj) / b_adj
                            elif method == "Ln":
                                # Y = a + b*ln(X) => X = exp((Y - a) / b)
                                x_pred = np.exp((y_prime - a_adj) / b_adj)
                            elif method == "EXP":
                                # Y = a * b^X => b^X = Y/a => X*ln(b) = ln(Y/a) => X = ln(Y/a) / ln(b)
                                if y_prime <= 0 or a_adj <= 0 or b_adj <= 0 or b_adj == 1:
                                     error_pred = "Inputs inválidos para EXP (Y'>0, a>0, b>0, b!=1)."; valid_pred = False
                                else: x_pred = np.log(y_prime / a_adj) / np.log(b_adj)
                            elif method == "PWR":
                                # Y = a * X^b => X^b = Y/a => b*ln(X) = ln(Y/a) => ln(X) = ln(Y/a)/b => X = exp(ln(Y/a)/b)
                                if y_prime <= 0 or a_adj <= 0:
                                     error_pred = "Inputs inválidos para PWR (Y'>0, a>0)."; valid_pred = False
                                elif abs(b_adj) < 1e-10:
                                     error_pred = "Inclinação (b) ≈ 0. Não é possível prever X'."; valid_pred = False
                                else: x_pred = np.exp(np.log(y_prime / a_adj) / b_adj)


                        if valid_pred and x_pred is not None: st.success(f"X' ≈ {x_pred:.4f}")
                        elif error_pred: st.error(error_pred)
                        else: st.warning("Não foi possível prever X'.")

                    except Exception as e: st.error(f"Erro previsão X': {e}")


## --- Rodapé ---
st.sidebar.info(
    """
    **Autor:** Luís Simões da Cunha (2025)
    **Licença:** [CC BY-NC 4.0](http://creativecommons.org/licenses/by-nc/4.0/)
    """
)

# Adicionar disclaimer breve ao caption
current_time_str = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
st.sidebar.caption(
    f"Data Atual: {current_time_str} | "
    "AVISO: Ferramenta Educacional. Sem garantias. Use por sua conta e risco."
)