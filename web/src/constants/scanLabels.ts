export const ALL_REPORT_FORMATS = [
  "html",
  "pdf",
  "json",
  "sarif",
  "junit",
  "csv",
  "xlsx",
] as const;

export const AUTH_MODE = {
  NONE: "none",
  COOKIE_HEADERS: "cookie_headers",
  FORM_LOGIN: "form_login",
} as const;

export const PRESET_IDS = {
  QUICK: "quick",
  FULL: "full",
  API_FOCUS: "api_focus",
  CUSTOM: "custom",
} as const;

export const PRESET_LIST = [
  PRESET_IDS.QUICK,
  PRESET_IDS.FULL,
  PRESET_IDS.API_FOCUS,
] as const;

export const LOGIN_FIELD_DEFAULTS = {
  USERNAME: "username",
  PASSWORD: "password",
} as const;

export const PLACEHOLDERS = {
  TARGET: "https://example.com",
  TARGET_LOGIN: "https://example.com/login",
  SCOPE: "Focus on authentication and API endpoints",
  AUTH_HEADERS: '{"Authorization": "Bearer xxx"} atau\nAuthorization: Bearer xxx',
  AUTH_COOKIES: '{"session": "abc123"} atau\nsession=abc123',
  USERNAME: "admin@example.com",
  PASSWORD: "••••••••",
  USERNAME_FIELD: "username",
  PASSWORD_FIELD: "password",
} as const;

export const ERR_PREFIX = "Failed: ";
export const ERR_SPEC_PREFIX = "Failed to parse spec: ";

export const SEPARATORS = {
  SPACE: " ",
  NEWLINE: "\n",
  COLON: ":",
  EQUALS: "=",
} as const;

export const SCOPE_PREFIX = "only ";

export function scanRoute(id: string | number): string {
  return `/scan/${String(id)}/live`;
}
