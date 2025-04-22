# Nginx Setup for Wallet Monitor API

This guide explains how to set up Nginx as a reverse proxy for the Wallet Monitor API with localhost-only access.

## Prerequisites

- Nginx installed on your system
- Python environment with required dependencies

## API Service Setup

1. Edit the systemd service file with your actual paths:

```bash
sudo nano wallet-monitor-api.service
```

2. Replace `/path/to/wallet-monitoring` with your actual project path.

3. Install the service:

```bash
sudo cp wallet-monitor-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable wallet-monitor-api
sudo systemctl start wallet-monitor-api
```

4. Check service status:

```bash
sudo systemctl status wallet-monitor-api
```

## Nginx Setup

1. Copy the Nginx configuration file to the appropriate location:

```bash
# For Ubuntu/Debian
sudo cp wallet-monitor-api.nginx.conf /etc/nginx/sites-available/wallet-monitor-api
sudo ln -s /etc/nginx/sites-available/wallet-monitor-api /etc/nginx/sites-enabled/

# For CentOS/RHEL
sudo cp wallet-monitor-api.nginx.conf /etc/nginx/conf.d/wallet-monitor-api.conf
```

2. Test the Nginx configuration:

```bash
sudo nginx -t
```

3. Restart Nginx to apply changes:

```bash
sudo systemctl restart nginx
```

## Security Features

The provided configuration:

- Listens on port 8080 (can be changed as needed)
- Only allows connections from localhost (127.0.0.1)
- Blocks all other IP addresses
- Sets security headers to help prevent common attacks
- API binds only to 127.0.0.1, not 0.0.0.0, for additional security

## Testing the Setup

To test that the configuration is working properly:

1. Ensure the service is running:
```bash
sudo systemctl status wallet-monitor-api
```

2. Test local access (should work):
```bash
curl http://localhost:8080/
```

3. If you have access to another machine, try accessing from there (should fail):
```bash
curl http://your-server-ip:8080/
```

## Troubleshooting

- Check service logs: `sudo journalctl -u wallet-monitor-api`
- Check Nginx error logs: `/var/log/nginx/error.log`
- Ensure ports are not being blocked by firewall
- Verify API-specific permissions with `sudo -u www-data test_command` 