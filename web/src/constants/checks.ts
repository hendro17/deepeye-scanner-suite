export interface CheckCategory {
  id: string;
  name: string;
  checks: string[];
}

export const CHECK_CATEGORIES: CheckCategory[] = [
  {
    id: "injection",
    name: "Injection",
    checks: [
      "sql_injection",
      "xss",
      "stored_xss",
      "command_injection",
      "nosql_injection",
      "ldap_injection",
      "xml_injection",
      "ssti",
      "ssti_engines",
      "crlf_injection",
      "crlf_header_inject_deep",
      "sse_injection",
    ],
  },
  {
    id: "ssrf_path_traversal",
    name: "SSRF & Path Traversal",
    checks: ["ssrf", "ssrf_cloud", "path_traversal", "lfi", "rfi", "open_redirect", "open_redirect_deep"],
  },
  {
    id: "auth_session",
    name: "Auth & Session",
    checks: [
      "csrf",
      "authentication_bypass",
      "broken_authentication",
      "jwt_vulnerabilities",
      "jwt_deep",
      "oauth_testing",
      "saml_attacks",
    ],
  },
  {
    id: "config_exposure",
    name: "Config & Exposure",
    checks: [
      "security_misconfiguration",
      "information_disclosure",
      "sensitive_data_exposure",
      "cors_misconfiguration",
      "cors_csp",
      "cloud_misconfig",
      "email_injection",
    ],
  },
  {
    id: "xxe_deserialization",
    name: "XXE & Deserialization",
    checks: ["xxe", "insecure_deserialization"],
  },
  {
    id: "http_header_attacks",
    name: "HTTP Header Attacks",
    checks: ["host_header_injection", "host_header_deep", "http_method_override", "http_smuggling", "h2_smuggle"],
  },
  {
    id: "api_graphql",
    name: "API & GraphQL",
    checks: ["api_vulnerabilities", "api_security", "api_bola_deep", "graphql_vulnerabilities", "graphql_deep"],
  },
  {
    id: "business_logic",
    name: "Business Logic",
    checks: ["business_logic", "race_condition", "mass_assignment"],
  },
  {
    id: "file_webshell",
    name: "File & Webshell",
    checks: ["file_upload", "php_webshell"],
  },
  {
    id: "websocket",
    name: "WebSocket",
    checks: ["websocket", "websocket_deep"],
  },
  {
    id: "cache_supply_chain",
    name: "Cache & Supply Chain",
    checks: ["cache_poisoning", "cache_deception", "supply_chain_js"],
  },
  {
    id: "recon_discovery",
    name: "Recon & Discovery",
    checks: ["directory_bruteforce", "port_scanner", "subdomain_takeover", "waf_fingerprint"],
  },
  {
    id: "mobile",
    name: "Mobile",
    checks: ["frida_mobile", "android_static", "ios_plist", "mobile_ssl_pinning", "mobile_ai_chain"],
  },
  {
    id: "specialized",
    name: "Specialized",
    checks: ["anomaly_detector", "secret_scanning", "log4shell"],
  },
  {
    id: "parameter_pollution",
    name: "Parameter Pollution",
    checks: ["hpp_pollution"],
  },
];

export const ALL_CHECKS: string[] = CHECK_CATEGORIES.flatMap((c) => c.checks);

export type PresetId = "quick" | "full" | "api_focus" | "custom";

export const QUICK_SCAN_CHECKS: string[] = [
  "sql_injection",
  "xss",
  "stored_xss",
  "command_injection",
  "csrf",
  "path_traversal",
  "open_redirect",
  "security_misconfiguration",
  "information_disclosure",
  "cors_misconfiguration",
];

export const API_FOCUS_CATEGORY_IDS: string[] = ["injection", "api_graphql"];

export function presetChecks(preset: PresetId): string[] {
  if (preset === "full") return [...ALL_CHECKS];
  if (preset === "api_focus")
    return CHECK_CATEGORIES.filter((c) => API_FOCUS_CATEGORY_IDS.includes(c.id)).flatMap((c) => c.checks);
  if (preset === "quick") return [...QUICK_SCAN_CHECKS];
  return [];
}

const ACRONYM_TOKENS = new Set([
  "sql",
  "nosql",
  "xss",
  "ssrf",
  "lfi",
  "rfi",
  "crlf",
  "ssti",
  "sse",
  "ldap",
  "csrf",
  "jwt",
  "oauth",
  "saml",
  "xxe",
  "api",
  "cors",
  "csp",
  "php",
  "js",
  "hpp",
  "waf",
  "ai",
]);

function formatToken(token: string): string {
  if (token === "ios") {
    return "iOS";
  }
  if (ACRONYM_TOKENS.has(token)) {
    return token.toUpperCase();
  }
  return token.charAt(0).toUpperCase() + token.slice(1);
}

export function checkLabel(id: string): string {
  return id
    .split("_")
    .map(formatToken)
    .join(" ");
}
