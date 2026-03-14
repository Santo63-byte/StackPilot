# StackPilot

A simple windows developer tool for managing and launching multiple local development servers with ease. StackPilot provides a unified dashboard to create, configure, start, stop, and monitor multiple development servers from a single interface.

## 🎯 Overviews

StackPilot is designed for windows developers who work with multiple development servers simultaneously. Instead of managing terminals and commands for each server, StackPilot provides an intuitive graphical interface that allows you to:

- Create and manage server configurations
- Start/stop servers with a single click
- Monitor server status and processes
- Manage environment variables and proxy settings
- Integrate with Git repositories
- Execute custom commands in Windows Terminal


## ✨ Key Features

### Core Features
- **Server Management**: Create, read, update, and delete server configurations effortlessly
- **Windows Terminal Integration**: Launch servers directly in Windows Terminal with custom commands
- **Process Monitoring**: Real-time status checking of running server processes
- **Git Branch Detection**: Display current Git branch for repositories
- **Persistent Storage**: All server configurations are stored locally and restored on startup
- **Proxy Control (Custom-addon)**: If configured, helps switch between your different working environments 

### Advanced Features Upcoming
- **Port Management**: Check if specified ports are already in use before launching servers
- **Environment Variable Management**: Configure environment variables for each server directly from the interface
- **Customizable Proxy Settings**: Configure proxy settings for servers requiring internet access (developer should handle this in ProxyManager Class as proxy config can vary depend on your working environment)

## 📝 Notes from the Author 

StackPilot was created to simplify my daily workflow and eliminate repetitive tasks when context switching between multiple applications. I'm releasing it as an open-source tool for the community to use and extend. Currently it support Windows Terminal only

The architecture is intentionally minimal and straightforward, designed to make it easy to add custom addon features. If you'd like to contribute or add new features, please feel free to extend this tool and help make it a valuable utility for the Windows developer community!


## 🏗️ Architecture

StackPilot uses a simple, modular architecture with a clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                         │
│            Embedded Web Interface (FastAPI)             │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │                     │
┌───────▼──────────┐  ┌──────▼────────────┐
│  View Layer      │  │  API Router       │
│  (apirouter.py)  │  │  (/sp/*)          │
└──────────────────┘  └──────┬────────────┘
                             │
                    ┌────────┼─────────┐
                    │                  │
            ┌───────▼──────────┐  ┌────▼──────────┐
            │  Core Services   │  │  Bootstrap    │
            │  - ServerManager │  │  - Config     │
            │  - Addons        │  │  - FileManager│
            │  - Processor     │  │  - etc        │
            └────────┬─────────┘  └───────────────┘
                     │
            ┌────────┴──────────┐
            │                   │
        ┌───▼──────┐      ┌─────▼────┐
        │ Storage  │      │ Addons   │
        │ (JSON)   │      │ - Git    │
        │          │      │ - Env    │
        └──────────┘      └──────────┘
```

### Core Components

#### **Bootstrap Layer** (`src/bootstrap/`)
- **`Application`**: Singleton class that initializes FastAPI and loads configurations
- **`Bootstrap`**: Initializes application components, mounts static files, configures routers
- **`ConfigManager`**: Manages application configuration from `app_config.json`
- **`FileManager`**: Handles file and directory setup

#### **Core Services** (`src/core/`)
- **`ServerManager`**: CRUD operations for server configurations
- **`ServerProcessor`**: Executes commands and manages server processes in Windows Terminal
- **`Addons`**: Plugin system for extended functionality (Git integration, environment inspection)
- **`EnvInspector`**: Inspects environment, detects processes, retrieves Git information

#### **View/API Layer** (`src/view/`)
- **`apirouter.py`**: FastAPI routes for server operations (`@router.get/post/put/delete`)
- **Modal Classes**: Request/response data models for type safety

#### **Interface Layer** (`src/interface/`)
- **Templates**: HTML templates for the web interface
- **Static Files**: JavaScript, CSS, and frontend logic
- **Styles**: CSS stylesheets for UI components

#### **Storage Layer** (`src/storage/`)
- **`Storage`**: Abstracts server configuration persistence using JSON files

## 💻 Installation

### Requirements
- Python 3.8 or higher
- Windows OS (for Windows Terminal integration)
- pip (Python package manager)

### Setup Steps

1. **Clone or download the repository**
   ```bash
   cd path/to/DevDock_V1
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the application** (optional)
   - Edit `src/configs/app_config.json` to customize settings, ports, and addons

## 🚀 Running the Application

### Method 1: Web Interface (Development)
```bash
python src/stackpilotapp.py
```
This starts the FastAPI server on the configured port (default: 8017). Access the interface at `http://localhost:8017/sp/`

## 📋 Configuration

Edit `src/configs/app_config.json` to customize:

```json
{
    "app_info": {
        "app_name": "StackPilot",
        "version": "1.0.0",
        "port": 8017
    },
    "app_settings": {
        "refresh_interval": 30,
        "enable_notifications": true,
        "error_reporting": true,
        "storage": "D_Drive_Temp",
        "terminal": "Windows_Terminal",
        "same_window": true,
        "core_addons": { // here define addon features 
            "git_integration": { "enabled": true },
            "server_detection": { "enabled": false },
            "environment_inspection": { "enabled": false }
        },
        "custom_addons": { // here define ur custom addons for your requirment
            "proxy_settings": {
                "enabled": true,
                "proxy_file_path": "your proxy file path",
                "available_envs": ["dev", "qa", "local", "pre-stage"]
            }
        }
    }
}
```

**Configuration Notes:**
- `refresh_interval`: Server listing refresh interval for user interface (in seconds)
- `enable_notifications`: Enable desktop notifications
- `error_reporting`: Display error information in interface
- `storage`: Path to store server info (`D_Drive_Temp` = D:/tmp/StackPilot, `C_Drive_Temp` = C:/tmp/StackPilot)
- `terminal`: Currently supports Windows Terminal only
- `same_window`: If true, servers launch in multiple tabs of same terminal; if false, each opens in new window
- `proxy_file_path`: Path to your proxy configuration file
- `available_envs`: List of available environments (dev, qa, local, pre-stage, etc.)

## 📡 API Endpoints

### Server Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sp/` | Serve main dashboard HTML |
| GET | `/sp/list/servers` | List all configured servers |
| POST | `/sp/servers/add` | Add a new server configuration |
| POST | `/sp/servers/{id}/start` | Start a server |
| POST | `/sp/servers/{id}/stop` | Stop a server |
| PUT | `/sp/servers/edit` | Update server configuration |
| DELETE | `/sp/servers/{id}` | Delete a server |

### Utilities
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sp/browse-folder` | Open native folder browser dialog |

## 📁 Project Structure

```
DevDock_V1/
├── src/
│   ├── bootstrap/           # Application initialization
│   │   ├── application.py   # Main Application class
│   │   ├── bootstrap.py     # Bootstrap orchestration
│   │   └── managers/        # ConfigManager, FileManager
│   ├── core/                # Core business logic
│   │   ├── server_manager.py
│   │   ├── server_processor.py
│   │   ├── addons.py
│   │   ├── envinspector.py
│   │   └── abstracts/       # Abstract base classes
│   ├── view/                # API layer
│   │   ├── apirouter.py     # Main router
│   │   └── modals/          # Data models
│   ├── custom/              # Custom addons
│   │   └── proxy_manager.py
│   ├── interface/           # Web UI
│   │   ├── templates/       # HTML templates
│   │   ├── static/          # JavaScript files
│   │   └── styles/          # CSS stylesheets
│   ├── configs/             # Configuration files
│   │   └── app_config.json
│   └── storage/             # Data persistence
├── stackpilotapp.py         # FastAPI Uvicorn entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 Development

### Project Dependencies
- **fastapi==0.128.0** - Modern Python web framework
- **uvicorn==0.40.0** - ASGI application server
- **python-multipart==0.0.6** - Multipart form data parsing
- **Windows Terminal** - Command-line application for running servers

### Running in Development Mode

1. Start the development server:
   ```bash
   python src/stackpilotapp.py
   ```

2. Open your browser to `http://localhost:8017/sp/`

3. Use the interface to add and manage servers

### Adding New Features

1. **New Server Addons**: Extend the `Addons` class in `src/core/addons.py`
2. **New API Endpoints**: Add routes to `src/view/apirouter.py`
3. **New UI Components**: Add HTML/CSS to `src/interface/templates/` and `src/interface/styles/`

## 📝 Usage Guide

### Adding a Server

1. Click "Add New Server" button
2. Fill in server details:
   - **Server Name**: Display name for the server
   - **Root Path**: Directory path where the server resides
   - **Runnable Command**: Command to execute (e.g., `npm start`, `python manage.py runserver`)
   - **Port Number**: Port the server runs on
3. Click "Save"

### Starting a Server

1. Select the server from the list
2. Click "Start" button
3. Windows Terminal will open and execute the runnable command
4. Monitor the status in the dashboard

### Stopping a Server

1. Look for the running server
2. Click "Stop" button
3. The process will be terminated

### Environment Variables

Configure environment variables for each server through the interface. These will be available when the server starts.

### Proxy Configuration

This is a custom addon feature. If you want to use it, add the necessary configuration to your JSON file and implement your proxy switching logic in the ProxyManager class.
If proxy settings are enabled in the config, you can select different proxy environments (developer, qa, local) for each server.

## 🐛 Troubleshooting

### Common Issues

**Server won't start**
- Verify the runnable command is correct
- Check that the root path exists and is accessible
- Ensure the port is not already in use
- Check Windows Terminal is installed and accessible

**Configuration not loading**
- Verify `app_config.json` syntax is valid JSON
- Check file paths are absolute and accessible


### Logs
- Check the console output for error messages
- Enable error reporting in `app_config.json` for detailed logging

## 📄 License

Please specify your license here (e.g., MIT, Apache 2.0, GPL, etc.)

## 👤 Author & Contributions

Developed as a Windows developer productivity tool to streamline local development server management.

---

| | |
|---|---|
| **Version** | 1.0.0 |
| **Last Updated** | March 2026 |
