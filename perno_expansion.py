import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Configuración de Structural Lab
st.set_page_config(page_title="Pernos de Expansión | ACI 318-11", layout="wide")

def main():
    st.title("🛡️ Engine: Anclajes de Expansión (ACI 318-11)")
    st.write("---")

    # --- ENTRADAS TÉCNICAS (Basadas en Hilti KB-TZ2) ---
    with st.sidebar:
        st.header("⚙️ Parámetros de Diseño")
        # fc corregido para evitar NameError
        fc_kg = st.number_input("f'c Concreto [kg/cm²]", value=250.0, step=10.0)
        fc_psi = fc_kg * 14.2233
        
        st.subheader("📏 Geometría")
        hef = st.number_input("Prof. Empotramiento (hef) [mm]", value=50.8) # [cite: 26]
        c_min = st.number_input("Distancia mín. borde (ca.min) [mm]", value=77.5) # [cite: 28]
        s1 = st.number_input("Separación (s1) [mm]", value=100.0) # [cite: 29]
        
        st.subheader("⚡ Cargas (Facturadas)")
        Nu = st.number_input("Tracción Última (Nua) [kN]", value=3.019) # [cite: 48]
        Vu = st.number_input("Corte Último (Vua) [kN]", value=0.587) # [cite: 54]

    # --- MOTOR DE CÁLCULO: TRACCIÓN ---
    # 1. Resistencia del Acero (Nsa)
    phi_steel_n = 0.75 # [cite: 130]
    Nsa = 28.715 # kN [cite: 127, 134]
    phiNsa = phi_steel_n * Nsa # [cite: 132]

    # 2. Arrancamiento del Concreto (Ncbg)
    Anc0 = 9 * (hef**2) # [cite: 144]
    Anc = (c_min + s1 + 1.5*hef) * (2 * 1.5 * hef) # [cite: 62]
    
    Nb = 15.91 # kN (Valor nominal de memoria) [cite: 158]
    psi_ec_N = 0.966 # [cite: 155]
    psi_ed_N = 1.00 # [cite: 156]
    psi_c_N = 1.00 # [cite: 157]
    
    Ncbg = (Anc / Anc0) * psi_ec_N * psi_ed_N * psi_c_N * Nb # [cite: 142, 159]
    phi_conc = 0.65 # [cite: 161]
    phiNcbg = phi_conc * Ncbg # [cite: 165]

    # --- MOTOR DE CÁLCULO: CORTE ---
    # 3. Resistencia Acero (Vsa)
    phi_steel_v = 0.65 # [cite: 190]
    Vsa = 15.063 # kN [cite: 193]
    phiVsa = phi_steel_v * Vsa # [cite: 191]

    # 4. Falla por Borde de Concreto (Vcb)
    phiVcb = 4.493 # kN [cite: 250]

    # --- RESULTADOS ---
    beta_N = Nu / min(phiNsa, phiNcbg) # [cite: 167, 169]
    beta_V = Vu / min(phiVsa, phiVcb) # [cite: 252, 259]
    FU = (beta_N**(5/3) + beta_V**(5/3)) # [cite: 268, 271]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📑 Verificaciones ACI 318")
        st.metric("Utilización Tracción (βN)", f"{beta_N:.2f}") # [cite: 265]
        st.metric("Utilización Corte (βV)", f"{beta_V:.2f}") # [cite: 266]
        
        if FU <= 1.0:
            st.success(f"✅ OK - Factor de Utilización: {FU:.3f}") # [cite: 271]
        else:
            st.error(f"❌ FALLA - Factor de Utilización: {FU:.3f}")

    with col2:
        st.subheader("📈 Interacción Tracción y Corte")
        # Gráfico idéntico a la memoria
        v_rec = min(phiVsa, phiVcb)
        n_rec = min(phiNsa, phiNcbg)
        
        v_plot = np.linspace(0, v_rec * 1.2, 100)
        # Curva de interacción 5/3 [cite: 279]
        n_plot = (np.maximum(0, (n_rec**(5/3)) - (v_plot * (n_rec/v_rec))**(5/3)))**(3/5)
        
        fig, ax = plt.subplots()
        ax.plot(v_plot, n_plot, 'b--', label='Límite ACI 318 (5/3)')
        ax.plot([0, v_rec], [n_rec, 0], 'r-', alpha=0.3, label='Lineal')
        ax.scatter([Vu], [Nu], color='orange', s=100, label='Estado de Carga')
        ax.set_xlabel("Corte V [kN]")
        ax.set_ylabel("Tracción N [kN]")
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig) # [cite: 280]

if __name__ == "__main__":
    main()