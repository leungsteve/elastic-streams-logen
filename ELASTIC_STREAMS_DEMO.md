# Elastic Streams Field Extraction Demo

This demo generates realistic log data to demonstrate **Elastic Streams field extraction** capabilities. The logs are sent as raw, unstructured text so you can practice using the Elastic Streams UI to extract meaningful fields.

## What This Demo Shows

The demo generates 10 different types of logs with various formats:

1. **Nginx Access Logs** (Common Log Format) - Practice extracting IPs, status codes, response times
2. **Java Application Logs** (JSON) - Extract log levels, class names, thread IDs  
3. **System Access Logs** (Syslog) - Extract usernames, source IPs, authentication results
4. **E-commerce Transactions** (JSON) - Extract amounts, payment methods, customer IDs
5. **API Gateway Logs** (JSON) - Extract endpoints, response codes, rate limits
6. **Database Query Logs** (Text) - Extract query types, execution times, table names
7. **Docker Container Logs** (JSON) - Extract container names, image versions, statuses
8. **CDN Access Logs** (Text) - Extract regions, cache status, file types
9. **CI/CD Pipeline Logs** (JSON) - Extract build status, stages, repositories
10. **Kubernetes Events** (JSON) - Extract pod names, namespaces, event types

## Starting the Demo

1. **Start log generation:**
   ```bash
   python main.py
   ```

2. **Start Filebeat with RAW configuration:**
   ```bash
   docker run -d --name filebeat-streams \
     -v $(pwd)/filebeat-raw.yml:/usr/share/filebeat/filebeat.yml:ro \
     -v $(pwd)/logs:/usr/share/filebeat/logs:ro \
     docker.elastic.co/beats/filebeat:8.11.0
   ```

3. **Verify logs are flowing:**
   ```bash
   docker logs filebeat-streams --tail 20
   ```

## Using Elastic Streams Field Extraction

1. **Go to Kibana → Observability → Logs → Stream**
2. **Find your data stream:** `logs-streams-demo-default`
3. **Click "Manage stream"**
4. **Go to "Processing" tab**
5. **Add processors to extract fields**

### Example Field Extractions to Try

**Nginx Logs:**
```
192.168.1.100 - - [10/Oct/2023:13:55:36 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0..." rt=0.123 correlation_id="uuid-123"
```
- Use **Dissect** processor: `%{remote_addr} - - [%{timestamp}] "%{method} %{request_uri} %{http_version}" %{status} %{bytes_sent} "%{referrer}" "%{user_agent}" rt=%{response_time} correlation_id="%{correlation_id}"`

**System Access Logs:**
```
Oct 10 13:55:36 web-server-01 sshd[1234]: FAILED login for user admin from 192.168.100.50 port 22 session_id="none" correlation_id="uuid-456"
```
- Use **Grok** processor: `%{SYSLOGTIMESTAMP:timestamp} %{HOSTNAME:hostname} %{WORD:process}: %{WORD:result} %{WORD:action} for user %{USER:user} from %{IP:source_ip}`

**JSON Logs (API Gateway):**
```json
{"timestamp": "2023-10-10T13:55:36.123Z", "method": "POST", "endpoint": "/api/v1/users", "response_code": 201, "client_id": "abc-123"}
```
- Already structured, but you can use **Date** processor to parse timestamps

## Stopping the Demo

```bash
# Stop log generator
# Press Ctrl+C in the python main.py terminal

# Stop and cleanup Filebeat
docker stop filebeat-streams
docker rm filebeat-streams
```

## Key Learning Points

1. **Raw vs Processed Data**: This demo sends raw logs, showing the before/after of field extraction
2. **Multiple Log Formats**: Practice with different formats (JSON, syslog, common log format, custom formats)
3. **Real-time Processing**: See field extraction applied to live data streams
4. **Preview & Testing**: Use Elastic Streams UI to preview extractions before applying
5. **Performance Impact**: Observe how field extraction affects ingestion rates

## What Makes This Different

- **No pre-processing** in Filebeat - all field extraction happens in Elastic Streams UI
- **Realistic data** with correlation IDs, varied formats, and business context
- **Multiple service types** to practice different extraction patterns
- **Continuous generation** for testing extraction performance
- **Built-in scenarios** like security events, business transactions, and system monitoring

This demonstrates Elastic Streams' ability to transform raw, unstructured logs into structured, queryable data without complex pipeline configurations.