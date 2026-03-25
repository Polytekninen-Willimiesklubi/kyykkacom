import { getCookie, fetchNewToken } from './cookies';

type PayLoad = Record<string, any> | undefined;

export async function fetchWrapper(
    url: string,
    postData?: Record<string, any>,
    method?: string,
    getOnlyPayload?: false,
): Promise<Response>

export async function fetchWrapper(
    url: string,
    postData: Record<string, any>,
    method: string,
    getOnlyPayload: true,
): Promise<PayLoad>


export async function fetchWrapper(
    url: string,
    postData: Record<string, any> = {},
    method: string = 'GET',
    getOnlyPayload: boolean = false,
): Promise<PayLoad | Response> {
    const headers: Record<string, string> = {
        'X-CSRFToken': getCookie('csrftoken'),
        'content-type': 'application/json',
    };
    const requestOpt: RequestInit = {
        method: method,
        headers: headers,
        credentials: 'include',
    }
    if (method === 'GET') {
        requestOpt.body = JSON.stringify(postData);
    }
    try {
        const response = await fetch(url, requestOpt);

        if (!response.ok && response.status === 403) {
            await fetchNewToken();
            headers['X-CSRFToken'] = getCookie('csrftoken');
            requestOpt.headers = headers;
            const secondResponse = await fetch(url, requestOpt);
            if (!secondResponse.ok) {
                console.log("Post request was denied: " + secondResponse);
            }
            return getOnlyPayload ? await getPayload(secondResponse) : secondResponse;
        }
        return getOnlyPayload ? await getPayload(response) : response;
    } catch (error) {
        console.log(error)
        return undefined;
    }
}

export async function getPayload(res: Response): Promise<Record<string, any> | undefined> {
    const isJson = res.headers?.get('content-type')?.includes('application/json');
    const data = (isJson ? await res.json() : null) as Record<string, any> | null;
    return data || undefined;
}