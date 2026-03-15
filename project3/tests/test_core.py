import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime
import string
from src.core import core
from src.db.models import Link

PATCH_PREFIX = "src.core.core"
VALID_URL = "http://valid.url"
NOT_EXIST_URL = "http://not.exist.url"
BASE_SHORT_CODE = "SHoRtCoDe"


def test_generate_short_code():
    short_code = core.generate_short_code()
    assert len(short_code) == 10
    
    custom_length = 15
    short_code = core.generate_short_code(custom_length)
    assert len(short_code) == custom_length

    allowed_chars = string.ascii_letters + string.digits
    assert all(c in allowed_chars for c in short_code)

    num_iter = 100
    codes = {core.generate_short_code() for _ in range(num_iter)}
    assert len(codes) == num_iter


@pytest.mark.asyncio
async def test_check_user_access():
    mock_db = AsyncMock()
    with patch(f"{PATCH_PREFIX}.links.get_active_link_by_code", AsyncMock(return_value=None)):
        result = await core.check_user_access(mock_db, BASE_SHORT_CODE, uuid4())
        assert result is True

    user_id = uuid4()
    mock_link = AsyncMock()
    mock_link.user_id = user_id
    
    mock_db = AsyncMock()
    with patch(f"{PATCH_PREFIX}.links.get_active_link_by_code", AsyncMock(return_value=mock_link)):
        result = await core.check_user_access(mock_db, BASE_SHORT_CODE, user_id)
        assert result is True
    
    mock_db = AsyncMock()
    with patch(f"{PATCH_PREFIX}.links.get_active_link_by_code", AsyncMock(return_value=mock_link)):
        result = await core.check_user_access(mock_db, BASE_SHORT_CODE, uuid4())
        assert result is False
    
    mock_db = AsyncMock()
    with patch(f"{PATCH_PREFIX}.links.get_active_link_by_code", AsyncMock(return_value=mock_link)):
        result = await core.check_user_access(mock_db, BASE_SHORT_CODE, None)
        assert result is False


@pytest.mark.asyncio
async def test_short_code_exists():
    mock_db = AsyncMock()
    with patch(f"{PATCH_PREFIX}.links.get_active_link_by_code", AsyncMock(return_value=object())):
        result = await core.short_code_exists(mock_db, BASE_SHORT_CODE)
        assert result is True

    with patch(f"{PATCH_PREFIX}.links.get_active_link_by_code", AsyncMock(return_value=None)):
        result = await core.short_code_exists(mock_db, BASE_SHORT_CODE)
        assert result == False

@pytest.mark.asyncio
async def test_get_actual_link():
    mock_db = AsyncMock()
    mock_link = object()
    with patch(f"{PATCH_PREFIX}.links.get_active_link_by_code", AsyncMock(return_value=mock_link)):
        result = await core.get_actual_link(mock_db, BASE_SHORT_CODE)
        assert result is mock_link

@pytest.mark.asyncio
async def test_add_new_link_to_db():
    mock_db = AsyncMock()
    mock_link = object()
    
    with patch(f"{PATCH_PREFIX}.short_code_exists", AsyncMock(return_value=False)), \
         patch(f"{PATCH_PREFIX}.links.create_link", AsyncMock(return_value=mock_link)):
        result = await core.add_new_link_to_db(mock_db, VALID_URL, BASE_SHORT_CODE)
        assert result is mock_link
    
    with patch(f"{PATCH_PREFIX}.short_code_exists", AsyncMock(return_value=True)):
        result = await core.add_new_link_to_db(mock_db, VALID_URL, BASE_SHORT_CODE)
        assert result is None

@pytest.mark.asyncio
async def test_get_original_url_from_db():
    mock_db = AsyncMock()
    mock_link = AsyncMock()
    mock_link.original_url = VALID_URL
    
    with patch(f"{PATCH_PREFIX}.links.get_active_link_by_code", AsyncMock(return_value=mock_link)), \
         patch(f"{PATCH_PREFIX}.links.increment_click_count", AsyncMock()) as mock_increment:
        result = await core.get_original_url_from_db(mock_db, BASE_SHORT_CODE)
        assert result == VALID_URL
        mock_increment.assert_called_once_with(mock_db, mock_link)

    with patch(f"{PATCH_PREFIX}.links.get_active_link_by_code", AsyncMock(return_value=None)):
        result = await core.get_original_url_from_db(mock_db, BASE_SHORT_CODE)
        assert result is None

@pytest.mark.asyncio
async def test_delete_short_code_from_db():
    mock_db = AsyncMock()
    mock_link = AsyncMock()
    
    with patch(f"{PATCH_PREFIX}.links.get_active_link_by_code", AsyncMock(return_value=mock_link)), \
         patch(f"{PATCH_PREFIX}.links.delete_link", AsyncMock()) as mock_delete:
        await core.delete_short_code_from_db(mock_db, BASE_SHORT_CODE)
        mock_delete.assert_called_once_with(mock_db, mock_link)

    with patch(f"{PATCH_PREFIX}.links.get_active_link_by_code", AsyncMock(return_value=None)), \
         patch(f"{PATCH_PREFIX}.links.delete_link", AsyncMock()) as mock_delete:
        await core.delete_short_code_from_db(mock_db, BASE_SHORT_CODE)
        mock_delete.assert_not_called()


@pytest.mark.asyncio
async def test_update_url_in_db():
    mock_db = AsyncMock()
    mock_link = AsyncMock()
    mock_link.expires_at = None
    mock_new_link = object()
    
    with patch(f"{PATCH_PREFIX}.links.get_active_link_by_code", AsyncMock(return_value=mock_link)), \
         patch(f"{PATCH_PREFIX}.links.delete_link", AsyncMock()), \
         patch(f"{PATCH_PREFIX}.add_new_link_to_db", AsyncMock(return_value=mock_new_link)):
        
        result = await core.update_url_in_db(mock_db, BASE_SHORT_CODE, "https://update.url")
        assert result is mock_new_link

    with patch(f"{PATCH_PREFIX}.links.get_active_link_by_code", AsyncMock(return_value=None)):
        result = await core.update_url_in_db(mock_db, BASE_SHORT_CODE, "https://update.url")
        assert result is None

@pytest.mark.asyncio
async def test_search_short_code_by_original_url():
    mock_db = AsyncMock()
    mock_result = ["code1", "code2"]
    
    with patch(f"{PATCH_PREFIX}.links.search_by_original_url", AsyncMock(return_value=mock_result)):
        result = await core.search_short_code_by_original_url(mock_db, VALID_URL)
        assert result == mock_result

@pytest.mark.asyncio
async def test_get_deleted_short_codes():
    mock_db = AsyncMock()
    mock_result = ["deleted1", "deleted2"]
    
    with patch(f"{PATCH_PREFIX}.links.get_deleted_links", AsyncMock(return_value=mock_result)):
        result = await core.get_deleted_short_codes(mock_db)
        assert result == mock_result

@pytest.mark.asyncio
async def test_get_stats_from_db():
    mock_db = AsyncMock()
    expected = {
        "short_code": BASE_SHORT_CODE,
        "original_url": "http://something",
        "creation_date": datetime.utcnow(),
        "click_count": 0,
        "last_using": None,
        "expires_at": None
    }
    mock_result = Link(
        short_code=expected["short_code"],
        original_url=expected["original_url"],
        creation_date=expected["creation_date"],
        click_count=expected["click_count"],
        last_using=expected["last_using"],
        expires_at=expected["expires_at"]
    )
    
    with patch(f"{PATCH_PREFIX}.links.get_active_link_by_code", AsyncMock(return_value=mock_result)):
        result = await core.get_stats_from_db(mock_db, BASE_SHORT_CODE)
        assert result == expected
    
    with patch(f"{PATCH_PREFIX}.links.get_active_link_by_code", AsyncMock(return_value=None)):
        result = await core.get_stats_from_db(mock_db, BASE_SHORT_CODE)
        assert result is None
