#!/bin/bash
echo "Starting Elastic Streams Multi-Service Demo..."

# Check for .env file
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo ""
    echo "Please create a .env file with your Elasticsearch credentials:"
    echo "1. Copy .env.example to .env"
    echo "2. Update ELASTICSEARCH_HOST and ELASTICSEARCH_API_KEY"
    echo ""
    echo "Example:"
    echo "cp .env.example .env"
    echo "# Then edit .env with your actual values"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

# Validate required environment variables
if [ -z "$ELASTICSEARCH_HOST" ] || [ -z "$ELASTICSEARCH_API_KEY" ]; then
    echo "❌ Error: Missing required environment variables!"
    echo ""
    echo "Please check your .env file contains:"
    echo "- ELASTICSEARCH_HOST"
    echo "- ELASTICSEARCH_API_KEY"
    exit 1
fi

echo "✅ Environment variables loaded"

# Start log generator in background
echo "Starting log generator..."
python main.py &
LOG_PID=$!
echo "Log generator started (PID: $LOG_PID)"

# Start Filebeat with MULTI-STREAMS configuration
echo "Starting Filebeat with multi-stream configuration..."

# Stop and remove existing container if it exists
docker stop filebeat-streams 2>/dev/null || true
docker rm filebeat-streams 2>/dev/null || true

docker run -d --name filebeat-streams \
  --env ELASTICSEARCH_HOST="$ELASTICSEARCH_HOST" \
  --env ELASTICSEARCH_API_KEY="$ELASTICSEARCH_API_KEY" \
  -v $(pwd)/filebeat-multi-streams.yml:/usr/share/filebeat/filebeat.yml:ro \
  -v $(pwd)/logs:/usr/share/filebeat/logs:ro \
  docker.elastic.co/beats/filebeat:8.11.0

echo ""
echo "✅ Elastic Streams Multi-Service Demo Started!"
echo ""
echo "📊 Generating ~30 logs/second across 10 service types"
echo "📝 Data streams created for each service:"
echo "   • logs-nginx-demo (Common Log Format)"
echo "   • logs-java-app-demo (JSON structured)"
echo "   • logs-kubernetes-demo (JSON events)"
echo "   • logs-system-access-demo (Syslog format)"
echo "   • logs-ecommerce-demo (JSON transactions)"
echo "   • logs-api-gateway-demo (JSON API logs)"
echo "   • logs-database-demo (Text queries)"
echo "   • logs-docker-demo (JSON container logs)"
echo "   • logs-cdn-demo (Access log format)"
echo "   • logs-cicd-demo (JSON pipeline logs)"
echo ""
echo "🔧 Next Steps in Kibana:"
echo "1. Go to Observability → Logs → Stream"
echo "2. Find each service-specific data stream"
echo "3. Click 'Manage stream' → 'Processing' tab"
echo "4. Add service-appropriate processors:"
echo "   - Nginx: Dissect processor for Common Log Format"
echo "   - System Access: Grok processor for syslog parsing"
echo "   - JSON logs: Already structured, add enrichment"
echo ""
echo "🎯 Demo Benefits:"
echo "• Service-specific field extraction strategies"
echo "• Cleaner processing rules per log type"
echo "• Realistic multi-service architecture"
echo "• Better correlation analysis across services"
echo ""
echo "📖 See ELASTIC_STREAMS_DEMO.md for detailed field extraction examples"
echo ""
echo "🛑 Stop demo with:"
echo "   kill $LOG_PID && docker stop filebeat-streams && docker rm filebeat-streams"