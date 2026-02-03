from collections import Counter
import streamlit as st


def causa_solucion(df):
    contador_palabras = Counter()
    temas_counts = df['Temas_Descripcion'].value_counts()

    for tema, cantidad in temas_counts.items():
        if isinstance(tema, str):
            partes = tema.split(' ')
            palabras = [p for p in partes if not p.isdigit() and len(p) > 1]
            for p in palabras:
                contador_palabras[p] += cantidad
    
    palabras_ordenadas = [p for p, c in contador_palabras.most_common()]

    palabra = st.selectbox("Seleccione la Palabra Clave para Filtrar la columna Temas_Descripcion", palabras_ordenadas, index=None, placeholder="Seleccione una Palabra Clave")

    # Estados
    if palabra != st.session_state.get('last_palabra_filtro'):
        st.session_state.items_visibles = 10
        st.session_state.last_palabra_filtro = palabra
    if 'items_visibles' not in st.session_state:
        st.session_state.items_visibles = 10

    if palabra:
        df_final = df[df['Temas_Descripcion'].str.contains(palabra, case=False, na=False)]

        st.markdown("---")
        st.markdown(f"### 🎯 Foco: {palabra} ({len(df_final)} tickets)")
        st.divider()

        if not df_final.empty:
            total = len(df_final)
            patrones = df_final.groupby(['Temas_Causa', 'Temas_Solucion']).size().reset_index(name='Frecuencia')
            patrones['Probabilidad'] = (patrones['Frecuencia'] / total) * 100
            patrones = patrones.sort_values('Frecuencia', ascending=False)
            total_patrones = len(patrones)
            patrones_visibles = patrones.iloc[:st.session_state.items_visibles]

            # Interfaz Visual
            for index, row in patrones_visibles.iterrows():
                causa = row['Temas_Causa']
                solucion = row['Temas_Solucion']
                prob = row['Probabilidad']
                count = row['Frecuencia']

                with st.container():
                    c1, c2 = st.columns([1, 4])

                    with c1:
                        st.metric(label="Probabilidad", value=f"{prob:.1f}%")
                        st.caption(f"({count} casos)")
                    
                    with c2:
                        st.error(f"**Causa Raíz:** {causa}")
                        st.success(f"**Solución Aplicada:** {solucion}")
                        
                        subset_ejemplo = df_final[
                            (df_final['Temas_Causa'] == causa) & 
                            (df_final['Temas_Solucion'] == solucion)
                        ]
                        
                        if not subset_ejemplo.empty:
                            ticket_real = subset_ejemplo.iloc[0]
                            raw_descripcion = ticket_real['Descripcion']
                            raw_causa = ticket_real['Causa']      
                            raw_solucion = ticket_real['Solucion'] 
                            
                            with st.expander("Ver Descripción del Ticket Original", expanded=False):
                                st.markdown(raw_descripcion)
                            
                            with st.expander("Ver Causa Raíz Detectada", expanded=False):
                                st.markdown(raw_causa)
                            
                            with st.expander("Ver Solución Aplicada", expanded=False):
                                st.markdown(raw_solucion)
                    
                    st.divider()

            if st.session_state.items_visibles < total_patrones:
                col_btn, _ = st.columns([1, 2])
                with col_btn:
                    if st.button(f"⬇️ Cargar 5 más (Vistos {len(patrones_visibles)} de {total_patrones})"):
                        st.session_state.items_visibles += 5
                        st.rerun()

