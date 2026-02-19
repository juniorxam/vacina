"""
logs.py - Página de logs do sistema com IP real
"""

import io
import pandas as pd
import plotly.express as px
import streamlit as st

from ui.components import UIComponents
from core.ip_utils import IPUtils


class LogsPage:
    """Página de logs do sistema"""
    
    def __init__(self, db, auth):
        self.db = db
        self.auth = auth
    
    def render(self):
        """Renderiza página de logs"""
        st.title("📝 Logs do Sistema")
        UIComponents.breadcrumb("🏠 Início", "Logs")

        if not self.auth.verificar_permissoes(st.session_state.nivel_acesso, "ADMIN"):
            st.error("❌ Apenas administradores podem visualizar os logs do sistema.")
            return

        col1, col2, col3 = st.columns(3)

        with col1:
            filtro_usuario = st.text_input("Usuário:", key="filtro_usuario_logs")

        with col2:
            filtro_modulo = st.selectbox(
                "Módulo:",
                ["TODOS", "AUTH", "SERVIDORES", "VACINAÇÃO", "CAMPANHAS", "ADMIN"],
                key="filtro_modulo_logs"
            )

        with col3:
            dias = st.slider("Últimos dias:", 1, 30, 7, key="filtro_dias_logs")

        where_clauses = ["data_hora >= datetime('now', '-' || ? || ' days')"]
        params = [str(dias)]

        if filtro_usuario:
            where_clauses.append("usuario LIKE ?")
            params.append(f"%{filtro_usuario}%")

        if filtro_modulo != "TODOS":
            where_clauses.append("modulo = ?")
            params.append(filtro_modulo)

        where_sql = " AND ".join(where_clauses)

        query = f"""
            SELECT * FROM logs
            WHERE {where_sql}
            ORDER BY data_hora DESC
            LIMIT 200
        """

        logs = self.db.read_sql(query, params)

        if not logs.empty:
            st.success(f"✅ {len(logs)} registros de log encontrados")

            df_logs = logs.copy()
            df_logs['data_hora'] = pd.to_datetime(df_logs['data_hora']).dt.strftime('%d/%m/%Y %H:%M:%S')
            
            # Mascarar IPs para exibição (opcional)
            df_logs['ip_masked'] = df_logs['ip_address'].apply(IPUtils.mask_ip)

            with st.expander("📈 Estatísticas"):
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

                with col_stat1:
                    usuarios_unicos = df_logs['usuario'].nunique()
                    st.metric("Usuários Únicos", usuarios_unicos)

                with col_stat2:
                    modulos_unicos = df_logs['modulo'].nunique()
                    st.metric("Módulos", modulos_unicos)

                with col_stat3:
                    acoes_unicas = df_logs['acao'].nunique()
                    st.metric("Tipos de Ação", acoes_unicas)
                
                with col_stat4:
                    ips_unicos = df_logs['ip_address'].nunique()
                    st.metric("IPs Únicos", ips_unicos)

                # Gráfico de IPs mais frequentes
                ip_count = df_logs['ip_masked'].value_counts().head(10)
                if not ip_count.empty:
                    fig_ip = px.bar(
                        x=ip_count.values,
                        y=ip_count.index,
                        orientation='h',
                        title='Top 10 IPs por Atividade',
                        labels={'x': 'Quantidade de Ações', 'y': 'IP (Mascarado)'}
                    )
                    st.plotly_chart(fig_ip, use_container_width=True)

            st.subheader("📋 Registros de Log")
            st.dataframe(
                df_logs[['data_hora', 'usuario', 'modulo', 'acao', 'detalhes', 'ip_masked']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "data_hora": "Data/Hora",
                    "usuario": "Usuário",
                    "modulo": "Módulo",
                    "acao": "Ação",
                    "detalhes": "Detalhes",
                    "ip_masked": "IP (Mascarado)"
                }
            )

            col_exp1, col_exp2 = st.columns(2)

            with col_exp1:
                csv = logs.to_csv(index=False)
                st.download_button(
                    "📥 CSV",
                    csv,
                    f"logs_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    use_container_width=True
                )

            with col_exp2:
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    logs.to_excel(writer, index=False, sheet_name='Logs')

                st.download_button(
                    "📊 Excel",
                    excel_buffer.getvalue(),
                    f"logs_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        else:
            st.info("📭 Nenhum registro de log encontrado para os filtros selecionados.")
