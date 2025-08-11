#!/usr/bin/env python3

import os
import sys
import yaml
import json
import time
import threading
import logging
from datetime import datetime, time as dt_time
from typing import Dict, Any, List
from pathlib import Path
import click
from concurrent.futures import ThreadPoolExecutor
import signal

from log_generators import (
    NginxLogGenerator, JavaAppLogGenerator, KubernetesLogGenerator,
    SystemAccessLogGenerator, EcommerceLogGenerator, APIGatewayLogGenerator,
    DatabaseLogGenerator, DockerLogGenerator, CDNLogGenerator, CICDLogGenerator
)

class LogGeneratorOrchestrator:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.generators = {}
        self.running = False
        self.executor = None
        self.log_files = {}
        
        self._setup_logging()
        self._initialize_generators()
        self._create_output_directories()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('generator.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _initialize_generators(self):
        generator_classes = {
            'nginx': NginxLogGenerator,
            'java_app': JavaAppLogGenerator,
            'kubernetes': KubernetesLogGenerator,
            'system_access': SystemAccessLogGenerator,
            'ecommerce': EcommerceLogGenerator,
            'api_gateway': APIGatewayLogGenerator,
            'database': DatabaseLogGenerator,
            'docker': DockerLogGenerator,
            'cdn': CDNLogGenerator,
            'cicd': CICDLogGenerator
        }
        
        for log_type, generator_class in generator_classes.items():
            if log_type in self.config['log_generator']['rates']:
                self.generators[log_type] = generator_class(self.config['log_generator'])
                self.logger.info(f"Initialized {log_type} generator")
    
    def _create_output_directories(self):
        base_dir = Path(self.config['log_generator']['output']['base_directory'])
        base_dir.mkdir(exist_ok=True)
        
        for log_type in self.generators.keys():
            log_dir = base_dir / log_type
            log_dir.mkdir(exist_ok=True)
            
            # Create log file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{log_type}_{timestamp}.log"
            file_path = log_dir / filename
            
            self.log_files[log_type] = {
                'path': file_path,
                'handle': open(file_path, 'a', encoding='utf-8'),
                'size': 0
            }
            
            self.logger.info(f"Created log file: {file_path}")
    
    def _is_peak_hours(self) -> bool:
        now = datetime.now().time()
        peak_config = self.config['log_generator']['business']['peak_hours']
        start_time = dt_time.fromisoformat(peak_config['start'])
        end_time = dt_time.fromisoformat(peak_config['end'])
        return start_time <= now <= end_time
    
    def _get_adjusted_rate(self, log_type: str) -> float:
        base_rate = self.config['log_generator']['rates'][log_type]
        if self._is_peak_hours():
            multiplier = self.config['log_generator']['business']['peak_hours']['multiplier']
            return base_rate * multiplier
        return base_rate
    
    def _get_host_for_service(self, log_type: str) -> Dict[str, Any]:
        hosts = self.config['log_generator']['infrastructure']['hosts']
        eligible_hosts = [host for host in hosts if log_type in host['services']]
        
        if not eligible_hosts:
            # Fallback to first host
            return hosts[0]
        
        import random
        return random.choice(eligible_hosts)
    
    def _write_log_entry(self, log_type: str, log_entry: Dict[str, Any]):
        if log_type not in self.log_files:
            return
            
        file_info = self.log_files[log_type]
        log_line = log_entry['log_line']
        
        # Write to file
        file_info['handle'].write(log_line + '\n')
        file_info['handle'].flush()
        file_info['size'] += len(log_line) + 1
        
        # Check for rotation
        max_size_bytes = self.config['log_generator']['output']['file_rotation']['max_size_mb'] * 1024 * 1024
        if file_info['size'] > max_size_bytes:
            self._rotate_log_file(log_type)
    
    def _rotate_log_file(self, log_type: str):
        file_info = self.log_files[log_type]
        file_info['handle'].close()
        
        # Create new file
        base_dir = Path(self.config['log_generator']['output']['base_directory'])
        log_dir = base_dir / log_type
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{log_type}_{timestamp}.log"
        file_path = log_dir / filename
        
        self.log_files[log_type] = {
            'path': file_path,
            'handle': open(file_path, 'a', encoding='utf-8'),
            'size': 0
        }
        
        self.logger.info(f"Rotated log file: {file_path}")
    
    def _generate_logs_for_type(self, log_type: str):
        generator = self.generators[log_type]
        
        while self.running:
            try:
                rate = self._get_adjusted_rate(log_type)
                if rate <= 0:
                    time.sleep(1)
                    continue
                
                # Calculate sleep time between logs
                sleep_time = 1.0 / rate if rate > 0 else 1.0
                
                # Get appropriate host for this service
                host_info = self._get_host_for_service(log_type)
                
                # Generate log entry
                log_entry = generator.generate_log(host_info)
                
                # Write to file
                self._write_log_entry(log_type, log_entry)
                
                # Sleep until next log
                time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"Error generating {log_type} log: {e}")
                time.sleep(1)
    
    def start(self):
        if self.running:
            self.logger.warning("Generator is already running")
            return
        
        self.running = True
        self.logger.info("Starting log generation...")
        
        # Start thread pool
        max_workers = len(self.generators)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Start generator for each log type
        futures = []
        for log_type in self.generators.keys():
            future = self.executor.submit(self._generate_logs_for_type, log_type)
            futures.append(future)
            self.logger.info(f"Started generator for {log_type}")
        
        self.logger.info("All generators started. Press Ctrl+C to stop.")
        
        try:
            # Wait for interruption
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        finally:
            self.stop()
    
    def stop(self):
        if not self.running:
            return
        
        self.logger.info("Stopping log generation...")
        self.running = False
        
        if self.executor:
            self.executor.shutdown(wait=True)
        
        # Close all log files
        for log_type, file_info in self.log_files.items():
            file_info['handle'].close()
            self.logger.info(f"Closed log file for {log_type}")
        
        self.logger.info("Log generation stopped")
    
    def status(self):
        """Print current status of the generator"""
        print(f"\n{'='*50}")
        print(f"LOG GENERATOR STATUS")
        print(f"{'='*50}")
        print(f"Running: {self.running}")
        print(f"Peak Hours: {self._is_peak_hours()}")
        print(f"\nCONFIGURED LOG TYPES:")
        
        for log_type, rate in self.config['log_generator']['rates'].items():
            adjusted_rate = self._get_adjusted_rate(log_type)
            print(f"  {log_type:15} - {rate:4.1f}/s (adjusted: {adjusted_rate:4.1f}/s)")
        
        print(f"\nOUTPUT FILES:")
        for log_type, file_info in self.log_files.items():
            size_mb = file_info['size'] / (1024 * 1024)
            print(f"  {log_type:15} - {file_info['path']} ({size_mb:.2f} MB)")
        
        print(f"\nHOST SIMULATION:")
        for host in self.config['log_generator']['infrastructure']['hosts']:
            services = ', '.join(host['services'])
            print(f"  {host['name']:15} ({host['ip']}) - {services}")

@click.command()
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
@click.option('--status', '-s', is_flag=True, help='Show status and exit')
@click.option('--duration', '-d', type=int, help='Run for specified seconds then stop')
def main(config, status, duration):
    """
    Elastic Streams Log Generator
    
    Generates realistic logs for demonstrating Elastic Streams capabilities.
    Supports multiple log types with configurable rates and security scenarios.
    """
    
    if not os.path.exists(config):
        click.echo(f"Configuration file not found: {config}", err=True)
        sys.exit(1)
    
    orchestrator = LogGeneratorOrchestrator(config)
    
    if status:
        orchestrator.status()
        return
    
    # Setup signal handler for graceful shutdown
    def signal_handler(signum, frame):
        click.echo("\nReceived shutdown signal...")
        orchestrator.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    click.echo("Starting Elastic Streams Log Generator...")
    click.echo(f"Configuration: {config}")
    
    if duration:
        click.echo(f"Will run for {duration} seconds")
        # Start in background thread
        generator_thread = threading.Thread(target=orchestrator.start)
        generator_thread.daemon = True
        generator_thread.start()
        
        # Wait for duration
        time.sleep(duration)
        orchestrator.stop()
        click.echo(f"Stopped after {duration} seconds")
    else:
        orchestrator.start()

if __name__ == '__main__':
    main()