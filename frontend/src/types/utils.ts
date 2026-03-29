export type NumericalString = `${number}`;
export type AllOrNone<T> = T | { [K in keyof T]?: never };