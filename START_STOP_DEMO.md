# How to Start and Stop the Elastic Streams Demo

This guide shows you how to start and stop the Elastic Streams field extraction demo.

## Prerequisites

1. **Set up credentials** (first time only):
   ```bash
   # Copy the environment template
   cp .env.example .env
   
   # Edit .env with your Elasticsearch credentials
   # Update ELASTICSEARCH_HOST and ELASTICSEARCH_API_KEY
   ```

2. **Make start script executable** (first time only):
   ```bash
   chmod +x start_demo.sh
   ```

## Starting the Demo

### Option 1: Automated Start (Recommended)

```bash
./start_demo.sh
```

The script will:
- Check for `.env` file and validate credentials
- Start the log generator in the background
- Start Filebeat with raw log configuration
- Display next steps and stop instructions

### Option 2: Manual Start

```bash
# 1. Load environment variables
source .env

# 2. Start log generator
python main.py &
LOG_PID=$!

# 3. Start Filebeat with RAW configuration (no field extraction)
docker run -d --name filebeat-streams \
  --env ELASTICSEARCH_HOST="$ELASTICSEARCH_HOST" \
  --env ELASTICSEARCH_API_KEY="$ELASTICSEARCH_API_KEY" \
  -v $(pwd)/filebeat-raw.yml:/usr/share/filebeat/filebeat.yml:ro \
  -v $(pwd)/logs:/usr/share/filebeat/logs:ro \
  docker.elastic.co/beats/filebeat:8.11.0

# 4. Note the log generator PID for stopping later
echo "Log generator PID: $LOG_PID"
```

## Verifying the Demo is Running

### Check Log Generator
```bash
# Check if Python process is running
ps aux | grep "python main.py"

# Check log files are being created
ls -la logs/*/
```

### Check Filebeat
```bash
# Check Filebeat container is running
docker ps | grep filebeat-streams

# Check Filebeat logs
docker logs filebeat-streams --tail 20

# Monitor ingestion (should show events being acknowledged)
docker logs filebeat-streams | grep "acked" | tail -5
```

### Check Elasticsearch
1. Go to **Kibana → Observability → Logs → Stream**
2. Look for data stream: `logs-streams-demo-default`
3. You should see raw, unstructured logs flowing in

## Using Elastic Streams Field Extraction

Once logs are flowing:

1. **Go to Kibana → Observability → Logs → Stream**
2. **Find data stream:** `logs-streams-demo-default`
3. **Click "Manage stream"**
4. **Go to "Processing" tab**
5. **Add processors to extract fields**

See `ELASTIC_STREAMS_DEMO.md` for specific field extraction examples.

## Stopping the Demo

### If Started with Script
The script shows you the exact command when it starts. It will look like:
```bash
kill <PID> && docker stop filebeat-streams && docker rm filebeat-streams
```

### Manual Stop

```bash
# 1. Stop log generator
# If running in foreground: Press Ctrl+C
# If running in background: kill <PID>

# Find the process if you forgot the PID
ps aux | grep "python main.py"
kill <PID>

# 2. Stop and remove Filebeat container
docker stop filebeat-streams
docker rm filebeat-streams

# 3. Verify everything is stopped
docker ps | grep filebeat-streams  # Should return nothing
ps aux | grep "python main.py"     # Should return nothing
```

## Troubleshooting

### Log Generator Not Starting
```bash
# Check Python is available
python --version

# Check required packages
pip install -r requirements.txt

# Check current directory has main.py
ls -la main.py
```

### Filebeat Not Starting
```bash
# Check Docker is running
docker --version

# Check .env file exists and has required variables
cat .env

# Check filebeat-raw.yml exists
ls -la filebeat-raw.yml

# Check logs directory exists
ls -la logs/

# View Filebeat startup errors
docker logs filebeat-streams
```

### No Logs in Elasticsearch
```bash
# Check Filebeat is processing logs
docker logs filebeat-streams | grep "events"

# Check Elasticsearch connection
docker logs filebeat-streams | grep -E "(error|Error|connection)"

# Verify environment variables are loaded
docker exec filebeat-streams env | grep ELASTICSEARCH
```

## What's Running When Demo is Active

- **Log Generator:** Python process generating ~30 logs/second
- **Filebeat Container:** `filebeat-streams` sending raw logs to Elasticsearch  
- **Log Files:** Created in `./logs/` directory (10 different service types)
- **Elasticsearch:** Receiving raw logs in `logs-streams-demo-default` data stream

## Important Notes

- **Raw Logs:** This demo sends unstructured logs for field extraction practice
- **No Pre-processing:** Unlike traditional setups, Filebeat does minimal processing
- **Continuous Generation:** Logs generate continuously until stopped
- **Resource Usage:** Moderate CPU/memory usage for log generation and Docker
- **Data Volume:** ~30 logs/second = ~2,500 logs/minute = ~150,000 logs/hour

## Clean Shutdown Checklist

- [ ] Log generator process stopped
- [ ] Filebeat container stopped and removed
- [ ] No residual processes running
- [ ] Log files can be safely deleted if desired (`rm -rf logs/`)