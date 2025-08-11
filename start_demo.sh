#!/bin/bash
echo "Starting Elastic Streams Field Extraction Demo..."

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

# Start Filebeat with RAW configuration (no field extraction)
echo "Starting Filebeat with raw log configuration..."
docker run -d --name filebeat-streams \
  --env ELASTICSEARCH_HOST="$ELASTICSEARCH_HOST" \
  --env ELASTICSEARCH_API_KEY="$ELASTICSEARCH_API_KEY" \
  -v $(pwd)/filebeat-raw.yml:/usr/share/filebeat/filebeat.yml:ro \
  -v $(pwd)/logs:/usr/share/filebeat/logs:ro \
  docker.elastic.co/beats/filebeat:8.11.0

echo ""
echo "✅ Elastic Streams Demo Started!"
echo ""
echo "📊 Generating ~30 logs/second across 10 service types"
echo "📝 Logs sent as RAW data to: logs-streams-demo-default"
echo ""
echo "🔧 Next Steps:"
echo "1. Go to Kibana → Observability → Logs → Stream"
echo "2. Find data stream: logs-streams-demo-default"
echo "3. Click 'Manage stream' → 'Processing' tab"
echo "4. Add processors to extract fields!"
echo ""
echo "📖 See ELASTIC_STREAMS_DEMO.md for field extraction examples"
echo ""
echo "🛑 Stop demo with:"
echo "   kill $LOG_PID && docker stop filebeat-streams && docker rm filebeat-streams"