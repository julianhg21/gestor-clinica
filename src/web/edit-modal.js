(function dualityEditDialogs() {
  "use strict";
  const modal = document.getElementById("modal");
  const modalBody = document.getElementById("modal-body");
  const modalTitle = document.getElementById("modal-title");
  const modalSubtitle = document.getElementById("modal-subtitle");
  const closeButton = modal.querySelector("[data-close-modal]");
  let session = null;

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, c => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[c]);
  }

  function field(name, label, value, options = {}) {
    const type = options.type || "text";
    const attributes = [
      `name="${escapeHtml(name)}"`,
      options.required ? "required" : "",
      options.maxLength ? `maxlength="${options.maxLength}"` : "",
      options.minLength ? `minlength="${options.minLength}"` : "",
      options.min !== undefined ? `min="${escapeHtml(options.min)}"` : "",
      options.max !== undefined ? `max="${escapeHtml(options.max)}"` : "",
      options.step ? `step="${escapeHtml(options.step)}"` : "",
      options.placeholder ? `placeholder="${escapeHtml(options.placeholder)}"` : ""
    ].filter(Boolean).join(" ");
    let control;
    if (type === "textarea") {
      control = `<textarea ${attributes} rows="3">${escapeHtml(value)}</textarea>`;
    } else if (type === "select") {
      const choices = [...(options.choices || [])];
      if (value !== null && value !== undefined && !choices.some(choice => String(choice.value) === String(value))) {
        choices.unshift({value: String(value), label: `Actual (${value})`});
      }
      control = `<select ${attributes}>${choices.map(choice =>
        `<option value="${escapeHtml(choice.value)}"${String(choice.value) === String(value) ? " selected" : ""}>${escapeHtml(choice.label)}</option>`
      ).join("")}</select>`;
    } else {
      control = `<input type="${escapeHtml(type)}" ${attributes} value="${escapeHtml(value)}">`;
    }
    return `<label class="edit-field${options.wide ? " wide" : ""}"><span>${escapeHtml(label)}${options.required ? ' <b aria-hidden="true">*</b>' : ""}</span>${control}</label>`;
  }

  const nullable = value => value.trim() || null;
  const numberOrNull = value => value.trim() === "" ? null : Number(value);
  const valuesOf = form => Object.fromEntries(new FormData(form).entries());

  function getRecord(type, id) {
    const names = {
      patients: ["patients", "id_paciente"],
      products: ["products", "id_producto"],
      services: ["services", "id_servicio"],
      clinical: ["clinical", "id_servicio_realizado"],
      payments: ["payments", "id_pago"],
      users: ["users", "id_usuario"]
    };
    const entry = names[type];
    return entry ? state[entry[0]].find(item => item[entry[1]] === id) : null;
  }

  async function buildEditor(type, id) {
    const r = type === "orders" ? (await api("/api/pedidos/" + encodeURIComponent(id))).order : getRecord(type, id);
    if (!r) throw new Error("No se encontró el registro seleccionado.");
    const endpoint = {
      patients: "/api/catalogo/patients/", products: "/api/catalogo/products/",
      services: "/api/catalogo/services/", clinical: "/api/catalogo/clinical-services/",
      orders: "/api/pedidos/", payments: "/api/pagos/", users: "/api/users/"
    }[type] + encodeURIComponent(id);
    const common = {endpoint, view: type, hint: "Actualiza los campos necesarios y guarda para aplicar los cambios."};
    switch (type) {
      case "patients":
        return {...common, title: "Editar paciente", fields: [
          field("nombres", "Nombres", r.nombres, {required: true, maxLength: 100}),
          field("apellidos", "Apellidos", r.apellidos, {required: true, maxLength: 100}),
          field("fecha_nacimiento", "Fecha de nacimiento", (r.fecha_nacimiento || "").slice(0, 10), {type: "date"}),
          field("telefono", "Teléfono", r.telefono, {maxLength: 25}),
          field("correo", "Correo electrónico", r.correo, {type: "email"}),
          field("observaciones", "Observaciones", r.observaciones, {type: "textarea", wide: true})
        ], payload: data => ({
          nombres: data.nombres.trim(), apellidos: data.apellidos.trim(),
          fecha_nacimiento: nullable(data.fecha_nacimiento), telefono: nullable(data.telefono),
          correo: nullable(data.correo), observaciones: nullable(data.observaciones)
        })};
      case "products":
        return {...common, title: "Editar producto", fields: [
          field("sku", "Código / SKU", r.sku, {maxLength: 50}),
          field("nombre", "Nombre del producto", r.nombre, {required: true, maxLength: 150}),
          field("costo_unitario", "Costo unitario (Q)", r.costo_unitario, {type: "number", min: 0, step: "0.01"}),
          field("precio_venta", "Precio de venta (Q)", r.precio_venta, {type: "number", min: 0, step: "0.01", required: true}),
          field("stock_minimo", "Stock mínimo", r.stock_minimo ?? 0, {type: "number", min: 0, step: "0.01"}),
          field("descripcion", "Descripción", r.descripcion, {type: "textarea", maxLength: 300, wide: true})
        ], payload: data => ({
          sku: nullable(data.sku), nombre: data.nombre.trim(),
          costo_unitario: numberOrNull(data.costo_unitario),
          precio_venta: Number(data.precio_venta),
          stock_minimo: numberOrNull(data.stock_minimo),
          descripcion: nullable(data.descripcion)
        })};
      case "services":
        return {...common, title: "Editar servicio", fields: [
          field("nombre", "Nombre del servicio", r.nombre, {required: true, maxLength: 120}),
          field("precio_base", "Precio base (Q)", r.precio_base, {type: "number", min: 0, step: "0.01", required: true}),
          field("duracion_min", "Duración (minutos)", r.duracion_min, {type: "number", min: 1, step: "1"}),
          field("descripcion", "Descripción", r.descripcion, {type: "textarea", maxLength: 300, wide: true})
        ], payload: data => ({
          nombre: data.nombre.trim(), precio_base: Number(data.precio_base),
          duracion_min: numberOrNull(data.duracion_min), descripcion: nullable(data.descripcion)
        })};
      case "clinical":
        return {...common, title: "Editar servicio realizado", hint: "Solo se pueden editar atenciones que aún no estén finalizadas o anuladas.", fields: [
          field("id_paciente", "Paciente", r.id_paciente, {type: "select", required: true,
            choices: state.patients.map(p => ({value: p.id_paciente, label: `${p.nombres} ${p.apellidos}`}))}),
          field("id_servicio", "Servicio", r.id_servicio, {type: "select", required: true,
            choices: state.services.map(s => ({value: s.id_servicio, label: s.nombre}))}),
          field("precio_aplicado", "Precio aplicado (Q)", r.precio_aplicado, {type: "number", min: 0, step: "0.01"}),
          field("observaciones", "Observaciones", r.observaciones, {type: "textarea", wide: true})
        ], payload: data => ({
          id_paciente: data.id_paciente, id_servicio: data.id_servicio,
          precio_aplicado: numberOrNull(data.precio_aplicado),
          id_venta: r.id_venta || null, observaciones: nullable(data.observaciones)
        })};
      case "orders":
        return {...common, title: "Editar venta pendiente", hint: `Subtotal: ${money(r.subtotal)}. Solo las ventas pendientes permiten edición.`, fields: [
          field("id_metodo_pago", "Método de pago", r.id_metodo_pago, {type: "select", required: true,
            choices: state.methods.map(m => ({value: m.id_metodo_pago, label: m.nombre}))}),
          field("descuento", "Descuento (Q)", r.descuento ?? 0, {type: "number", min: 0, max: Number(r.subtotal), step: "0.01", required: true}),
          field("observaciones", "Observaciones", r.observaciones, {type: "textarea", maxLength: 300, wide: true})
        ], payload: data => ({
          id_metodo_pago: data.id_metodo_pago, descuento: Number(data.descuento),
          observaciones: nullable(data.observaciones)
        })};
      case "payments": {
        const method = state.methods.find(m => m.nombre === r.metodo_pago);
        if (!method) throw new Error("No se pudo identificar el método de pago actual. Actualiza el listado y vuelve a intentarlo.");
        return {...common, title: "Editar pago", hint: "Los pagos solo pueden modificarse mientras la venta esté pendiente.", fields: [
          field("id_metodo_pago", "Método de pago", method.id_metodo_pago, {type: "select", required: true,
            choices: state.methods.map(m => ({value: m.id_metodo_pago, label: m.nombre}))}),
          field("monto", "Monto (Q)", r.monto, {type: "number", min: "0.01", step: "0.01", required: true}),
          field("referencia", "Referencia", r.referencia, {maxLength: 120, wide: true})
        ], payload: data => ({
          id_metodo_pago: data.id_metodo_pago, monto: Number(data.monto),
          referencia: nullable(data.referencia)
        })};
      }
      case "users":
        return {...common, title: "Editar usuario", hint: "El correo no puede modificarse desde esta pantalla. La contraseña nueva es opcional.", fields: [
          `<div class="edit-readonly wide"><span>Correo de acceso</span><strong>${escapeHtml(r.correo)}</strong></div>`,
          field("nombre_completo", "Nombre completo", r.nombre_completo, {required: true, maxLength: 120}),
          field("telefono", "Teléfono", r.telefono, {maxLength: 25}),
          field("id_rol", "Rol", r.id_rol, {type: "select", required: true, choices: [
            {value: "ROL_ADMIN", label: "Administrador"}, {value: "ROL_OPER", label: "Operativo"}, {value: "ROL_CONS", label: "Consulta"}
          ]}),
          field("activo", "Estado", String(r.activo), {type: "select", required: true, choices: [
            {value: "true", label: "Activo"}, {value: "false", label: "Inactivo"}
          ]}),
          field("password", "Nueva contraseña (opcional)", "", {type: "password", minLength: 8, maxLength: 128, placeholder: "Dejar vacío para conservar la actual", wide: true})
        ], payload: data => ({
          nombre_completo: data.nombre_completo.trim(), telefono: nullable(data.telefono),
          id_rol: data.id_rol, activo: data.activo === "true",
          ...(data.password ? {password: data.password} : {})
        })};
      default:
        throw new Error("Este módulo no tiene edición disponible.");
    }
  }

  function isDirty() {
    if (!session) return false;
    return JSON.stringify([...new FormData(session.form).entries()]) !== session.initial;
  }

  function finishEdit() {
    if (!session) return;
    const previous = session.previous;
    session = null;
    modal.classList.add("hidden");
    document.body.classList.remove("modal-open");
    modalBody.replaceChildren();
    if (previous && previous.isConnected && typeof previous.focus === "function") previous.focus();
  }

  function showDiscardConfirmation() {
    if (!session) return;
    session.form.hidden = true;
    session.confirm.hidden = false;
    modalTitle.textContent = "¿Descartar los cambios?";
    modalSubtitle.textContent = "Se perderán las modificaciones que no hayas guardado.";
    session.confirm.querySelector("[data-stay]").focus();
  }

  function returnToEdit() {
    if (!session) return;
    session.confirm.hidden = true;
    session.form.hidden = false;
    modalTitle.textContent = session.title;
    modalSubtitle.textContent = session.hint;
    session.form.querySelector("button[data-cancel-edit]").focus();
  }

  function requestCloseEdit() {
    if (!session || session.saving) return;
    if (!session.confirm.hidden) {
      returnToEdit();
    } else if (isDirty()) {
      showDiscardConfirmation();
    } else {
      finishEdit();
    }
  }

  window.openEditModal = async function openEditModal(type, id) {
    if (session) return;
    try {
      const config = await buildEditor(type, id);
      if (session) return;
      const previous = document.activeElement;
      modalTitle.textContent = config.title;
      modalSubtitle.textContent = config.hint;
      modalBody.innerHTML = `
        <form id="edit-record-form" class="edit-record-form">
          <div class="edit-fields">${config.fields.join("")}</div>
          <p id="edit-record-error" class="edit-record-error" role="alert" hidden></p>
          <div class="edit-modal-actions">
            <button type="button" class="secondary" data-cancel-edit>Cancelar</button>
            <button type="submit" class="edit-save-button">Guardar cambios</button>
          </div>
        </form>
        <section class="edit-discard-confirm" role="alert" hidden>
          <div class="discard-symbol" aria-hidden="true">!</div>
          <h3>Tienes cambios sin guardar</h3>
          <p>Si descartas, perderás las modificaciones realizadas en este formulario.</p>
          <div class="edit-modal-actions">
            <button type="button" class="secondary" data-stay>Seguir editando</button>
            <button type="button" class="discard-button" data-discard>Descartar cambios</button>
          </div>
        </section>`;
      const form = modalBody.querySelector("#edit-record-form");
      const confirm = modalBody.querySelector(".edit-discard-confirm");
      session = {
        form, confirm, previous, title: config.title, hint: config.hint,
        initial: JSON.stringify([...new FormData(form).entries()]), saving: false
      };
      form.querySelector("[data-cancel-edit]").addEventListener("click", requestCloseEdit);
      confirm.querySelector("[data-stay]").addEventListener("click", returnToEdit);
      confirm.querySelector("[data-discard]").addEventListener("click", finishEdit);
      form.addEventListener("submit", async event => {
        event.preventDefault();
        if (!session || session.saving) return;
        const button = form.querySelector(".edit-save-button");
        const error = form.querySelector("#edit-record-error");
        const data = valuesOf(form);
        session.saving = true;
        button.disabled = true;
        button.textContent = "Guardando…";
        error.hidden = true;
        try {
          await api(config.endpoint, {method: "PUT", body: JSON.stringify(config.payload(data))});
          finishEdit();
          toast("Cambios guardados correctamente");
          await view(config.view);
        } catch (err) {
          error.textContent = err.message || "No se pudieron guardar los cambios.";
          error.hidden = false;
          error.focus();
        } finally {
          if (session) session.saving = false;
          if (button.isConnected) {
            button.disabled = false;
            button.textContent = "Guardar cambios";
          }
        }
      });
      modal.classList.remove("hidden");
      document.body.classList.add("modal-open");
      form.querySelector("input:not([type=hidden]), select, textarea").focus();
    } catch (error) {
      toast(error.message || "No se pudo abrir la edición.", "error");
    }
  };

  closeButton.addEventListener("click", requestCloseEdit);
  modal.addEventListener("mousedown", event => {
    if (event.target === modal) requestCloseEdit();
  });
  document.addEventListener("keydown", event => {
    if (!session || modal.classList.contains("hidden")) return;
    if (event.key === "Escape") {
      event.preventDefault();
      requestCloseEdit();
    }
    if (event.key !== "Tab") return;
    const candidates = [...modal.querySelectorAll("button, input, select, textarea")].filter(el =>
      !el.disabled && !el.closest("[hidden]") && el.getClientRects().length > 0
    );
    if (!candidates.length) return;
    const first = candidates[0], last = candidates[candidates.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault(); last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault(); first.focus();
    }
  });
})();
