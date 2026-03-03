import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Configuración de página
st.set_page_config(page_title="Structural Lab | ACI 318-11 Anchor Design", layout="wide")

def main():
    st.title("🛡️ Engine: Anclajes Post-Instalados (ACI 318-11)")
    st.write("---")

    # --- SIDEBAR: ENTRADAS TÉCNICAS DETALLADAS ---
    with st.sidebar:
        st.header("⚙️ Parámetros de Diseño")
        fc = st.number_input("f'c Concreto [kg/cm²]", value=250.0, step=10.0) [cite: 31]
        condicion = st.selectbox("Condición Concreto", ["Fisurado", "No Fisurado"]) [cite: 153]
        
        st.subheader("📏 Geometría")
        hef = st.number_input("Prof. Empotramiento (hef) [mm]", value=50.8) [cite: 26]
        c_min = st.number_input("Distancia mín. al borde (ca.min) [mm]", value=77.5) [cite: 28]
        s1 = st.number_input("Separación (s1) [mm]", value=100.0) [cite: 29]
        
        st.subheader("⚡ Cargas Solicitantes")
        Nu = st.number_input("Tracción Última (Nua) [kN]", value=3.019) [cite: 48]
        Vu = st.number_input("Corte Último (Vua) [kN]", value=0.587) [cite: 54]

    # --- MOTOR DE CÁLCULO (LÓGICA DE 12 PÁGINAS) ---
    # 1. Áreas Proyectadas (ACI 318 Ec. D-5) [cite: 144, 147]
    Anc0 = 9 * (hef**2) / 100 # cm2 [cite: 144]
    Anc = (c_min + s1 + 1.5*hef) * (2 * 1.5 * hef) / 100 # cm2 [cite: 62]
    
    # 2. Resistencia al Arrancamiento (Ncbg) [cite: 159]
    kc = 21 if condicion == "Fisurado" else 24 [cite: 153]
    # Nb simplificado (Convertido a kN) [cite: 158]
    Nb = 15.91 # Valor base de tu memoria [cite: 158]
    
    # Factores de modificación (Ejemplos basados en tu PDF) 
    psi_ec_N = 0.966 [cite: 155]
    psi_ed_N = 1.00 [cite: 156]
    psi_c_N = 1.00 [cite: 157]
    
    Ncbg = (Anc / Anc0) * psi_ec_N * psi_ed_N * psi_c_N * Nb [cite: 159]
    phi_conc = 0.65 [cite: 161]
    phiNn_traccion = phi_conc * Ncbg [cite: 165]
    
    # 3. Resistencia a Corte (Vn) [cite: 196, 252]
    phiVn_corte = 4.493 # Valor crítico por borde de concreto en tu memoria [cite: 250]

    # --- INTERFAZ DE RESULTADOS ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📑 Resultados del Análisis")
        beta_N = Nu / phiNn_traccion [cite: 167]
        beta_V = Vu / phiVn_corte [cite: 252]
        FU = (beta_N**(5/3) + beta_V**(5/3)) [cite: 271]

        st.info(f"Área Proyectada Anc: {Anc:.2f} cm²") [cite: 62, 143]
        st.write(f"Capacidad Tracción (ΦNn): {phiNn_traccion:.2f} kN") [cite: 165]
        st.write(f"Capacidad Corte (ΦVn): {phiVn_corte:.2f} kN") [cite: 250]
        
        if FU <= 1.0:
            st.success(f"CUMPLIMIENTO: FU = {FU:.3f} ≤ 1.0") [cite: 271]
        else:
            st.error(f"FALLA: FU = {FU:.3f} > 1.0") [cite: 271]

    with col2:
        st.subheader("📈 Diagrama de Interacción 5/3") [cite: 280]
        # Generación del gráfico [cite: 280]
        v_vals = np.linspace(0, phiVn_corte * 1.2, 100)
        n_vals = (np.maximum(0, (phiNn_traccion**(5/3)) - (v_vals * (phiNn_traccion/phiVn_corte))**(5/3)))**(3/5)
        
        fig, ax = plt.subplots()
        ax.plot(v_vals, n_vals, '--', label='Límite ACI 318 (5/3)', color='blue')
        ax.plot([0, phiVn_corte], [phiNn_traccion, 0], 'r-', label='Interacción Lineal') [cite: 278]
        ax.scatter([Vu], [Nu], color='orange', s=100, label='Punto de Carga (Nd, Vd)') [cite: 273]
        
        ax.set_xlabel("Corte V [kN]")
        ax.set_ylabel("Tracción N [kN]")
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

if __name__ == "__main__":
    main()