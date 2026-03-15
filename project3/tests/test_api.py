import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta
from src.main import app
from src.db.models import User, Link
from src.auth.users import current_active_user


PATCH_PREFIX = "src.api.base.core"
VALID_URL = "http://valid.url"
NOT_EXIST_URL = "http://not.exist.url"
BASE_SHORT_CODE = "SHoRtCoDe"


@pytest.fixture(autouse=True)
def override_dependencies(mock_user):
    app.dependency_overrides[current_active_user] = lambda: mock_user
    yield
    app.dependency_overrides.clear()


def test_create_shorten_link_success(client, mock_user):
    with patch(f"{PATCH_PREFIX}.add_new_link_to_db", AsyncMock()) as mock_add, \
         patch(f"{PATCH_PREFIX}.generate_short_code", return_value=BASE_SHORT_CODE):

        mock_link = Link(
            short_code=BASE_SHORT_CODE,
            original_url=VALID_URL,
            creation_date=datetime.now(),
            user_id=mock_user.id
        )
        mock_add.return_value = mock_link
        
        response = client.post("/links/shorten", json={"url": VALID_URL})
        assert response.status_code == 200
        data = response.json()
        assert data["short_code"] == BASE_SHORT_CODE
        assert data["original_url"] == VALID_URL


def test_create_shorten_link_with_custom_alias(client, mock_user):
    with patch(f"{PATCH_PREFIX}.add_new_link_to_db", AsyncMock()) as mock_add:
        
        mock_link = Link(
            short_code="custom",
            original_url=VALID_URL,
            creation_date=datetime.now(),
            user_id=mock_user.id
        )
        mock_add.return_value = mock_link
        
        response = client.post(
            "/links/shorten",
            json={
                "url": VALID_URL,
                "custom_alias": "custom"
            }
        )
        assert response.status_code == 200
        assert response.json()["short_code"] == "custom"


def test_create_shorten_link_alias_exists(client):
    with patch(f"{PATCH_PREFIX}.add_new_link_to_db", AsyncMock(return_value=None)):
        response = client.post(
            "/links/shorten",
            json={
                "url": VALID_URL,
                "custom_alias": "existing"
            }
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Short code already exists"


def test_get_original_url_redirect(client):
    with patch(f"{PATCH_PREFIX}.get_original_url_from_db", AsyncMock(return_value=VALID_URL)):
        response = client.get(f"/links/{BASE_SHORT_CODE}", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == VALID_URL


def test_get_original_url_not_found(client):
    with patch(f"{PATCH_PREFIX}.get_original_url_from_db", AsyncMock(return_value=None)):
        response = client.get("/links/nonexistent")
        assert response.status_code == 404
        assert response.json()["detail"] == "Short code not found"


def test_get_stats_success(client):
    mock_stats = {
        "original_url": VALID_URL,
        "creation_date": datetime.now(),
        "click_count": 5,
        "last_using": datetime.now(),
        "expires_at": None
    }
    
    with patch(f"{PATCH_PREFIX}.get_stats_from_db", AsyncMock(return_value=mock_stats)):
        response = client.get(f"/links/{BASE_SHORT_CODE}/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["original_url"] == VALID_URL
        assert data["click_count"] == 5


def test_get_stats_not_found(client):
    with patch(f"{PATCH_PREFIX}.get_stats_from_db", AsyncMock(return_value=None)):
        response = client.get("/links/nonexistent/stats")
        assert response.status_code == 404
        assert response.json()["detail"] == "Short code not found"


def test_delete_link_forbidden(client):
    with patch(f"{PATCH_PREFIX}.check_user_access", AsyncMock(return_value=False)):
        response = client.delete(f"/links/{BASE_SHORT_CODE}")
        assert response.status_code == 403
        assert response.json()["detail"] == "Forbidden"


def test_update_link_forbidden(client):
    with patch(f"{PATCH_PREFIX}.check_user_access", AsyncMock(return_value=False)):
        response = client.put(
            f"/links/{BASE_SHORT_CODE}",
            json={"url": "https://new.url"}
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Forbidden"


def test_search_link_success(client):
    with patch(f"{PATCH_PREFIX}.search_short_code_by_original_url", AsyncMock(return_value=BASE_SHORT_CODE)):
        response = client.get(f"/links/search?original_url={VALID_URL}")
        assert response.status_code == 200
        assert response.json() == BASE_SHORT_CODE


def test_search_link_not_found(client):
    with patch(f"{PATCH_PREFIX}.search_short_code_by_original_url", AsyncMock(return_value=None)):
        response = client.get(f"/links/search?original_url={NOT_EXIST_URL}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Short code not found"


def test_get_deleted_links(client):
    with patch(f"{PATCH_PREFIX}.get_deleted_short_codes", AsyncMock(return_value=[])):
        response = client.get("/links/deleted")
        assert response.status_code == 200
        assert response.json()["deleted"] == []
