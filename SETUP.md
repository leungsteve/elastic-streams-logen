# Setup Guide

## Prerequisites

- Python 3.7+
- Docker
- Elasticsearch cluster with API access

## Initial Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd elastic-streams-logen
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Elasticsearch credentials**
   ```bash
   # Copy the environment template
   cp .env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```bash
   ELASTICSEARCH_HOST=https://your-deployment.es.region.provider.elastic.cloud:443
   ELASTICSEARCH_API_KEY=your_api_key_id:your_api_key_secret
   ```

4. **Make scripts executable**
   ```bash
   chmod +x start_demo.sh
   ```

## Getting Your Elasticsearch Credentials

### Elasticsearch Host
- Go to your Elastic Cloud console
- Find your deployment
- Copy the "Elasticsearch endpoint" 
- Include the full URL with `https://` and port (usually `:443`)

### API Key
1. In Kibana, go to **Stack Management → Security → API Keys**
2. Click **Create API Key**
3. Name it (e.g., "streams-demo")
4. Set privileges:
   ```json
   {
     "cluster": ["monitor"],
     "index": [
       {
         "names": ["logs-streams-demo-*"],
         "privileges": ["create_index", "write", "read"]
       }
     ]
   }
   ```
5. Copy the generated key in `id:secret` format

## Security Best Practices

✅ **Good:**
- Credentials in `.env` file (gitignored)
- Environment variables in Docker containers
- Minimal required permissions for API keys

❌ **Avoid:**
- Hardcoded credentials in config files
- Committing `.env` to version control
- Using overly broad API key permissions

## Verification

Test your setup:
```bash
# Check environment variables
cat .env

# Test connection (optional)
curl -H "Authorization: ApiKey $ELASTICSEARCH_API_KEY" $ELASTICSEARCH_HOST

# Start demo
./start_demo.sh
```

## File Security

- `.env` - **Never commit** (contains secrets)
- `.env.example` - **Safe to commit** (template only)
- `filebeat*.yml` - **Safe to commit** (uses environment variables)

The `.gitignore` file is configured to exclude all sensitive files.