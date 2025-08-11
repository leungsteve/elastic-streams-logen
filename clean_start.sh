#!/bin/bash
echo "🧹 Clean Start for Elastic Streams Demo"
echo "======================================="

# Check for .env file
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please run: cp .env.example .env and configure your credentials"
    exit 1
fi

# Load environment variables
source .env

echo "🗑️  Cleaning up existing demo resources..."

# Stop and remove existing containers
docker stop filebeat-streams 2>/dev/null || true
docker rm filebeat-streams 2>/dev/null || true

# Stop existing log generators
pkill -f "python main.py" 2>/dev/null || true

# Clean local log files
rm -rf logs/
mkdir -p logs/{nginx,java_app,kubernetes,system_access,ecommerce,api_gateway,database,docker,cdn,cicd}

# Delete Elasticsearch index (optional - prompt user)
read -p "🗑️  Delete Elasticsearch index 'logs-streams-demo-default'? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Deleting index..."
    curl -X DELETE \
      -H "Authorization: ApiKey $ELASTICSEARCH_API_KEY" \
      "$ELASTICSEARCH_HOST/logs-streams-demo-default" \
      2>/dev/null || echo "Index may not exist (this is OK)"
    echo "✅ Index deleted"
fi

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "🚀 Starting fresh demo..."

# Start the demo
./start_demo.sh