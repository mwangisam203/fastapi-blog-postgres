let currentUser = null;
let fetchPromise = null;

// Bearer headers remain temporarily supported for users with an older session.
export function getAuthHeaders() {
  const legacyToken = localStorage.getItem("access_token");
  return legacyToken ? { Authorization: `Bearer ${legacyToken}` } : {};
}

export async function getCurrentUser() {
  if (currentUser) return currentUser;
  if (fetchPromise) return fetchPromise;

  fetchPromise = (async () => {
    try {
      const response = await fetch("/api/users/me", {
        headers: getAuthHeaders(),
      });
      if (response.ok) {
        currentUser = await response.json();
        return currentUser;
      }
      localStorage.removeItem("access_token");
      return null;
    } catch (error) {
      console.error("Error fetching current user:", error);
      return null;
    } finally {
      fetchPromise = null;
    }
  })();
  return fetchPromise;
}

export async function logout() {
  try {
    await fetch("/api/users/logout", {
      method: "POST",
      headers: getAuthHeaders(),
    });
  } finally {
    localStorage.removeItem("access_token");
    currentUser = null;
    window.location.href = "/";
  }
}

export function clearUserCache() {
  currentUser = null;
}
