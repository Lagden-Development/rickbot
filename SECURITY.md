# Security Policy

## Overview

RickBot handles sensitive data including Discord bot tokens, MongoDB credentials, and potentially user data. This document outlines security best practices and guidelines.

## Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Instead, please report security issues privately:
1. Email security concerns to the repository maintainers
2. Include detailed information about the vulnerability
3. Allow reasonable time for a fix before public disclosure

## Credential Management

### Discord Bot Token

**Critical:** Your Discord bot token provides full access to your bot account.

#### Best Practices

- **NEVER** commit your token to version control
- **NEVER** share your token publicly (Discord, forums, screenshots, etc.)
- **NEVER** hardcode tokens in your source code
- **ALWAYS** use environment variables (`.env` file)
- **ALWAYS** regenerate tokens if exposed
- **ROTATE** tokens periodically (every 90 days recommended)

#### Token Storage

✅ **CORRECT:**
```env
# .env file (in .gitignore)
DISCORD_TOKEN=your_token_here
```

```yaml
# config.yaml
bot:
  token: ${DISCORD_TOKEN}  # References environment variable
```

❌ **INCORRECT:**
```python
# NEVER DO THIS!
token = "MTQyODg5NjE4NDk1MjQyMjU0Mg.G6tZ7g...."
```

#### If Your Token is Exposed

1. **Immediately** go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Navigate to your application → Bot
3. Click "Regenerate" next to the token
4. Update your `.env` file with the new token
5. Restart your bot
6. Review audit logs for unauthorized actions

### MongoDB Credentials

MongoDB credentials provide access to all your bot's data.

#### Best Practices

- Use **strong, unique passwords** (20+ characters)
- Enable **authentication** on MongoDB
- Use **IP whitelisting** when possible
- Enable **SSL/TLS** for connections
- Create **dedicated database users** per environment
- Grant **minimum required permissions** (principle of least privilege)
- **Rotate credentials** every 90 days

#### MongoDB Connection Strings

✅ **CORRECT:**
```env
# .env file
MONGO_URI=mongodb://username:password@localhost:27017/dbname
```

❌ **INCORRECT:**
```yaml
# config.yaml - NEVER put credentials directly here!
mongodb:
  uri: "mongodb://admin:password123@localhost:27017"
```

#### MongoDB Atlas Security

If using MongoDB Atlas:

1. Enable **IP Access List** (whitelist only your server IPs)
2. Use **VPC Peering** for production deployments
3. Enable **Encryption at Rest**
4. Enable **Audit Logs**
5. Use **M10+ clusters** for production (automatic backups)
6. Enable **Two-Factor Authentication** on Atlas account

### Environment Variables

The `.env` file contains all sensitive credentials.

#### File Security

```bash
# Correct file permissions (Linux/macOS)
chmod 600 .env  # Only owner can read/write
```

#### .gitignore

Verify `.env` is in `.gitignore`:

```gitignore
# Environment files
.env
.env.local
.env.production

# Configuration (may contain app IDs)
config.yaml
```

#### Template Files

Provide `.env.example` and `config.yaml.example` with **no real credentials**:

```env
# .env.example
DISCORD_TOKEN=your_discord_bot_token_here
MONGO_URI=mongodb://username:password@localhost:27017/database
```

## Data Privacy

### Personally Identifiable Information (PII)

The bot logs command executions which may contain PII:
- User IDs
- Usernames
- Guild IDs
- Command arguments (could be anything!)

#### Configuration

```yaml
observability:
  track_command_args: true  # ⚠️ SET TO FALSE IF HANDLING SENSITIVE DATA
```

If your bot handles sensitive data (passwords, emails, etc.), set `track_command_args: false`.

#### Data Retention

Implement data retention policies:

```javascript
// Example MongoDB TTL index (30 days)
db.command_logs.createIndex(
  { "executed_at": 1 },
  { expireAfterSeconds: 2592000 }  // 30 days
)
```

#### GDPR Compliance

If your bot has European users:

1. Provide a privacy policy
2. Implement data deletion requests
3. Allow users to export their data
4. Obtain consent for data collection
5. Encrypt sensitive data at rest

### Error Logging

Error logs include:
- Stack traces (may reveal code internals)
- User IDs and interaction data
- Potentially sensitive arguments

#### Best Practices

- Set `store_error_traceback: false` in production if concerned about leaks
- Regularly review and purge error logs
- Restrict access to `/errors` command (owner-only)

## Discord Intents

Request only the intents you need.

### Privileged Intents

These require explicit approval from Discord:

| Intent | Risk Level | Use Case |
|--------|------------|----------|
| `message_content` | **HIGH** | Reading message content |
| `members` | **MEDIUM** | Accessing member data |
| `presences` | **MEDIUM** | Tracking online status |

**Note:** Slash-command-only bots **DO NOT** need `message_content` intent.

#### Configuration

```yaml
intents:
  message_content: false  # Only enable if absolutely necessary
  members: false          # Only enable for member-specific features
  presences: false        # Only enable for status tracking
```

## Application Security

### Command Permissions

Restrict dangerous commands:

```python
@app_commands.command()
@app_commands.default_permissions(administrator=True)
async def dangerous_command(self, interaction):
    # Only admins can see/use this
    pass
```

### Owner-Only Commands

Use the `@is_owner()` check:

```python
from helpers.checks import is_owner

@app_commands.command()
@is_owner()
async def reload(self, interaction):
    # Only bot owners can use this
    pass
```

### Input Validation

Always validate user input:

```python
@app_commands.command()
async def ban(self, interaction, user_id: str):
    # Validate input
    try:
        user_id_int = int(user_id)
        if user_id_int < 0:
            raise ValueError("Invalid user ID")
    except ValueError:
        await interaction.response.send_message("❌ Invalid user ID!")
        return

    # Proceed with ban...
```

### Rate Limiting

Discord.py handles API rate limiting, but implement application-level limits for resource-intensive operations:

```python
from discord.ext import commands

@commands.cooldown(1, 60, commands.BucketType.user)
@app_commands.command()
async def expensive_command(self, interaction):
    # Limited to once per minute per user
    pass
```

## Production Deployment

### Pre-Deployment Checklist

- [ ] Regenerate all credentials (fresh tokens/passwords for production)
- [ ] Verify `.env` and `config.yaml` are in `.gitignore`
- [ ] Set `track_command_args: false` if handling sensitive data
- [ ] Enable only required Discord intents
- [ ] Set appropriate owner IDs in config
- [ ] Use production MongoDB with authentication
- [ ] Enable MongoDB SSL/TLS
- [ ] Implement IP whitelisting
- [ ] Set up automated backups
- [ ] Configure monitoring and alerts
- [ ] Review and test error handling
- [ ] Implement logging rotation
- [ ] Set up firewall rules
- [ ] Use reverse proxy (if applicable)
- [ ] Enable HTTPS for webhooks (if applicable)

### Environment Separation

Use separate environments for development, staging, and production:

```bash
# Development
.env.development

# Staging
.env.staging

# Production
.env.production
```

**NEVER** use production credentials in development!

### Server Security

#### Firewall Configuration

Only expose necessary ports:
- MongoDB: `27017` (localhost only or IP-whitelisted)
- HTTPS: `443` (if using webhooks)

```bash
# Example UFW rules (Ubuntu)
sudo ufw default deny incoming
sudo ufw allow ssh
sudo ufw enable
```

#### Process Management

Use a process manager to automatically restart the bot:

**systemd (Linux):**
```ini
[Unit]
Description=RickBot Discord Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/opt/rickbot
Environment="PATH=/opt/rickbot/.venv/bin"
ExecStart=/opt/rickbot/.venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**PM2 (Cross-platform):**
```bash
pm2 start app.py --name rickbot --interpreter python3
pm2 save
pm2 startup
```

### Monitoring

Implement monitoring for:
- Bot uptime
- Memory usage
- Error rates
- Command execution times
- Database connection health
- Unauthorized access attempts

Use the built-in `/metrics` and `/errors` commands for real-time monitoring.

## Code Security

### Dependency Management

Keep dependencies up to date:

```bash
pip list --outdated
pip install --upgrade <package>
```

### Security Scanning

Use tools to scan for vulnerabilities:

```bash
# Install safety
pip install safety

# Scan dependencies
safety check
```

### Code Review

- Review all code changes for security issues
- Never execute arbitrary code from users
- Sanitize all user inputs
- Use parameterized queries (Pydantic models prevent injection)

### Secrets Scanning

Before committing:

```bash
# Install git-secrets
git secrets --install
git secrets --register-aws

# Scan for secrets
git secrets --scan
```

## Incident Response

### If Credentials are Compromised

1. **Immediately** rotate all affected credentials
2. Review audit logs for unauthorized actions
3. Check database for suspicious modifications
4. Notify affected users if PII was exposed
5. Document the incident
6. Implement preventive measures

### If the Bot is Compromised

1. **Immediately** shut down the bot
2. Revoke all tokens and credentials
3. Review all code for malicious changes
4. Check database for unauthorized access
5. Restore from known-good backup
6. Investigate how compromise occurred
7. Implement fixes and security improvements
8. Redeploy with new credentials

## Additional Resources

- [Discord Security Best Practices](https://discord.com/safety)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [MongoDB Security Checklist](https://www.mongodb.com/docs/manual/administration/security-checklist/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-XX | Initial security policy |

---

**Remember: Security is not a one-time task, it's an ongoing process.**
