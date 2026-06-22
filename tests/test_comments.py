import pytest
from httpx import AsyncClient

from tests.conftest import auth_header, create_test_user, login_user


async def create_post(client: AsyncClient, headers: dict[str, str]) -> int:
    response = await client.post(
        "/api/posts",
        json={"title": "A post", "content": "A post with comments"},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


@pytest.mark.anyio
async def test_comment_lifecycle(client: AsyncClient):
    user = await create_test_user(client)
    headers = auth_header(await login_user(client))
    post_id = await create_post(client, headers)

    response = await client.post(
        f"/api/posts/{post_id}/comments",
        json={"content": "A thoughtful comment"},
        headers=headers,
    )
    assert response.status_code == 201
    comment = response.json()
    assert comment["content"] == "A thoughtful comment"
    assert comment["author"]["id"] == user["id"]

    post_response = await client.get(f"/api/posts/{post_id}")
    assert post_response.json()["comments_count"] == 1

    response = await client.get(f"/api/posts/{post_id}/comments")
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["comments"][0]["id"] == comment["id"]

    response = await client.patch(
        f"/api/posts/{post_id}/comments/{comment['id']}",
        json={"content": "An updated comment"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["content"] == "An updated comment"

    response = await client.delete(
        f"/api/posts/{post_id}/comments/{comment['id']}", headers=headers
    )
    assert response.status_code == 204

    response = await client.get(f"/api/posts/{post_id}/comments")
    assert response.json()["total"] == 0
    post_response = await client.get(f"/api/posts/{post_id}")
    assert post_response.json()["comments_count"] == 0


@pytest.mark.anyio
async def test_comments_require_authentication_to_create(client: AsyncClient):
    await create_test_user(client)
    headers = auth_header(await login_user(client))
    post_id = await create_post(client, headers)
    client.cookies.clear()

    response = await client.post(
        f"/api/posts/{post_id}/comments",
        json={"content": "Anonymous comment"},
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_comment_can_only_be_changed_by_owner(client: AsyncClient):
    await create_test_user(client, username="owner", email="owner@example.com")
    owner_headers = auth_header(await login_user(client, email="owner@example.com"))
    post_id = await create_post(client, owner_headers)
    response = await client.post(
        f"/api/posts/{post_id}/comments",
        json={"content": "Owner's comment"},
        headers=owner_headers,
    )
    comment_id = response.json()["id"]

    await create_test_user(client, username="other", email="other@example.com")
    other_headers = auth_header(await login_user(client, email="other@example.com"))

    response = await client.patch(
        f"/api/posts/{post_id}/comments/{comment_id}",
        json={"content": "Changed by someone else"},
        headers=other_headers,
    )
    assert response.status_code == 403

    response = await client.delete(
        f"/api/posts/{post_id}/comments/{comment_id}", headers=other_headers
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_comments_for_missing_post_return_not_found(client: AsyncClient):
    response = await client.get("/api/posts/999999/comments")
    assert response.status_code == 404
