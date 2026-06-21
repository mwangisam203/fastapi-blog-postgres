import pytest
from httpx import AsyncClient

from tests.conftest import auth_header, create_test_user, login_user


async def create_post(client: AsyncClient, headers: dict[str, str]) -> int:
    response = await client.post(
        "/api/posts",
        json={"title": "Likeable post", "content": "Content worth liking"},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["likes"] == 0
    return response.json()["id"]


@pytest.mark.anyio
async def test_user_can_like_and_withdraw_like(client: AsyncClient):
    await create_test_user(client)
    headers = auth_header(await login_user(client))
    post_id = await create_post(client, headers)

    response = await client.post(f"/api/posts/{post_id}/like", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"post_id": post_id, "likes": 1, "liked": True}

    response = await client.get(
        f"/api/posts/likes/me?post_ids={post_id}", headers=headers
    )
    assert response.status_code == 200
    assert response.json()["post_ids"] == [post_id]

    response = await client.post(f"/api/posts/{post_id}/like", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"post_id": post_id, "likes": 0, "liked": False}

    response = await client.get(f"/api/posts/{post_id}")
    assert response.status_code == 200
    assert response.json()["likes"] == 0


@pytest.mark.anyio
async def test_likes_are_counted_across_users(client: AsyncClient):
    await create_test_user(client, username="first", email="first@example.com")
    first_headers = auth_header(await login_user(client, email="first@example.com"))
    post_id = await create_post(client, first_headers)

    await create_test_user(client, username="second", email="second@example.com")
    second_headers = auth_header(await login_user(client, email="second@example.com"))

    first = await client.post(f"/api/posts/{post_id}/like", headers=first_headers)
    second = await client.post(f"/api/posts/{post_id}/like", headers=second_headers)
    assert first.json()["likes"] == 1
    assert second.json()["likes"] == 2


@pytest.mark.anyio
async def test_like_requires_authentication(client: AsyncClient):
    await create_test_user(client)
    headers = auth_header(await login_user(client))
    post_id = await create_post(client, headers)

    response = await client.post(f"/api/posts/{post_id}/like")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_like_missing_post_returns_not_found(client: AsyncClient):
    await create_test_user(client)
    headers = auth_header(await login_user(client))

    response = await client.post("/api/posts/999999/like", headers=headers)
    assert response.status_code == 404
