import { Ref } from "vue/dist/vue.js";


/**
 * Utility function to get a value from localStorage and parse it as JSON.
 * @param key The key of the item to retrieve from localStorage.
 * @returns The parsed value from localStorage, or null if the key does not exist or parsing fails.
 */
export function getLocal(key: string): any {
    try {
        return JSON.parse(localStorage.getItem(key) || 'null');
    } catch (error) {
        console.error(`Error parsing localStorage item with key "${key}":`, error);
        return null;
    }
}

/**
 * Utility function to set a value in localStorage after stringifying it as JSON.
 * @param key The key of the item to store in localStorage.
 * @param value The value to store in localStorage.
 */
export function setLocal(key: string, value: any): void {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.error(`Error setting localStorage item with key "${key}":`, error);
    }
}

export function setLocalWithRef<T>(key: string, value: T, refValue: Ref<T>): void {
    setLocal(key, value);
    refValue.value = value;
}

export function removeLocalAndNullRef<T>(key: string, refValue: Ref<T | null>): void {
    localStorage.removeItem(key);
    refValue.value = null;
}