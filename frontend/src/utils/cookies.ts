
/**
 * Get cookie by name. Used for getting CSRF token from cookies.
 * Returns empty string if cookie is not found.
 */
export function getCookie(name: string): string {
    let cookieValue = '';
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Fetch new CSRF token from server. Used when CSRF token is expired.
 */
export async function fetchNewToken(): Promise<void> {
    await fetch('api/csrf/', { credentials: 'include' });
}