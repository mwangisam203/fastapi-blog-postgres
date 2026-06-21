from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from auth import CurrentUser
import models
from database import get_db
from schemas import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
    LikedPostsResponse,
    LikeResponse,
    PaginatedCommentsResponse,
    PaginatedPostsResponse,
    PostCreate,
    PostResponse,
    PostUpdate,
)

router = APIRouter()


@router.get("", response_model=PaginatedPostsResponse)
async def get_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    announcements_only: bool = False,
):
    filters = [models.Post.is_announcement.is_(True)] if announcements_only else []
    count_result = await db.execute(
        select(func.count()).select_from(models.Post).where(*filters)
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(*filters)
        .order_by(models.Post.date_posted.desc())
        .offset(skip)
        .limit(limit),
    )
    posts = result.scalars().all()

    has_more = skip + len(posts) < total

    return PaginatedPostsResponse(
        posts=[PostResponse.model_validate(post) for post in posts],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    post: PostCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):

    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=current_user.id,
        is_announcement=post.is_announcement,
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["author"])
    return new_post


@router.get("/likes/me", response_model=LikedPostsResponse)
async def get_my_liked_posts(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    post_ids: Annotated[list[int] | None, Query()] = None,
):
    post_ids = post_ids or []
    if len(post_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="A maximum of 100 post IDs is allowed",
        )
    if not post_ids:
        return LikedPostsResponse(post_ids=[])

    result = await db.execute(
        select(models.Like.post_id).where(
            models.Like.user_id == current_user.id,
            models.Like.post_id.in_(set(post_ids)),
        )
    )
    return LikedPostsResponse(post_ids=sorted(result.scalars().all()))


@router.post("/{post_id}/like", response_model=LikeResponse)
async def toggle_post_like(
    post_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Post)
        .where(models.Post.id == post_id)
        .with_for_update()
    )
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    result = await db.execute(
        select(models.Like).where(
            models.Like.post_id == post_id,
            models.Like.user_id == current_user.id,
        )
    )
    existing_like = result.scalars().first()
    if existing_like:
        await db.delete(existing_like)
        liked = False
    else:
        db.add(models.Like(post_id=post_id, user_id=current_user.id))
        liked = True

    await db.flush()
    likes = await db.scalar(
        select(func.count())
        .select_from(models.Like)
        .where(models.Like.post_id == post_id)
    ) or 0
    post.likes = likes
    await db.commit()

    return LikeResponse(post_id=post_id, likes=likes, liked=liked)


## get_post
@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id == post_id),
    )
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


## update_post_full
@router.put("/{post_id}", response_model=PostResponse)
async def update_post_full(
    post_id: int,
    post_data: PostCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized!!",
        )

    post.title = post_data.title
    post.content = post_data.content
    post.is_announcement = post_data.is_announcement

    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post


## update_post_partial
@router.patch("/{post_id}", response_model=PostResponse)
async def update_post_partial(
    post_id: int,
    post_data: PostUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized!!",
        )

    update_data = post_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post


## delete_post
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized!!",
        )

    await db.delete(post)
    await db.commit()


@router.get("/{post_id}/comments", response_model=PaginatedCommentsResponse)
async def get_comments(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    post_exists = await db.scalar(
        select(models.Post.id).where(models.Post.id == post_id)
    )
    if post_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    total = await db.scalar(
        select(func.count())
        .select_from(models.Comment)
        .where(models.Comment.post_id == post_id)
    ) or 0
    result = await db.execute(
        select(models.Comment)
        .options(selectinload(models.Comment.author))
        .where(models.Comment.post_id == post_id)
        .order_by(models.Comment.date_posted.desc(), models.Comment.id.desc())
        .offset(skip)
        .limit(limit)
    )
    comments = result.scalars().all()

    return PaginatedCommentsResponse(
        comments=[CommentResponse.model_validate(comment) for comment in comments],
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(comments) < total,
    )


@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    post_exists = await db.scalar(
        select(models.Post.id).where(models.Post.id == post_id)
    )
    if post_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    comment = models.Comment(
        content=comment_data.content,
        user_id=current_user.id,
        post_id=post_id,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment, attribute_names=["author"])
    return comment


@router.patch("/{post_id}/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    post_id: int,
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Comment).where(
            models.Comment.id == comment_id,
            models.Comment.post_id == post_id,
        )
    )
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this comment",
        )

    comment.content = comment_data.content
    await db.commit()
    await db.refresh(comment, attribute_names=["author"])
    return comment


@router.delete(
    "/{post_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    post_id: int,
    comment_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Comment).where(
            models.Comment.id == comment_id,
            models.Comment.post_id == post_id,
        )
    )
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment",
        )

    await db.delete(comment)
    await db.commit()
