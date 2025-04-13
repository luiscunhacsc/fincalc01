import streamlit as st
import numpy as np
import numpy_financial as npf
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from scipy import stats
from scipy.optimize import newton

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA (Mobile-Friendly e Pedagógica)
# =============================================================================
st.set_page_config(
    layout="centered",  # Layout centralizado para melhor visualização em dispositivos móveis
    page_title="Calculadora Financeira Educacional (Mobile)"
)

st.title("Calculadora Financeira Educacional")
st.caption("Uma ferramenta interativa para aprender conceitos financeiros passo a passo.")

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def plot_amortization(schedule_df):
    """
    Gera um gráfico simples do saldo devedor ao longo dos períodos.
    Este gráfico ajuda a visualizar como cada pagamento abate o saldo devedor.
    """
    fig, ax = plt.subplots()
    ax.plot(schedule_df['Período'], schedule_df['Saldo Final'], marker='o', linestyle='-')
    ax.set_xlabel("Período")
    ax.set_ylabel("Saldo Devedor (€)")
    ax.set_title("Evolução do Saldo Devedor")
    ax.grid(True)

    # Formatar eixo Y com símbolo de euro
    from matplotlib.ticker import FuncFormatter
    def currency_formatter(x, pos):
        return f'€{x:,.2f}'
    ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))
    st.pyplot(fig)

def calculate_breakeven(known_vars):
    """
    Calcula a variável faltante no ponto de equilíbrio (Breakeven).
    Exemplo de entrada:
        {'FC': 3000, 'VC': 15, 'PFT': 0, 'P': 20, 'Q': None, 'Target': 'Q'}
    Retorna o valor calculado ou uma mensagem de erro se algum input estiver incorreto.
    """
    target = known_vars['Target']
    try:
        p = known_vars['P']
        vc = known_vars['VC']
        fc = known_vars['FC']
        pft = known_vars['PFT']
        q = known_vars['Q']

        if target == 'Q':
            margin_contribution = p - vc
            if margin_contribution <= 0:
                return "Erro: Preço (P) deve ser maior que Custo Variável (VC)."
            result = (fc + pft) / margin_contribution
        elif target == 'PFT':
            result = ( (p - vc) * q ) - fc
        elif target == 'FC':
            result = ( (p - vc) * q ) - pft
        elif target == 'P':
            if q <= 0:
                return "Erro: Quantidade (Q) deve ser > 0."
            result = (fc + (vc * q) + pft) / q
        elif target == 'VC':
            if q <= 0:
                return "Erro: Quantidade (Q) deve ser > 0."
            result = ((p * q) - fc - pft) / q
        else:
            return "Erro: Variável alvo ('Target') desconhecida."
        return result
    except ZeroDivisionError:
         return f"Erro: Divisão por zero ao calcular {target}."
    except Exception as e:
         return f"Erro inesperado ao calcular {target}: {e}"

# =============================================================================
# Interface: Abas principais (Cada aba corresponde a uma funcionalidade)
# =============================================================================

main_tabs = st.tabs([
    "Introdução",
    "TVM & Amortização",
    "Fluxo de Caixa (NPV & IRR)",
    "Conversão de Taxas",
    "Margem de Lucro",
    "Breakeven",
    "Depreciação",
    "Datas",
    "Obrigações",
    "Estatística"
])

# =============================================================================
# Aba 0: Introdução
# =============================================================================
with main_tabs[0]:
    st.header("Bem-vindo!")
    st.warning(
        """
        ### Aviso Importante
        **Esta ferramenta foi desenvolvida para fins educacionais**: os cálculos são uma aproximação dos métodos utilizados em calculadoras financeiras.
        **Sem Garantias:** os resultados apresentados não substituem uma análise profissional.
        """
    )
    st.markdown(
        """
        Neste aplicativo, você encontrará diversas ferramentas para aprender como funcionam cálculos de:
        - Valor do Dinheiro no Tempo (TVM) e Amortização
        - Fluxo de Caixa (NPV e IRR)
        - Conversão de Taxas de Juro
        - Cálculo de Margem de Lucro e Ponto de Equilíbrio
        - Depreciação de Ativos
        - Cálculo de Datas
        - Análise de Obrigações
        - Estatística aplicada
        ---
        Escolha a aba desejada e explore os exemplos e explicações disponíveis. Boa aprendizagem!
        """
    )

# =============================================================================
# Aba 1: TVM & Amortização
# =============================================================================
with main_tabs[1]:
    st.header("Valor do Dinheiro no Tempo (TVM) e Amortização")
    st.subheader("Explicação Pedagógica")
    with st.expander("Clique para ler uma explicação detalhada sobre TVM"):
        st.markdown(
            """
            **Valor do Dinheiro no Tempo (TVM):** O princípio que afirma que um euro hoje tem mais valor do que um euro amanhã, pois pode ser investido para render juros.  
            **Variáveis importantes:**
            - **N:** Número de períodos.
            - **I/Y:** Taxa de juro anual.
            - **PV:** Valor presente (investimento ou empréstimo).
            - **PMT:** Pagamento periódico.
            - **FV:** Valor futuro ao final dos períodos.
            - **P/Y e C/Y:** Número de pagamentos e composições por ano.
            """
        )
    st.subheader("Calculadora TVM")
    with st.form("TVM_Calc"):
        n = st.number_input("N (Número de Períodos)", min_value=1, value=360, help="Ex: 30 anos x 12 meses")
        i_y = st.number_input("I/Y (Taxa de Juro Anual %)", min_value=0.0, value=5.5, format="%.4f")
        pv = st.number_input("PV (Valor Presente)", value=75000.0, format="%.2f", help="Valor positivo se receber; negativo se pagar")
        pmt = st.number_input("PMT (Pagamento Periódico)", value=-425.84, format="%.2f")
        fv = st.number_input("FV (Valor Futuro)", value=0.0, format="%.2f")
        p_y = st.number_input("P/Y (Pagamentos/ano)", min_value=1, value=12)
        c_y = st.number_input("C/Y (Composições/ano)", min_value=1, value=p_y, help="Normalmente igual a P/Y")
        pmt_mode = st.radio("Modo de Pagamento", options=["END", "BGN"], index=0, help="END = fim; BGN = início")
        submitted = st.form_submit_button("Calcular TVM")
    if submitted:
        when = 'begin' if pmt_mode == "BGN" else 'end'
        try:
            # Para calcular N, usamos a taxa ajustada conforme a periodicidade de pagamento
            rate_for_nper = (i_y / 100) / p_y
            result_N = npf.nper(rate_for_nper, pmt, pv, fv, when)
            st.success(f"Calculado: N = {result_N:.4f} períodos")
            # Aqui você pode armazenar o resultado em session_state se desejar para outras funções
        except Exception as e:
            st.error(f"Erro ao calcular TVM: {e}")

    st.subheader("Amortização")
    with st.expander("Clique para ver a tabela de amortização"):
        st.markdown(
            """
            A tabela de amortização mostra como cada pagamento é dividido entre juros e principal, e como o saldo devedor evolui.
            Basta informar o intervalo de períodos para ver os detalhes.
            """
        )
        if st.button("Gerar Tabela de Amortização"):
            try:
                schedule = []
                current_balance = pv  # Valor inicial
                rate_per_period = (i_y / 100) / p_y
                for period in range(1, int(n)+1):
                    interest_payment = current_balance * rate_per_period
                    principal_payment = pmt - interest_payment
                    new_balance = current_balance + principal_payment
                    schedule.append({
                        'Período': period,
                        'Saldo Inicial': current_balance,
                        'Juros': abs(interest_payment),
                        'Principal': abs(principal_payment),
                        'Saldo Final': max(0, new_balance)
                    })
                    current_balance = new_balance
                    if current_balance <= 0:
                        break
                if schedule:
                    df_schedule = pd.DataFrame(schedule)
                    st.dataframe(df_schedule.style.format({
                        'Saldo Inicial': '{:,.2f} €',
                        'Juros': '{:,.2f} €',
                        'Principal': '{:,.2f} €',
                        'Saldo Final': '{:,.2f} €'
                    }))
                    st.subheader("Gráfico da Evolução do Saldo")
                    plot_amortization(df_schedule)
                else:
                    st.error("Não foi possível gerar a tabela.")
            except Exception as e:
                st.error(f"Erro na geração da tabela: {e}")

# =============================================================================
# Aba 2: Fluxo de Caixa (NPV & IRR)
# =============================================================================
with main_tabs[2]:
    st.header("Fluxo de Caixa (NPV & IRR)")
    with st.expander("Explicação sobre NPV e IRR"):
        st.markdown(
            """
            **NPV (Valor Atual Líquido):** A soma dos fluxos de caixa descontados ao presente.  
            **IRR (Taxa Interna de Retorno):** A taxa que torna o NPV igual a zero.  
            Utilize estes indicadores para avaliar a viabilidade de projetos.
            """
        )
    with st.form("CashFlow_Calc"):
        st.markdown("**Insira os fluxos de caixa:**")
        cf0 = st.number_input("CF0 (Investimento Inicial)", value=-7000.0, format="%.2f", help="Normalmente negativo")
        # Para simplificar, usaremos uma tabela inicial com três fluxos – o usuário pode editar.
        default_cf = pd.DataFrame([
            {"Fluxo": 3000.0, "Frequência": 1},
            {"Fluxo": 5000.0, "Frequência": 4},
            {"Fluxo": 4000.0, "Frequência": 1}
        ])
        cf_data = st.data_editor("Tabela de Fluxos", default_cf, num_rows="dynamic")
        discount_rate = st.number_input("Taxa de Desconto (%)", value=20.0, format="%.4f")
        submitted_cf = st.form_submit_button("Calcular NPV & IRR")
    if submitted_cf:
        # Construir a lista de fluxos completa
        cash_flows = [cf0]
        valid_input = True
        try:
            for index, row in cf_data.iterrows():
                cf_val = float(row["Fluxo"])
                freq = int(row["Frequência"])
                if freq < 1:
                    st.error(f"Erro na linha {index+1}: Frequência deve ser >= 1.")
                    valid_input = False
                    break
                cash_flows.extend([cf_val] * freq)
            if valid_input:
                # NPV
                npv_result = npf.npv(discount_rate/100, cash_flows)
                st.success(f"NPV = {npv_result:,.2f}")
                # IRR – cuidado com fluxos sem mudança de sinal
                if sum(1 for i in range(len(cash_flows)-1) if cash_flows[i]*cash_flows[i+1] < 0) == 0:
                    st.error("Erro: Fluxos de caixa sem mudança de sinal – IRR não pode ser calculado.")
                else:
                    irr_result = npf.irr(cash_flows)
                    if np.isnan(irr_result):
                        st.error("Erro: IRR não convergiu. Verifique os fluxos.")
                    else:
                        st.success(f"IRR = {irr_result * 100:,.4f} %")
        except Exception as e:
            st.error(f"Erro no processamento dos fluxos: {e}")

# =============================================================================
# Aba 3: Conversão de Taxas
# =============================================================================
with main_tabs[3]:
    st.header("Conversão de Taxas de Juro")
    with st.expander("Entenda a conversão"):
        st.markdown(
            """
            **Nominal vs. Efetiva:**  
            - **Taxa Nominal:** A taxa declarada sem levar em consideração a capitalização.
            - **Taxa Efetiva:** A taxa real considerando a frequência de capitalização.
            Fórmulas:
            - EFF = (1 + NOM/CY)^(CY) - 1  
            - NOM = CY * ((1 + EFF)^(1/CY) - 1)
            """
        )
    with st.form("Conversion_Calc"):
        nom = st.number_input("NOM (Taxa Nominal %)", min_value=0.0, value=15.0, format="%.4f")
        c_y_conv = st.number_input("C/Y (Capitalizações por Ano)", min_value=1, value=4)
        # Escolha: converter NOM para EFF ou vice-versa
        conversion_option = st.selectbox("Converter para", options=["EFF (Taxa Efetiva)", "NOM (Taxa Nominal)"])
        if conversion_option == "EFF (Taxa Efetiva)":
            submitted_conv = st.form_submit_button("Calcular EFF")
        else:
            eff = st.number_input("EFF (Taxa Efetiva %)", min_value=0.0, value=15.87, format="%.4f")
            submitted_conv = st.form_submit_button("Calcular NOM")
    if submitted_conv:
        try:
            if conversion_option == "EFF (Taxa Efetiva)":
                eff_calc = ((1 + (nom / 100) / c_y_conv)**c_y_conv - 1) * 100
                st.success(f"Taxa Efetiva = {eff_calc:.4f} %")
            else:
                base = 1 + eff / 100
                if base <= 0:
                    st.error("Base negativa para cálculo. Verifique os inputs.")
                else:
                    nom_calc = c_y_conv * (base**(1.0/c_y_conv) - 1) * 100
                    st.success(f"Taxa Nominal = {nom_calc:.4f} %")
        except Exception as e:
            st.error(f"Erro na conversão: {e}")

# =============================================================================
# Aba 4: Margem de Lucro
# =============================================================================
with main_tabs[4]:
    st.header("Margem de Lucro")
    with st.expander("Explicação"):
        st.markdown(
            """
            A margem de lucro é a diferença percentual entre o preço de venda e o custo.  
            Fórmula: MAR = ((SEL - CST) / SEL) * 100  
            Isso permite avaliar a lucratividade de um produto.
            """
        )
    with st.form("Margin_Calc"):
        cst = st.number_input("Custo (CST)", min_value=0.0, value=100.0, format="%.2f")
        sel = st.number_input("Preço de Venda (SEL)", min_value=0.0, value=125.0, format="%.2f")
        mar_input = st.number_input("Margem (MAR %) [Se desejar calcular outra variável, deixe em branco]", format="%.2f", value=20.0)
        calculation_choice = st.selectbox("Calcular", ["CST", "SEL", "MAR"])
        submitted_margin = st.form_submit_button("Calcular")
    if submitted_margin:
        try:
            if calculation_choice == "CST":
                if sel <= 0:
                    st.error("Preço de Venda deve ser positivo.")
                else:
                    result = sel * (1 - mar_input/100)
                    st.success(f"Custo (CST) = {result:.2f}")
            elif calculation_choice == "SEL":
                if abs(1 - mar_input/100) < 1e-9:
                    st.error("Margem não pode ser 100%")
                else:
                    result = cst / (1 - mar_input/100)
                    st.success(f"Preço de Venda (SEL) = {result:.2f}")
            else:  # Calcular MAR
                if sel == 0:
                    st.error("Preço de Venda não pode ser zero.")
                else:
                    result = ((sel - cst) / sel) * 100
                    st.success(f"Margem (MAR) = {result:.2f} %")
        except Exception as e:
            st.error(f"Erro no cálculo: {e}")

# =============================================================================
# Aba 5: Breakeven (Ponto de Equilíbrio)
# =============================================================================
with main_tabs[5]:
    st.header("Ponto de Equilíbrio (Breakeven)")
    with st.expander("Entenda o conceito"):
        st.markdown(
            """
            O ponto de equilíbrio é o volume de vendas em que os custos totais (fixos e variáveis) são iguais à receita.
            Fórmula: Q = (FC + PFT) / (P - VC)
            Onde:
            - FC: Custos Fixos
            - VC: Custo Variável por Unidade
            - P: Preço por Unidade
            - PFT: Lucro desejado (0 para breakeven exato)
            """
        )
    with st.form("Breakeven_Calc"):
        fc = st.number_input("Custos Fixos (FC)", min_value=0.0, value=3000.0, format="%.2f")
        vc = st.number_input("Custo Variável por Unidade (VC)", min_value=0.0, value=15.0, format="%.2f")
        p  = st.number_input("Preço por Unidade (P)", min_value=0.0, value=20.0, format="%.2f")
        pft = st.number_input("Lucro Desejado (PFT)", value=0.0, format="%.2f", help="0 para breakeven exato")
        target_var = st.selectbox("Calcular", options=["Q", "FC", "VC", "P", "PFT"])
        submitted_break = st.form_submit_button("Calcular")
    if submitted_break:
        # Os inputs que não serão calculados precisam ser passados; para o alvo, passamos None
        inputs = {"FC": fc, "VC": vc, "P": p, "PFT": pft, "Q": None, "Target": target_var}
        result = calculate_breakeven(inputs)
        if isinstance(result, str):
            st.error(result)
        else:
            st.success(f"{target_var} = {result:.2f}")

# =============================================================================
# Aba 6: Depreciação
# =============================================================================
with main_tabs[6]:
    st.header("Depreciação de Ativos")
    with st.expander("Conceitos-chave"):
        st.markdown(
            """
            A depreciação representa a redução do valor de um ativo ao longo do tempo.  
            Métodos comuns:
            - **SL (Linha Reta):** (CST - SAL) / LIF.
            - **SYD:** Utiliza a soma dos dígitos dos anos.
            - **DB:** Saldo decrescente, aplicando uma taxa fixa sobre o valor remanescente.
            """
        )
    with st.form("Depreciation_Calc"):
        st.markdown("**Insira os dados do ativo:**")
        method = st.selectbox("Método de Depreciação", options=["SL", "SYD", "DB"])
        lif = st.number_input("Vida Útil (anos)", min_value=1, value=5)
        m01 = st.number_input("Mês Inicial (M01)", min_value=1.0, max_value=12.99, value=1.0, format="%.2f",
                              help="Exemplo: 1 = início de janeiro; 3.5 = meio de março")
        cst = st.number_input("Custo Inicial (CST)", min_value=0.0, value=10000.0, format="%.2f")
        sal = st.number_input("Valor Residual (SAL)", min_value=0.0, value=1000.0, format="%.2f")
        yr = st.number_input("Ano para calcular", min_value=1, max_value=lif+1, value=1, step=1)
        if method == "DB":
            db_factor_percent = st.number_input("Fator DB (%)", min_value=1.0, value=200.0, format="%.1f",
                                                help="Ex: 200 para dobrar a taxa", step=10.0)
            db_factor = db_factor_percent/100.0
        else:
            db_factor = None
        submitted_depr = st.form_submit_button("Calcular Depreciação")
    if submitted_depr:
        try:
            # Para simplificação, usamos o método SL como exemplo básico
            if sal >= cst:
                st.error("Erro: O valor residual não pode ser maior ou igual ao custo.")
            else:
                if method == "SL":
                    annual_dep = (cst - sal) / lif
                    if yr == 1:
                        # Ajuste para o primeiro ano com base no mês inicial
                        first_year_factor = (13 - m01) / 12
                        dep = annual_dep * first_year_factor
                    elif yr == lif+1:
                        # Último ano proporcional
                        last_year_factor = 1 - ((13 - m01) / 12)
                        dep = annual_dep * last_year_factor
                    else:
                        dep = annual_dep
                    rbv = cst - dep * yr  # Simplificação linear
                    st.success(f"Depreciação no ano {yr} = {dep:.2f} €, RBV ≈ {rbv:.2f} €")
                else:
                    st.info("Este exemplo implementa detalhadamente o método SL. Outros métodos ainda estão em desenvolvimento.")
        except Exception as e:
            st.error(f"Erro ao calcular depreciação: {e}")

# =============================================================================
# Aba 7: Datas
# =============================================================================
with main_tabs[7]:
    st.header("Cálculo de Datas")
    with st.expander("Entenda o cálculo de datas"):
        st.markdown(
            """
            Essa ferramenta permite calcular o número de dias entre duas datas (usando métodos ACT ou 360) e,
            a partir disso, determinar uma data futura ou passada.  
            - **ACT:** Conta os dias reais.
            - **360:** Assume 30 dias por mês.
            """
        )
    with st.form("Dates_Calc"):
        dt1 = st.date_input("Data Inicial (DT1)", value=datetime.date(2003, 9, 4))
        dt2 = st.date_input("Data Final (DT2)", value=datetime.date(2003, 11, 1))
        dbd = st.number_input("Dias entre as Datas (DBD)", min_value=0, value=58, step=1)
        method_days = st.selectbox("Método de Contagem", ["ACT", "360"])
        submitted_date = st.form_submit_button("Calcular")
    if submitted_date:
        try:
            if method_days == "ACT":
                delta = dt2 - dt1
                st.success(f"Entre {dt1} e {dt2} há {delta.days} dias (ACT).")
            else:
                # Função days_360 definida abaixo
                def days_360(date1, date2):
                    d1, m1, y1 = date1.day, date1.month, date1.year
                    d2, m2, y2 = date2.day, date2.month, date2.year
                    if d1 == 31: d1 = 30
                    if d2 == 31 and d1 == 30: d2 = 30
                    return (y2 - y1) * 360 + (m2 - m1) * 30 + (d2 - d1)
                st.success(f"Entre {dt1} e {dt2} há {days_360(dt1, dt2)} dias (360).")
        except Exception as e:
            st.error(f"Erro no cálculo: {e}")

# =============================================================================
# Aba 8: Obrigações (Bonds)
# =============================================================================
with main_tabs[8]:
    st.header("Análise de Obrigações")
    with st.expander("O que são obrigações?"):
        st.markdown(
            """
            Obrigações são títulos de dívida. Esta ferramenta permite calcular:
            - **Preço Limpo (PRI):** O valor da obrigação sem os juros corridos.
            - **Yield (YLD):** A taxa de retorno anualizada.
            - **Juros Corridos (AI):** Os juros acumulados até a data de liquidação.
            """
        )
    with st.form("Bonds_Calc"):
        sdt = st.date_input("Data de Liquidação (SDT)", value=datetime.date(2006, 6, 12))
        rdt = st.date_input("Data de Reembolso (RDT)", value=datetime.date(2007, 12, 31))
        cpn = st.number_input("Taxa Cupão (CPN %)", value=7.0, format="%.4f")
        rv = st.number_input("Valor de Reembolso (RV %)", value=100.0, format="%.2f")
        # Para simplificar, o usuário informa yield para calcular preço ou vice-versa:
        calculation_mode = st.selectbox("Calcular", ["Preço (dado Yield)", "Yield (dado Preço)"])
        if calculation_mode == "Preço (dado Yield)":
            yld = st.number_input("Yield Anual (YLD %)", value=8.0, format="%.4f")
        else:
            pri = st.number_input("Preço Limpo (PRI %)", value=98.56, format="%.4f")
        day_count = st.selectbox("Método de Contagem", ["ACT", "360"])
        coupons_per_year = st.selectbox("Número de Cupões/Ano", [1, 2], index=1)
        submitted_bond = st.form_submit_button("Calcular")
    if submitted_bond:
        try:
            # Para simplificação, usamos funções internas abaixo – veja que os cálculos de bonds podem ser complexos.
            # Primeiro, gerar datas de cupão (exemplo simples)
            def get_coupon_dates(rdt, sdt, n):
                dates = []
                interval = int(12 / n)
                current = rdt
                for _ in range(10):
                    dates.append(current)
                    month = current.month - interval
                    year = current.year
                    while month <= 0:
                        month += 12
                        year -= 1
                    current = datetime.date(year, month, current.day)
                return sorted(dates)
            coupon_dates = get_coupon_dates(rdt, sdt, coupons_per_year)
            # Cálculo simplificado de AI:
            if coupon_dates:
                prev_coupon = max([d for d in coupon_dates if d <= sdt], default=sdt)
                next_coupon = min([d for d in coupon_dates if d > sdt], default=rdt)
                days_accrued = (sdt - prev_coupon).days
                period_days = (next_coupon - prev_coupon).days if (next_coupon - prev_coupon).days > 0 else 1
                coupon_amount = (cpn / 100) / coupons_per_year * 100
                AI = (days_accrued / period_days) * coupon_amount
            else:
                AI = 0
            st.info(f"Juros Corridos (AI) ≈ {AI:.4f} %")
            # Se o usuário escolheu calcular Preço dado Yield:
            if calculation_mode == "Preço (dado Yield)":
                # Usando npf.pv como aproximação para calcular o preço limpo
                rate_per_period = (yld / 100) / coupons_per_year
                # Aproximação: número de períodos até reembolso
                n_periods = ((rdt - sdt).days / 365) * coupons_per_year
                pv_coupons = npf.pv(rate_per_period, n_periods, coupon_amount, 0)
                pv_redemption = npf.pv(rate_per_period, n_periods, 0, rv)
                dirty_price = -(pv_coupons + pv_redemption)
                price_clean = dirty_price - AI
                st.success(f"Preço Limpo (PRI) ≈ {price_clean:.4f} %")
            else:
                st.info("Cálculo de Yield a partir do Preço envolve um solver iterativo. Esta funcionalidade está em fase avançada e pode demorar.")
                # Exemplo: use newton para encontrar yield que torna o preço calculado igual ao input.
                def f(yld_guess):
                    rate_pp = yld_guess / 100 / coupons_per_year
                    n_periods = ((rdt - sdt).days / 365) * coupons_per_year
                    pv_val = npf.pv(rate_pp, n_periods, coupon_amount, rv)
                    return -(pv_val) - AI - pri
                initial_guess = cpn  # usar a taxa de cupão como palpite inicial
                solved_yld = newton(f, initial_guess, tol=1e-6, maxiter=100)
                st.success(f"Yield (YLD) ≈ {solved_yld:.4f} %")
        except Exception as e:
            st.error(f"Erro no cálculo da obrigação: {e}")

# =============================================================================
# Aba 9: Estatística
# =============================================================================
with main_tabs[9]:
    st.header("Análise Estatística")
    with st.expander("Conceitos Estatísticos"):
        st.markdown(
            """
            Nesta seção, você pode analisar dados (uma ou duas variáveis), calcular médias, desvios, e fazer regressões.  
            - **1-V:** Usa os dados de X e frequências em Y para calcular estatísticas.
            - **2-V:** Realiza regressão linear (ou transformada) para ajustar uma equação aos dados.
            """
        )
    with st.form("Stats_Calc"):
        st.markdown("**Insira os dados (colunas X e Y):**")
        default_data = pd.DataFrame([
            {"X": 1, "Y": 10},
            {"X": 2, "Y": 12},
            {"X": 3, "Y": 15},
            {"X": 4, "Y": 18},
            {"X": 5, "Y": 20},
        ])
        stats_df = st.data_editor("Dados Estatísticos", default_data, num_rows="dynamic")
        method_stat = st.selectbox("Método", options=["1-V", "LIN", "Ln", "EXP", "PWR"], index=1)
        submitted_stats = st.form_submit_button("Calcular Estatísticas")
    if submitted_stats:
        try:
            results = {}
            if method_stat == "1-V":
                # Expandir dados conforme a frequência informada em Y
                frequencies = stats_df["Y"].round().astype(int)
                x_data = np.repeat(stats_df["X"].values, frequencies.values)
                results['n'] = len(x_data)
                results['Média X'] = np.mean(x_data)
                results['Desvio Padrão (Sx)'] = np.std(x_data, ddof=1) if len(x_data)>1 else 0
            else:
                x_data = stats_df["X"].astype(float).values
                y_data = stats_df["Y"].astype(float).values
                results['n'] = len(x_data)
                results['Média X'] = np.mean(x_data)
                results['Média Y'] = np.mean(y_data)
                slope, intercept, r_value, _, _ = stats.linregress(x_data, y_data)
                results['a (Intercepto)'] = intercept
                results['b (Inclinação)'] = slope
                results['r (Correlação)'] = r_value
            st.success("Cálculo Estatístico Concluído!")
            st.json(results)
        except Exception as e:
            st.error(f"Erro no cálculo estatístico: {e}")

# =============================================================================
# Rodapé
# =============================================================================
st.sidebar.info("""
**Autor:** Luís Simões da Cunha (2025)  
**Licença:** [CC BY-NC 4.0](http://creativecommons.org/licenses/by-nc/4.0/)
""")
st.sidebar.caption(f"Data Atual: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')} | Ferramenta Educacional. Use com responsabilidade.")
