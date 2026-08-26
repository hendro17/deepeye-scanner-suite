export interface SecretPattern {
  id: string;
  label: string;
}

export const SECRET_PATTERNS: SecretPattern[] = [
  { id: "aws_access_key", label: "AWS Access Key" },
  { id: "aws_secret_key", label: "AWS Secret Key" },
  { id: "gcp_service_account", label: "GCP Service Account" },
  { id: "azure_client_secret", label: "Azure Client Secret" },
  { id: "github_token", label: "GitHub Token" },
  { id: "gitlab_token", label: "GitLab Token" },
  { id: "slack_token", label: "Slack Token" },
  { id: "stripe_api_key", label: "Stripe API Key" },
  { id: "twilio_api_key", label: "Twilio API Key" },
  { id: "sendgrid_api_key", label: "SendGrid API Key" },
  { id: "mailgun_api_key", label: "Mailgun API Key" },
  { id: "google_api_key", label: "Google API Key" },
  { id: "openai_api_key", label: "OpenAI API Key" },
  { id: "jwt_secret", label: "JWT Secret" },
  { id: "private_key", label: "Private Key (RSA/SSH)" },
  { id: "database_url", label: "Database URL" },
  { id: "firebase_config", label: "Firebase Config" },
  { id: "npm_token", label: "npm Token" },
  { id: "heroku_api_key", label: "Heroku API Key" },
  { id: "telegram_bot_token", label: "Telegram Bot Token" },
];

export const ALL_SECRET_PATTERNS: string[] = SECRET_PATTERNS.map((p) => p.id);
