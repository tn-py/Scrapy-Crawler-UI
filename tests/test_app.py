
import pytest
from app.core import test_url

def test_test_url_success(requests_mock):
    url = "http://test.com"
    requests_mock.get(url, text="<html/>", status_code=200, headers={"Content-Type": "text/html; charset=utf-8"})
    result = test_url(url)
    assert result["status"] == 200
    assert "latency" in result
    assert result["charset"] == "utf-8"
    assert result["content"] == "<html/>"

def test_test_url_failure(requests_mock):
    url = "http://test.com"
    requests_mock.get(url, status_code=404)
    result = test_url(url)
    assert "error" in result
