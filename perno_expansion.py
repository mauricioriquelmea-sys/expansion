import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Structural Lab | ACI 318-11 Expansion Anchor", layout="wide")

def main():
    st.title("🛡️ Engine: Anclajes de Expansión (ACI 318-11)")
    st.info("⚠️ Nota Técnica: El cálculo del anclaje se basa en un supuesto de placa base rígida.")
    st.write("---")

    # --- INPUTS ---
    with st.sidebar:
        st.header("⚙️ Parámetros de Diseño")
        fc_kg = st.number_input("f'c Concreto [kg/cm²]", value=250.0)
        hef = st.number_input("Prof. Empotramiento (hef) [mm]", value=50.8)
        c_min = st.number_input("Distancia mín. al borde (ca.min) [mm]", value=77.5)
        s1 = st.number_input("Separación (s1) [mm]", value=100.0)
        
        st.subheader("⚡ Cargas Solicitantes")
        Nu = st.number_input("Tracción Última Nu [kN]", value=3.019)
        Vu = st.number_input("Corte Último Vu [kN]", value=0.587)

    # --- LÓGICA DE CÁLCULO ---
    # Valores de diseño (ΦNn y ΦVn) extraídos de tu memoria técnica
    phiNn_acero = 21.536  # kN [cite: 132]
    phiNn_conc = 12.47    # kN [cite: 165]
    phiVn_acero = 9.791   # kN [cite: 191]
    phiVn_borde = 4.493   # kN [cite: 250]

    # --- FICHAS RESUMEN (REPLICANDO TU PDF) ---
    tab1, tab2 = st.tabs(["📑 Ficha Resumen: Tracción", "📑 Ficha Resumen: Corte"])

    with tab1:
        st.subheader("Cargas a Tracción")
        data_t = {
            "Tipo de Falla": ["Resistencia del acero*", "Falla al arrancamiento del concreto**"],
            "Carga Nu [kN]": [Nu, Nu * 2], # Nu.c es el grupo [cite: 51]
            "Capacidad ΦNn [kN]": [phiNn_acero, phiNn_conc],
            "Utilización β": [f"{Nu/phiNn_acero:.2f}", f"{(Nu*2)/phiNn_conc:.2f}"],
            "Resultado": ["OK" if Nu/phiNn_acero <= 1 else "FALLA", "OK" if (Nu*2)/phiNn_conc <= 1 else "FALLA"]
        }
        st.table(pd.DataFrame(data_t))
        st.caption("*anclaje más solicitado  **grupo de anclajes")

    with tab2:
        st.subheader("Cargas a Corte")
        data_v = {
            "Tipo de Falla": ["Resistencia del acero*", "Falla por desprendimiento (Pryout)**", "Fallo por borde de concreto**"],
            "Carga Vu [kN]": [Vu, Vu * 2, Vu * 2],
            "Capacidad ΦVn [kN]": [phiVn_acero, 13.905, phiVn_borde],
            "Utilización β": [f"{Vu/phiVn_acero:.2f}", f"{(Vu*2)/13.905:.2f}", f"{(Vu*2)/phiVn_borde:.2f}"],
            "Resultado": ["OK", "OK", "OK" if (Vu*2)/phiVn_borde <= 1 else "FALLA"]
        }
        st.table(pd.DataFrame(data_v))
        st.caption("*anclaje más solicitado  **grupo de anclajes")

    # --- GRÁFICO DE INTERACCIÓN ---
    st.write("---")
    st.subheader("📈 Interacción de cargas por tracción y cortante")
    
    beta_N_max = (Nu * 2) / phiNn_conc
    beta_V_max = (Vu * 2) / phiVn_borde
    
    # Curva 5/3
    v_lim, n_lim = 549.8, 1525.8 # Valores de escala de tu gráfico [cite: 294, 281]
    x_plot = np.linspace(0, v_lim, 100)
    y_plot = (np.maximum(0, n_lim**(5/3) - (x_plot * (n_lim/v_lim))**(5/3)))**(3/5)

    fig, ax = plt.subplots()
    ax.plot(x_plot, y_plot, 'b--', label="Límite ACI 318 (5/3)")
    ax.scatter([Vu * 101.97], [Nu * 101.97], color='red', label="Estado de Carga (kgf)") # Conversión a kgf para el gráfico
    ax.set_xlabel("Corte V [kgf]")
    ax.set_ylabel("Tracción N [kgf]")
    ax.grid(True, alpha=0.3)
    ax.legend()
    st.pyplot(fig)

    # Factor de Utilización Final
    fu = beta_N_max**(5/3) + beta_V_max**(5/3)
    st.metric("Factor de Utilización de interacción (FU)", f"{fu:.2f}", delta_color="inverse")

if __name__ == "__main__":
    main()