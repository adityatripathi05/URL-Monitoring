# URL Monitoring System

This is a URL monitoring system built with FastAPI, React, TimescaleDB, and Telegraf. It is designed to monitor thousands of URLs simultaneously with minimal performance impact.

## Architecture

```mermaid
graph TD
  subgraph Monitoring
    Telegraf[Telegraf Agent]
    URL1[Monitored URL 1]
    URL2[Monitored URL 2]
    URL3[Monitored URL 3]
    Telegraf -->|Collect Metrics via inputs.http_response| URL1
    Telegraf --> URL2
    Telegraf --> URL3
  end

  subgraph Web_API_Layer
    Nginx[Nginx - Reverse Proxy]
    Gunicorn[Gunicorn App Server]
    FastAPI[FastAPI Backend]
    Nginx --> Gunicorn
    Gunicorn --> FastAPI
    FastAPI -->|Serve Target URLs| Telegraf
  end

  subgraph Data_Storage
    TimescaleDB[(TimescaleDB)]
    Telegraf -->|Send Metrics via outputs.postgresql| TimescaleDB
    FastAPI -->|Store Metadata| TimescaleDB
    FastAPI <-->|Query Metrics| TimescaleDB
  end

  subgraph Visualization
    React[React Frontend]
    React -->|API Requests| Nginx
  end
```

## Components

*   **FastAPI Backend**: Provides the API endpoints for managing URLs, retrieving monitoring data, and configuring the system.
*   **React Frontend**: Provides a user interface for visualizing the monitoring data and managing the system.
*   **TimescaleDB**: Stores the time-series data for the monitored URLs.
*   **Telegraf**: Collects the monitoring data from the URLs.
*   **Docker**: Containerizes the application for easy deployment.
*   **Docker Compose**: Orchestrates the different services of the application.

## Getting Started

1.  Install Docker and Docker Compose.
2.  Clone the repository.
3.  Run `docker-compose up --build` to start the application.
