"""Extended unit tests for runtime letta_client."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from runtime.core.letta_client import LettaClient


class TestLettaClientExtended:
    """Extended test cases for LettaClient."""

    def test_letta_client_initialization(self):
        """Test LettaClient initialization."""
        client = LettaClient()
        assert client is not None

    def test_letta_client_initialization_with_config(self):
        """Test LettaClient initialization with config."""
        config = {"base_url": "http://test.com", "timeout": 30}
        client = LettaClient(config=config)
        assert client is not None

    @pytest.mark.asyncio
    async def test_letta_client_connect(self):
        """Test LettaClient connect method."""
        client = LettaClient()
        
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"status": "connected"}
            
            result = await client.connect()
            assert result == {"status": "connected"}

    @pytest.mark.asyncio
    async def test_letta_client_disconnect(self):
        """Test LettaClient disconnect method."""
        client = LettaClient()
        
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"status": "disconnected"}
            
            result = await client.disconnect()
            assert result == {"status": "disconnected"}

    @pytest.mark.asyncio
    async def test_letta_client_send_message(self):
        """Test LettaClient send_message method."""
        client = LettaClient()
        message = {"text": "Hello, world!"}
        
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"response": "Message sent"}
            
            result = await client.send_message(message)
            assert result == {"response": "Message sent"}

    @pytest.mark.asyncio
    async def test_letta_client_get_status(self):
        """Test LettaClient get_status method."""
        client = LettaClient()
        
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"status": "active", "uptime": 3600}
            
            result = await client.get_status()
            assert result == {"status": "active", "uptime": 3600}

    @pytest.mark.asyncio
    async def test_letta_client_get_config(self):
        """Test LettaClient get_config method."""
        client = LettaClient()
        
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"config": {"timeout": 30}}
            
            result = await client.get_config()
            assert result == {"config": {"timeout": 30}}

    @pytest.mark.asyncio
    async def test_letta_client_update_config(self):
        """Test LettaClient update_config method."""
        client = LettaClient()
        new_config = {"timeout": 60}
        
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"status": "updated"}
            
            result = await client.update_config(new_config)
            assert result == {"status": "updated"}

    @pytest.mark.asyncio
    async def test_letta_client_make_request_get(self):
        """Test LettaClient _make_request with GET method."""
        client = LettaClient()
        
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": "test"}
            mock_get.return_value = mock_response
            
            result = await client._make_request("GET", "/test")
            assert result == {"data": "test"}

    @pytest.mark.asyncio
    async def test_letta_client_make_request_post(self):
        """Test LettaClient _make_request with POST method."""
        client = LettaClient()
        data = {"key": "value"}
        
        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"created": True}
            mock_post.return_value = mock_response
            
            result = await client._make_request("POST", "/test", data=data)
            assert result == {"created": True}

    @pytest.mark.asyncio
    async def test_letta_client_make_request_put(self):
        """Test LettaClient _make_request with PUT method."""
        client = LettaClient()
        data = {"key": "updated"}
        
        with patch('httpx.AsyncClient.put', new_callable=AsyncMock) as mock_put:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"updated": True}
            mock_put.return_value = mock_response
            
            result = await client._make_request("PUT", "/test", data=data)
            assert result == {"updated": True}

    @pytest.mark.asyncio
    async def test_letta_client_make_request_delete(self):
        """Test LettaClient _make_request with DELETE method."""
        client = LettaClient()
        
        with patch('httpx.AsyncClient.delete', new_callable=AsyncMock) as mock_delete:
            mock_response = MagicMock()
            mock_response.status_code = 204
            mock_response.json.return_value = None
            mock_delete.return_value = mock_response
            
            result = await client._make_request("DELETE", "/test")
            assert result is None

    @pytest.mark.asyncio
    async def test_letta_client_make_request_with_headers(self):
        """Test LettaClient _make_request with custom headers."""
        client = LettaClient()
        headers = {"Authorization": "Bearer token"}
        
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"authenticated": True}
            mock_get.return_value = mock_response
            
            result = await client._make_request("GET", "/test", headers=headers)
            assert result == {"authenticated": True}

    @pytest.mark.asyncio
    async def test_letta_client_make_request_with_params(self):
        """Test LettaClient _make_request with query parameters."""
        client = LettaClient()
        params = {"page": 1, "limit": 10}
        
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"page": 1, "limit": 10}
            mock_get.return_value = mock_response
            
            result = await client._make_request("GET", "/test", params=params)
            assert result == {"page": 1, "limit": 10}

    @pytest.mark.asyncio
    async def test_letta_client_make_request_http_error(self):
        """Test LettaClient _make_request with HTTP error."""
        client = LettaClient()
        
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = Exception("Not Found")
            mock_get.return_value = mock_response
            
            with pytest.raises(Exception, match="Not Found"):
                await client._make_request("GET", "/test")

    @pytest.mark.asyncio
    async def test_letta_client_make_request_json_error(self):
        """Test LettaClient _make_request with JSON decode error."""
        client = LettaClient()
        
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_get.return_value = mock_response
            
            with pytest.raises(ValueError, match="Invalid JSON"):
                await client._make_request("GET", "/test")

    @pytest.mark.asyncio
    async def test_letta_client_make_request_network_error(self):
        """Test LettaClient _make_request with network error."""
        client = LettaClient()
        
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            with pytest.raises(Exception, match="Network error"):
                await client._make_request("GET", "/test")

    @pytest.mark.asyncio
    async def test_letta_client_make_request_timeout(self):
        """Test LettaClient _make_request with timeout."""
        client = LettaClient()
        
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Timeout")
            
            with pytest.raises(Exception, match="Timeout"):
                await client._make_request("GET", "/test")

    def test_letta_client_get_base_url_default(self):
        """Test LettaClient get_base_url with default."""
        client = LettaClient()
        base_url = client._get_base_url()
        assert base_url == "http://localhost:8000"

    def test_letta_client_get_base_url_from_config(self):
        """Test LettaClient get_base_url from config."""
        config = {"base_url": "http://custom.com"}
        client = LettaClient(config=config)
        base_url = client._get_base_url()
        assert base_url == "http://custom.com"

    def test_letta_client_get_base_url_from_env(self):
        """Test LettaClient get_base_url from environment."""
        with patch('os.getenv', return_value="http://env.com"):
            client = LettaClient()
            base_url = client._get_base_url()
            assert base_url == "http://env.com"

    def test_letta_client_get_timeout_default(self):
        """Test LettaClient get_timeout with default."""
        client = LettaClient()
        timeout = client._get_timeout()
        assert timeout == 30

    def test_letta_client_get_timeout_from_config(self):
        """Test LettaClient get_timeout from config."""
        config = {"timeout": 60}
        client = LettaClient(config=config)
        timeout = client._get_timeout()
        assert timeout == 60

    def test_letta_client_get_timeout_from_env(self):
        """Test LettaClient get_timeout from environment."""
        with patch('os.getenv', return_value="45"):
            client = LettaClient()
            timeout = client._get_timeout()
            assert timeout == 45

    def test_letta_client_get_timeout_invalid_env(self):
        """Test LettaClient get_timeout with invalid environment value."""
        with patch('os.getenv', return_value="invalid"):
            client = LettaClient()
            timeout = client._get_timeout()
            assert timeout == 30  # Should fall back to default

    def test_letta_client_get_headers_default(self):
        """Test LettaClient get_headers with default."""
        client = LettaClient()
        headers = client._get_headers()
        assert headers == {"Content-Type": "application/json"}

    def test_letta_client_get_headers_from_config(self):
        """Test LettaClient get_headers from config."""
        config = {"headers": {"Authorization": "Bearer token"}}
        client = LettaClient(config=config)
        headers = client._get_headers()
        assert headers == {"Authorization": "Bearer token"}

    def test_letta_client_get_headers_merged(self):
        """Test LettaClient get_headers with merged config."""
        config = {"headers": {"Authorization": "Bearer token"}}
        client = LettaClient(config=config)
        headers = client._get_headers()
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer token"

    @pytest.mark.asyncio
    async def test_letta_client_context_manager(self):
        """Test LettaClient as context manager."""
        client = LettaClient()
        
        with patch.object(client, 'connect', new_callable=AsyncMock) as mock_connect:
            with patch.object(client, 'disconnect', new_callable=AsyncMock) as mock_disconnect:
                async with client:
                    pass
                
                mock_connect.assert_called_once()
                mock_disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_letta_client_context_manager_with_exception(self):
        """Test LettaClient context manager with exception."""
        client = LettaClient()
        
        with patch.object(client, 'connect', new_callable=AsyncMock) as mock_connect:
            with patch.object(client, 'disconnect', new_callable=AsyncMock) as mock_disconnect:
                try:
                    async with client:
                        raise ValueError("Test exception")
                except ValueError:
                    pass
                
                mock_connect.assert_called_once()
                mock_disconnect.assert_called_once()

    def test_letta_client_str_representation(self):
        """Test LettaClient string representation."""
        client = LettaClient()
        client_str = str(client)
        assert "LettaClient" in client_str

    def test_letta_client_repr_representation(self):
        """Test LettaClient repr representation."""
        client = LettaClient()
        client_repr = repr(client)
        assert "LettaClient" in client_repr

    def test_letta_client_equality(self):
        """Test LettaClient equality."""
        client1 = LettaClient()
        client2 = LettaClient()
        
        # Should not be equal (different instances)
        assert client1 != client2

    def test_letta_client_hash(self):
        """Test LettaClient hash."""
        client = LettaClient()
        client_hash = hash(client)
        assert isinstance(client_hash, int)

    @pytest.mark.asyncio
    async def test_letta_client_with_custom_client(self):
        """Test LettaClient with custom httpx client."""
        custom_client = MagicMock()
        client = LettaClient(http_client=custom_client)
        
        assert client._client == custom_client

    @pytest.mark.asyncio
    async def test_letta_client_make_request_with_custom_client(self):
        """Test LettaClient _make_request with custom client."""
        custom_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"custom": "response"}
        custom_client.get.return_value = mock_response
        
        client = LettaClient(http_client=custom_client)
        result = await client._make_request("GET", "/test")
        
        assert result == {"custom": "response"}
        custom_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_letta_client_make_request_with_retries(self):
        """Test LettaClient _make_request with retries."""
        client = LettaClient()
        
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            # First call fails, second succeeds
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"retried": True}
            mock_get.side_effect = [Exception("Network error"), mock_response]
            
            result = await client._make_request("GET", "/test")
            assert result == {"retried": True}

    @pytest.mark.asyncio
    async def test_letta_client_make_request_with_auth(self):
        """Test LettaClient _make_request with authentication."""
        client = LettaClient()
        
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"authenticated": True}
            mock_get.return_value = mock_response
            
            result = await client._make_request("GET", "/test", auth=("user", "pass"))
            assert result == {"authenticated": True}

    @pytest.mark.asyncio
    async def test_letta_client_make_request_with_cookies(self):
        """Test LettaClient _make_request with cookies."""
        client = LettaClient()
        cookies = {"session": "abc123"}
        
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"cookies": "set"}
            mock_get.return_value = mock_response
            
            result = await client._make_request("GET", "/test", cookies=cookies)
            assert result == {"cookies": "set"}

    @pytest.mark.asyncio
    async def test_letta_client_make_request_with_files(self):
        """Test LettaClient _make_request with files."""
        client = LettaClient()
        files = {"file": ("test.txt", "content")}
        
        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"uploaded": True}
            mock_post.return_value = mock_response
            
            result = await client._make_request("POST", "/test", files=files)
            assert result == {"uploaded": True}

    @pytest.mark.asyncio
    async def test_letta_client_make_request_with_stream(self):
        """Test LettaClient _make_request with streaming."""
        client = LettaClient()
        
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"streamed": True}
            mock_get.return_value = mock_response
            
            result = await client._make_request("GET", "/test", stream=True)
            assert result == {"streamed": True}
