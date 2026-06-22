import { getAuthHeaders } from "/static/js/auth.js?v=2";
import { getErrorMessage, showModal } from "/static/js/utils.js?v=3";

function showLikeError(message) {
  const errorMessage = document.getElementById("errorMessage");
  if (errorMessage && document.getElementById("errorModal")) {
    errorMessage.textContent = message;
    showModal("errorModal");
  }
}

function setButtonState(button, liked, likes) {
  button.classList.toggle("btn-primary", liked);
  button.classList.toggle("btn-outline-secondary", !liked);
  button.setAttribute("aria-pressed", String(liked));
  button.setAttribute("aria-label", liked ? "Unlike this post" : "Like this post");
  button.querySelector(".like-icon").textContent = liked ? "♥" : "♡";
  button.querySelector(".like-count").textContent = likes;
}

async function loadLikedState(buttons) {
  const url = new URL("/api/posts/likes/me", window.location.origin);
  buttons.forEach((button) => {
    url.searchParams.append("post_ids", button.dataset.likePostId);
  });

  try {
    const response = await fetch(url, {
      headers: getAuthHeaders(),
    });
    if (!response.ok) return;
    const likedIds = new Set((await response.json()).post_ids.map(String));
    buttons.forEach((button) => {
      setButtonState(
        button,
        likedIds.has(button.dataset.likePostId),
        button.querySelector(".like-count").textContent,
      );
    });
  } catch (error) {
    console.error("Unable to load like status:", error);
  }
}

export function initializeLikeButtons(root = document) {
  const buttons = [...root.querySelectorAll(".like-button:not([data-like-ready])")];
  if (!buttons.length) return;

  buttons.forEach((button) => {
    button.dataset.likeReady = "true";
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        const response = await fetch(
          `/api/posts/${button.dataset.likePostId}/like`,
          {
            method: "POST",
            headers: getAuthHeaders(),
          },
        );
        if (response.status === 401) {
          window.location.href = "/login";
          return;
        }
        if (!response.ok) {
          const error = await response.json().catch(() => ({}));
          throw new Error(getErrorMessage(error));
        }
        const data = await response.json();
        document
          .querySelectorAll(`[data-like-post-id="${data.post_id}"]`)
          .forEach((matchingButton) => {
            setButtonState(matchingButton, data.liked, data.likes);
          });
      } catch (error) {
        console.error("Unable to update like:", error);
        showLikeError(error.message || "Unable to update like. Please try again.");
      } finally {
        button.disabled = false;
      }
    });
  });

  loadLikedState(buttons);
}

export function likeButtonHtml(post) {
  return `
    <button type="button"
            class="btn btn-sm btn-outline-secondary like-button"
            data-like-post-id="${post.id}"
            aria-pressed="false"
            aria-label="Like this post">
      <span class="like-icon" aria-hidden="true">♡</span>
      <span class="like-count">${post.likes}</span>
    </button>`;
}

export function commentCountHtml(post) {
  return `
    <a class="btn btn-sm btn-outline-secondary"
       href="/posts/${post.id}#comments"
       aria-label="View comments">
      <span aria-hidden="true">💬</span>
      <span>${post.comments_count}</span>
    </a>`;
}
