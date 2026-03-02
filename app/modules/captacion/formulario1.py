import streamlit as st
import re
import json
import os
import base64

from pathlib import Path

from modules.captacion.service import crear_caso
from utils.helpers import generar_link_documentos, generar_email_bienvenida
from services.email import enviar_email
from services.radicado import generar_radicado

# 🔥 CARGAR DATOS DE COLOMBIA

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ruta_json = os.path.join(BASE_DIR, "data", "colombia.json")

with open(ruta_json, encoding="utf-8") as f:
    datos_colombia = json.load(f)

def formulario_1():

    if "opcion" not in st.session_state:
        st.session_state["opcion"] = None

    rol = st.session_state.get("opcion")

    # -------------------------------
    # ENCABEZADO SFD
    # -------------------------------
    def get_base64_image(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
        
    logo_path = Path(__file__).parent / "logo_sfd-header.png"

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.image(str(logo_path), width=600)

    st.markdown('<div class="firma">SFD GESTIÓN JURÍDICA</div>', unsafe_allow_html=True)
    st.markdown('<div class="subfirma">Su caso no es uno más: es una responsabilidad que asumimos al máximo nivel</div>', unsafe_allow_html=True)

    st.markdown('<div class="linea-dorada"></div>', unsafe_allow_html=True)

    def k(nombre):
        return f"{nombre}_{rol if rol else 'tmp'}"

    # -------------------------------
    # SELECCIÓN DE ROL
    # -------------------------------
    st.markdown("## ⚖️ ¿En qué podemos ayudarte hoy?")
    st.markdown("Selecciona una opción:")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Quiero demandar", use_container_width=True):
            st.session_state["opcion"] = "1"

        if st.button("⚖️ Me están demandando", use_container_width=True):
            st.session_state["opcion"] = "3"
 
        if st.button("📄 Trámite legal", use_container_width=True):
            st.session_state["opcion"] = "5"

    with col2:
        if st.button("🔄 Cambiar de abogado", use_container_width=True):
            st.session_state["opcion"] = "2"

        if st.button("🚨 Demanda en curso + nuevo abogado", use_container_width=True):
            st.session_state["opcion"] = "4"

    rol = st.session_state.get("opcion")

    if not rol:
        st.warning("⚠️ Selecciona una opción para continuar")
        return

    if rol in ["2", "4"]:
       st.error("🚫 Este caso requiere documentación previa")

    key_radio = f"paz_salvo_{rol}"

    # 🔥 SOLO CREAR EL WIDGET UNA VEZ
    if key_radio not in st.session_state:
        dispone_docs = st.radio(
            "¿Tiene paz y salvo del abogado anterior?",
            ["Sí", "No"],
            key=key_radio
        )
    else:
        dispone_docs = st.session_state[key_radio]

    if dispone_docs == "No":
        st.warning("⚠️ Debe solicitar el paz y salvo y radicarlo en nuestro sistema para continuar con su representación")
        return

    # -------------------------------
    # CONTROL DOCUMENTOS
    # -------------------------------
        rol = st.session_state.get("opcion")
        if rol in ["2", "4"]:
           st.error("🚫 Este caso requiere documentación previa")
  
           dispone_docs = st.radio(
                  "¿Tiene paz y salvo del abogado anterior?",
                  ["Sí", "No"],
                  key=k("paz_salvo")
           )

        if dispone_docs == "No":
            st.warning("⚠️ Debe solicitar el paz y salvo y radicarlo en nuestro sistema para continuar con su representación")

    # -------------------------------
    # DATOS PERSONALES
    # -------------------------------
    st.markdown("## 1. Datos Personales")

    col1, col2 = st.columns(2)

    nombre = col1.text_input("Nombre completo*", key=k("nombre"))
    doc_raw = col2.text_input("Cédula*", key=k("cedula"))

    if doc_raw:
        if doc_raw.isdigit():
            st.caption(f"📌 Verificación: {int(doc_raw):,}".replace(",", "."))
        else:
            st.error("❌ Solo números en la cédula")

    # -------------------------------
    # TELÉFONO
    # -------------------------------
    col3, col4 = st.columns(2)

    celular = col3.text_input("Celular*", key=k("celular"))

    if celular.isdigit() and celular.startswith("57") and len(celular) >= 12:
        st.caption(f"📌 Formato: (57) {celular[2:5]} {celular[5:8]} {celular[8:]}")

    es_wa = col4.radio("¿Mismo número para WhatsApp?", ["Sí", "No"], key=k("wa"))

    whatsapp = celular
    if es_wa == "No":
        whatsapp = st.text_input("Número WhatsApp", key=k("whatsapp"))

    # -------------------------------
    # SITUACIÓN LABORAL (AGREGADO)
    # -------------------------------
    st.markdown("## Situación Laboral")

    situacion_laboral = st.radio(
        "Seleccione su situación laboral*",
        ["Empleado", "Pensionado", "Independiente"],
        horizontal=True,
        key=k("sit_laboral")
    )

    empresa_pagador = ""
    actividad_economica = ""

    if situacion_laboral == "Empleado":
        empresa_pagador = st.text_input(
            "Nombre de la empresa / Pagador*",
            key=k("empresa_pagador")
        ).upper()

    elif situacion_laboral == "Pensionado":
        empresa_pagador = st.text_input(
            "Entidad pagadora de la pensión*",
            key=k("entidad_pension")
        ).upper()

    elif situacion_laboral == "Independiente":
        actividad_economica = st.text_input(
            "Actividad económica*",
            key=k("actividad_economica")
        ).upper()

    # -------------------------------
    # EMAIL
    # -------------------------------
    st.markdown("## 2. Correo")

    col5, col6 = st.columns(2)

    email = col5.text_input("Correo electrónico*", key=k("email"))
    email_conf = col6.text_input("Confirmar correo*", key=k("email_conf"))

    error_email = False

    def validar_email(correo):
        return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', correo)

    if email and not validar_email(email):
        st.error("❌ Formato de correo inválido")
        error_email = True

    if email and email_conf:
        if email != email_conf:
            st.error("❌ Los correos no coinciden")
            error_email = True
        elif not error_email:
            st.success("✅ Correo verificado")

    # -------------------------------
    # DIRECCIÓN (AJUSTE EXACTO)
    # -------------------------------
    st.markdown("## Dirección de Notificación Física")
    st.write("**Nomenclatura Exacta**")

    d_cols = st.columns([1.5, 1, 1, 1, 0.5, 1, 1, 1, 1, 1.5])

    with d_cols[0]: 
        via = st.selectbox("Nomenclatura", ["Calle", "Carrera", "Diagonal", "Transversal", "Avenida"], key="v1")
    with d_cols[1]: 
        n_1 = st.text_input("Número", key="n1")
    with d_cols[2]: 
        l_1 = st.selectbox("Letra", ["-", "A", "B", "C", "D", "E"], key="l1")
    with d_cols[3]: 
        ref_1 = st.selectbox("Referencia", ["-", "Bis", "Sur", "Este"], key="r1")
    with d_cols[4]: 
        st.markdown("<h3 style='text-align:center; margin-top:20px;'>#</h3>", unsafe_allow_html=True)
    with d_cols[5]: 
        n_2 = st.text_input("Número ", key="n2")
    with d_cols[6]: 
        l_2 = st.selectbox("Letra ", ["-", "A", "B", "C", "D", "E"], key="l2")
    with d_cols[7]: 
        n_3 = st.text_input("Número  ", key="n3")
    with d_cols[8]: 
        ref_2 = st.selectbox("Referencia ", ["-", "Bis", "Sur", "Este"], key="r2")
    with d_cols[9]: 
        apto = st.text_input("Adicional", placeholder="Apto 201", key="apto")

    l1_v = "" if l_1 == "-" else l_1
    r1_v = "" if ref_1 == "-" else ref_1
    l2_v = "" if l_2 == "-" else l_2
    r2_v = "" if ref_2 == "-" else ref_2

    direccion = f"{via} {n_1}{l1_v} {r1_v} # {n_2}{l2_v} - {n_3} {r2_v} {apto}".replace("  ", " ").strip()

    st.text_input("Dirección que será registrada (Verificación Visual)*", value=direccion, disabled=True)

    col_dep, col_mun = st.columns(2)
    lista_departamentos = [d['departamento'] for d in datos_colombia]

    with col_dep:
        dep_sel = st.selectbox("Departamento*", ["Seleccione..."] + lista_departamentos, key="dep_sel")

    with col_mun:
        municipios = []
        if dep_sel != "Seleccione...":
            municipios = next(d['ciudades'] for d in datos_colombia if d['departamento'] == dep_sel)
        mun_sel = st.selectbox("Municipio / Ciudad*", ["Seleccione..."] + municipios, key="mun_sel")

    # -------------------------------
    # COMO NOS CONOCIÓ
    # -------------------------------
    st.markdown("## ¿Cómo nos conoció?")

    origen = st.selectbox(
        "Seleccione una opción",
        ["Google", "Facebook", "Instagram", "Recomendación", "Otro"],
        key=k("origen")
    )

    # -------------------------------
    # CONTRAPARTE DINÁMICA
    # -------------------------------
    st.markdown("## 5. Información de la Contraparte")

    labels = {
        "1": "Nombre de la persona o entidad a demandar*",
        "2": "Nombre de la persona o entidad a quien demanda*",
        "3": "Nombre de la persona que lo demanda*",
        "4": "Nombre de la persona o entidad que lo está demandando*",
        "5": "Entidad del trámite*"
    }

    label = labels.get(rol)
    nombre_contraparte = st.text_input(label, key=k("contraparte"))

    if rol not in ["2", "4"]:

        conoce_doc = st.radio("¿Conoce la cédula o NIT?", ["No", "Sí"])
        if conoce_doc == "Sí":
            st.text_input("Número de documento")

        conoce_emp = st.radio("¿Conoce la empresa?", ["No", "Sí"])
        if conoce_emp == "Sí":
            st.text_input("Empresa")

        conoce_email = st.radio("¿Conoce el correo?", ["No", "Sí"])
        if conoce_email == "Sí":
            st.text_input("Correo")

        conoce_direccion = st.radio("¿Conoce la dirección?", ["No", "Sí"])

        if conoce_direccion == "Sí":
            st.markdown("### Dirección de la Contraparte")

            d_cols_c = st.columns([1.3, 0.8, 0.8, 1, 0.4, 0.8, 0.8, 0.8, 1, 1.2])

            with d_cols_c[0]:
                via_c = st.selectbox("Nomenclatura", ["Calle", "Carrera", "Diagonal", "Transversal", "Avenida"])
            with d_cols_c[1]:
                n_1c = st.text_input("Número")
            with d_cols_c[2]:
                l_1c = st.selectbox("Letra", ["-", "A", "B", "C", "D", "E"])
            with d_cols_c[3]:
                ref_1c = st.selectbox("Referencia", ["-", "Bis", "Sur", "Este"])
            with d_cols_c[4]:
                st.markdown("<h3 style='text-align:center; margin-top:20px;'>#</h3>", unsafe_allow_html=True)
            with d_cols_c[5]:
                n_2c = st.text_input("Número ")
            with d_cols_c[6]:
                l_2c = st.selectbox("Letra ", ["-", "A", "B", "C", "D", "E"])
            with d_cols_c[7]:
                n_3c = st.text_input("Número  ")
            with d_cols_c[8]:
                ref_2c = st.selectbox("Referencia ", ["-", "Bis", "Sur", "Este"])
            with d_cols_c[9]:
                apto_c = st.text_input("Adicional", placeholder="Apto 201")

            l1_vc = "" if l_1c == "-" else l_1c
            r1_vc = "" if ref_1c == "-" else ref_1c
            l2_vc = "" if l_2c == "-" else l_2c
            r2_vc = "" if ref_2c == "-" else ref_2c

            direccion_generada_c = f"{via_c} {n_1c}{l1_vc} {r1_vc} # {n_2c}{l2_vc} - {n_3c} {r2_vc} {apto_c}".replace("  ", " ").strip()

            st.text_input("Verificación Dirección*", value=direccion_generada_c, disabled=True)

    # -------------------------------
    # DESCRIPCIÓN
    # -------------------------------
    st.markdown("## 6. Descripción del caso")

    tipo = st.radio("Seleccione", ["Escribir", "Subir audio"], key=k("tipo"))

    descripcion = ""
    if tipo == "Escribir":
        descripcion = st.text_area("Describa el caso", key=k("descripcion"))
    else:
        st.file_uploader("Subir audio", type=["mp3", "wav"], key=k("audio"))

    # -------------------------------
    # BOTÓN FINAL
    # -------------------------------
    if st.button("REGISTRAR CASO"):

        if nombre and doc_raw and not error_email: 

            data = {
                "nombre": nombre,
                "cedula": doc_raw,
                "telefono": celular,
                "whatsapp": whatsapp,
                "email": email,
                "direccion": direccion,
                "empresa": empresa_pagador,
                "actividad": actividad_economica,
                "situacion_laboral": situacion_laboral,
                "rol": rol,
                "descripcion": descripcion
           }

            radicado = generar_radicado(rol)

            data["radicado"] = radicado

            crear_caso(data)

            link = generar_link_documentos(radicado)

            cuerpo = generar_email_bienvenida(nombre, radicado, link)

            enviar_email(email, "📄 Registro de caso - Sistema Jurídico SFD", cuerpo)

            st.success(f"✅ Radicado generado: {radicado}")
            st.info("📧 Se ha enviado un mensaje al correo que ha registrado con instrucciones para continuar el proceso")

        else:
            st.error("⚠️ Completa los campos obligatorios correctamente")