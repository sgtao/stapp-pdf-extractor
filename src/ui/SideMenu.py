# SideMenu.py
import streamlit as st


class SideMenu:
    def render_menu(self):
        with st.sidebar:
            st.subheader("Sub Menus:")
            # state viewer
            with st.expander("session_state", expanded=False):
                st.write(st.session_state)

            # control buttons
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("", help="Clear whole state", icon="🔄"):
                    st.session_state.clear()
                    st.rerun()
            with col2:
                pass
            with col3:
                pass
            with col4:
                pass
            with col5:
                pass
