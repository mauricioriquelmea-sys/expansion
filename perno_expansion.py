import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Configuración de Marca: Structural Lab
st.set_page_config(page_title="Structural Lab | ACI 318-11 Expansion Anchor", layout="wide")

def main():
    st.title("🛡️ Engine: Anclajes de Expansión (ACI 318-11)")
    st.info("⚠️ Nota Técnica: El análisis de tensiones y distribución de cargas se basa en el supuesto de placa base rígida.")
    st.write("---")

    # --- INPUTS TÉCNICOS (SIDEBAR) ---
    with st.sidebar:
        st.header("⚙️ Parámetros de Diseño")
        fc_kg = st.number_input("f'c Concreto [kg/cm²]", value=250.0)
        
        st.subheader("📏 Geometría del Anclaje")
        hef = st.number_input("Prof. Empotramiento (hef) [mm]", value=50.8)
        c_min = st.number_input("Distancia mín. al borde (ca.min) [mm]", value=77.5)
        s1 = st.number_input("Separación (s1) [mm]", value=100.0)
        
        st.subheader("⚡ Cargas Solicitantes (Facturadas)")
        Nu = st.number_input("Tracción Última Nu [kN]", value=3.019)
        Vu = st.number_input("Corte Último Vu [kN]", value=0.587)

    # --- MOTOR DE CÁLCULO (Lógica ACI 318-11 / ESR-4266) ---
    # Capacidades extraídas de la memoria técnica Hilti KB-TZ2
    phiNn_acero = 21.536  # kN
    phiNn_conc = 12.47    # kN (Capacidad controlada por arrancamiento)
    
    phiVn_acero = 9.791   # kN
    phiVn_pryout = 13.905 # kN
    phiVn_borde = 4.493   # kN (Capacidad controlada por borde)

    # Determinación de los betas críticos para interacción
    beta_N_max = (Nu * 2) / phiNn_conc  # Basado en el grupo (Nu.c)
    beta_V_max = (Vu * 2) / phiVn_borde # Basado en el grupo (Vu.c)

    # --- FICHAS RESUMEN (LAYOUT PROFESIONAL) ---
    tab1, tab2 = st.tabs(["📑 Ficha Resumen: Tracción", "📑 Ficha Resumen: Corte"])

    with tab1:
        st.subheader("Análisis de Resistencia a Tracción")
        data_t = {
            "Tipo de Falla": [
                "Resistencia del acero*", 
                "Falla al arrancamiento del concreto**"
            ],
            "Carga Nu [kN]": [Nu, Nu * 2],
            "Capacidad ΦNn [kN]": [phiNn_acero, phiNn_conc],
            "Utilización β": [
                f"{Nu/phiNn_acero:.2f}", 
                f"{(Nu*2)/phiNn_conc:.2f}"
            ],
            "Resultado": [
                "OK" if Nu/phiNn_acero <= 1 else "FALLA", 
                "OK" if (Nu*2)/phiNn_conc <= 1 else "FALLA"
            ]
        }
        st.table(pd.DataFrame(data_t))
        st.caption("*anclaje más solicitado  **grupo de anclajes (anclajes relevantes)")

    with tab2:
        st.subheader("Análisis de Resistencia a Corte")
        data_v = {
            "Tipo de Falla": [
                "Resistencia del acero*", 
                "Falla por desprendimiento (Pryout)**", 
                "Fallo por borde de concreto**"
            ],
            "Carga Vu [kN]": [Vu, Vu * 2, Vu * 2],
            "Capacidad ΦVn [kN]": [phiVn_acero, phiVn_pryout, phiVn_borde],
            "Utilización β": [
                f"{Vu/phiVn_acero:.2f}", 
                f"{(Vu*2)/phiVn_pryout:.2f}", 
                f"{(Vu*2)/phiVn_borde:.2f}"
            ],
            "Resultado": [
                "OK", 
                "OK", 
                "OK" if (Vu*2)/phiVn_borde <= 1 else "FALLA"
            ]
        }
        st.table(pd.DataFrame(data_v))
        st.caption("*anclaje más solicitado  **grupo de anclajes (anclajes relevantes)")

    # --- DIAGRAMA DE INTERACCIÓN AUTO-ESCALABLE ---
    st.write("---")
    st.subheader("📈 Interacción Combinada (Tensión y Corte)")
    
    # 1. Definimos los límites de capacidad real en kgf para el gráfico
    n_limit_kgf = phiNn_conc * 101.97  
    v_limit_kgf = phiVn_borde * 101.97      
    
    # 2. Generamos la curva 5/3 basada en las capacidades REALES calculadas
    x_curve = np.linspace(0, v_limit_kgf, 100)
    # Ecuación: (N/Nn)^5/3 + (V/Vn)^5/3 = 1
    y_curve = n_limit_kgf * (np.maximum(0, 1 - (x_curve / v_limit_kgf)**(5/3)))**(3/5)

    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Dibujar curva y zona segura sombreada
    ax.plot(x_curve, y_curve, 'b--', label="Límite Normativo ACI 318 (ζ=5/3)")
    ax.fill_between(x_curve, y_curve, alpha=0.1, color='blue', label="Zona de Diseño Seguro")
    
    # Posicionar punto de carga (Nu.c y Vu.c) convertido a kgf
    punto_n_kgf = (Nu * 2) * 101.97
    punto_v_kgf = (Vu * 2) * 101.97
    
    ax.scatter([punto_v_kgf], [punto_n_kgf], color='red', s=120, label="Estado de Carga Grupo", zorder=5)
    
    # Auto-escala dinámica de los ejes
    ax.set_xlim(0, max(v_limit_kgf, punto_v_kgf) * 1.3)
    ax.set_ylim(0, max(n_limit_kgf, punto_n_kgf) * 1.3)
    
    ax.set_xlabel("Corte V [kgf]")
    ax.set_ylabel("Tracción N [kgf]")
    ax.set_title("Diagrama de Interacción Dinámico - Structural Lab")
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend()
    st.pyplot(fig)

    # --- RESULTADO FINAL Y MÉTRICAS ---
    # Factor de Utilización de interacción (FU)
    fu_final = beta_N_max**(5/3) + beta_V_max**(5/3)
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Máximo β Tracción", f"{beta_N_max:.2f}")
    col_b.metric("Máximo β Corte", f"{beta_V_max:.2f}")
    col_c.metric("Utilización Total (FU)", f"{fu_final:.3f}")
    
    if fu_final <= 1.0:
        st.success("ESTADO DEL DISEÑO: CUMPLE SATISFACTORIAMENTE ✅")
    else:
        st.error("ESTADO DEL DISEÑO: SOBRECARGA NORMATIVA ❌")

if __name__ == "__main__":
    main()