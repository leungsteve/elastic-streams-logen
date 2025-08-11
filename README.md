# Elastic Streams Log Generator

A comprehensive log generation tool designed to demonstrate Elastic Streams capabilities with realistic, multi-service log data.

## Overview

This application generates 10 different types of logs that showcase various Elastic Streams features:

### Log Types Generated

1. **Nginx Access Logs** - Common Log Format for field extraction demos
2. **Java Application Logs** - JSON format with structured logging
3. **Kubernetes Logs** - Container orchestration events
4. **System Access Logs** - SSH/authentication events (syslog format)
5. **E-commerce Transaction Logs** - Payment processing events
6. **API Gateway Logs** - Rate limiting and API management
7. **Database Logs** - Query performance and database events
8. **Docker Container Logs** - Container lifecycle events
9. **CDN Logs** - Content delivery and caching events
10. **CI/CD Pipeline Logs** - Build and deployment events

### Key Features

- **Multi-host simulation** with realistic IP addresses and service topology
- **Correlation IDs** for tracing requests across services
- **Security scenarios** including brute force attacks and API abuse
- **Business scenarios** like payment gateway outages and peak hour traffic
- **Configurable rates** and realistic timing patterns
- **Field extraction targets** optimized for Elastic Streams parsing

## Installation

1. Clone this repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your Elastic Cloud connection in `filebeat.yml`:
   ```yaml
   output.elasticsearch:
     hosts: ["<YOUR_ELASTIC_CLOUD_ENDPOINT>"]
     api_key: "<YOUR_API_KEY>"
   ```

## Configuration

Edit `config.yaml` to customize:

- **Log generation rates** (logs per second per type)
- **Infrastructure topology** (hosts, IPs, service mapping)
- **Security attack scenarios** (intensity, source IPs, target endpoints)
- **Business scenarios** (peak hours, failure probabilities)
- **Output formats** and file rotation settings

### Example Configuration Sections

```yaml
# Adjust log generation rates
rates:
  nginx: 5          # 5 logs per second
  java_app: 3       # 3 logs per second
  ecommerce: 2      # 2 logs per second

# Configure attack scenarios
security:
  attack_patterns:
    brute_force:
      enabled: true
      intensity: 0.1    # 10% of login attempts are attacks
      source_ips: 
        - 192.168.100.50
        - 203.0.113.100

# Set business hours multiplier
business:
  peak_hours: 
    start: "09:00"
    end: "17:00" 
    multiplier: 2.5   # 2.5x more logs during business hours
```

## Usage

### Basic Usage

Start generating logs with default configuration:
```bash
python main.py
```

### Custom Configuration

Use a different config file:
```bash
python main.py --config custom-config.yaml
```

### Time-Limited Generation

Run for a specific duration (useful for demos):
```bash
python main.py --duration 300  # Run for 5 minutes
```

### Check Status

View current configuration and file locations:
```bash
python main.py --status
```

## Filebeat Integration

The included `filebeat.yml` configuration is optimized for Elastic Streams:

1. **Different input types** for each log format (JSON vs text parsing)
2. **Pre-configured field extraction** using dissect and grok processors
3. **Data stream routing** to appropriate indices
4. **Field type mappings** for optimal parsing performance

### Starting Filebeat

```bash
filebeat -c filebeat.yml
```

## Elastic Streams Demo Scenarios

### Security Use Case: Brute Force Detection

1. Enable brute force attacks in config:
   ```yaml
   security:
     attack_patterns:
       brute_force:
         enabled: true
         intensity: 0.2  # 20% attack rate
   ```

2. In Elastic Streams, extract fields:
   - `source_ip` from system access logs
   - `result` (SUCCESS/FAILED) from authentication events
   - `user` from login attempts

3. Create visualizations showing:
   - Failed login attempts by source IP over time
   - Successful vs failed authentication rates
   - Geographic distribution of attack sources

### Business Use Case: Payment Processing Analysis

1. Configure payment gateway outages:
   ```yaml
   business:
     failure_scenarios:
       payment_gateway_outage:
         probability: 0.05  # 5% of transactions fail
   ```

2. Extract fields from e-commerce logs:
   - `amount` for revenue impact calculation
   - `payment_method` for method-specific analysis
   - `error_code` for failure categorization
   - `processing_time` for performance monitoring

3. Correlate with nginx logs using `correlation_id` to track user journey:
   - Shopping cart → Payment attempt → Transaction result

### Multi-Service Correlation Example

Track a complete user transaction across services:

1. **Nginx**: User visits `/checkout` page
2. **Java App**: Payment service processes transaction
3. **API Gateway**: Rate limiting and authentication
4. **Database**: Transaction storage and query performance
5. **E-commerce**: Final transaction result

All logs share the same `correlation_id` for easy tracing.

## Log File Structure

```
logs/
├── nginx/           # Web server access logs
├── java_app/        # Application logs (JSON)
├── kubernetes/      # K8s events (JSON)
├── system_access/   # SSH/auth logs (syslog)
├── ecommerce/       # Transaction logs (JSON)
├── api_gateway/     # API management logs (JSON)
├── database/        # DB query logs (text)
├── docker/          # Container events (JSON)
├── cdn/             # CDN access logs (text)
└── cicd/            # Build pipeline logs (JSON)
```

## Field Extraction Examples

### Nginx Log Parsing
```
# Raw log line:
192.168.1.100 - - [10/Oct/2023:13:55:36 +0000] "GET /api/users HTTP/1.1" 200 1234 "-" "Mozilla/5.0..." rt=0.123 correlation_id="uuid-123"

# Extracted fields:
- remote_addr: 192.168.1.100
- method: GET
- request_uri: /api/users
- status: 200
- response_time: 0.123
- correlation_id: uuid-123
```

### System Access Log Parsing
```
# Raw log line:
Oct 10 13:55:36 web-server-01 sshd[1234]: FAILED login for user admin from 192.168.100.50 port 22 session_id="none" correlation_id="uuid-456"

# Extracted fields:
- user: admin
- source_ip: 192.168.100.50
- action: login
- result: FAILED
- session_id: none
- correlation_id: uuid-456
```

## Customization

### Adding New Log Types

1. Create a new generator class in `log_generators.py`
2. Add configuration to `config.yaml`
3. Update the orchestrator in `main.py`
4. Add corresponding Filebeat input configuration

### Modifying Security Scenarios

Edit the `_is_attack_request()` methods in generator classes to implement custom attack patterns.

### Adjusting Business Logic

Modify the `_is_peak_hours()` and failure scenario logic to match your demonstration needs.

## Troubleshooting

### Common Issues

1. **Permission denied on log files**: Ensure write permissions in the logs directory
2. **High CPU usage**: Reduce log generation rates in config.yaml
3. **Filebeat connection issues**: Verify Elastic Cloud endpoint and API key

### Log File Locations

- Application logs: `generator.log`
- Generated logs: `./logs/<log_type>/`
- Filebeat logs: `/var/log/filebeat/` (configurable)

## Performance Notes

- Default configuration generates ~30 logs/second across all types
- Each log type can be independently configured
- File rotation prevents disk space issues
- Peak hours multiplier simulates realistic traffic patterns

## License

This project is for demonstration purposes with Elastic Stack.