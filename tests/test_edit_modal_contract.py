"""Contratos del formulario flotante de edición de Duality (sin navegador)."""
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "src/web/app.js").read_text(encoding="utf-8")
EDIT = (ROOT / "src/web/edit-modal.js").read_text(encoding="utf-8")
HTML = (ROOT / "src/web/index.html").read_text(encoding="utf-8")
CSS = (ROOT / "src/web/styles.css").read_text(encoding="utf-8")
DOCKER = (ROOT / "docker/web/Dockerfile").read_text(encoding="utf-8")


@pytest.mark.unit
@pytest.mark.parametrize("handler,view", [
    ("editPatient", "patients"),
    ("editProduct", "products"),
    ("editService", "services"),
    ("editClinical", "clinical"),
    ("editOrder", "orders"),
    ("editPayment", "payments"),
    ("editUser", "users"),
])
def test_edit_handlers_open_form_instead_of_browser_prompt(handler, view):
    assert re.search(
        rf"function {handler}\(id\)\{{return openEditModal\('{view}',id\)\}}", APP
    )
    assert f'case "{view}":' in EDIT


@pytest.mark.unit
def test_edit_modal_loaded_into_deployed_nginx_image():
    assert '<script src="/app.js"></script>' in HTML
    assert '<script src="/edit-modal.js"></script>' in HTML
    assert HTML.index('src="/app.js"') < HTML.index('src="/edit-modal.js"')
    assert "COPY src/web/edit-modal.js /usr/share/nginx/html/edit-modal.js" in DOCKER


@pytest.mark.unit
def test_unsaved_changes_require_explicit_discard():
    assert "new FormData(session.form)" in EDIT
    assert "showDiscardConfirmation()" in EDIT
    assert 'data-stay>Seguir editando</button>' in EDIT
    assert 'data-discard>Descartar cambios</button>' in EDIT
    assert 'confirm.querySelector("[data-discard]").addEventListener("click", finishEdit)' in EDIT
    assert 'confirm.querySelector("[data-stay]").addEventListener("click", returnToEdit)' in EDIT


@pytest.mark.unit
def test_modal_uses_put_and_accessible_controls():
    assert 'method: "PUT"' in EDIT
    assert 'id="edit-record-error"' in EDIT
    assert 'type="submit" class="edit-save-button"' in EDIT
    assert 'data-cancel-edit>Cancelar</button>' in EDIT
    assert 'aria-labelledby="modal-title"' in HTML
    assert 'aria-describedby="modal-subtitle"' in HTML
    assert 'class="edit-record-form"' in EDIT


@pytest.mark.unit
def test_responsive_modal_styles_present():
    assert ".edit-fields{display:grid" in CSS
    assert "@media(max-width:600px)" in CSS
    assert ".edit-discard-confirm" in CSS
    assert ".edit-record-form[hidden]" in CSS


@pytest.mark.unit
@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js no disponible en este agente")
@pytest.mark.parametrize("file_name", ["app.js", "edit-modal.js"])
def test_javascript_syntax(file_name):
    subprocess.run(
        ["node", "--check", str(ROOT / "src/web" / file_name)],
        check=True,
        capture_output=True,
        text=True,
    )
