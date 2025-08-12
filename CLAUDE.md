# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

JoyAgent-JDGenie is an end-to-end multi-agent system built with a microservices architecture. It provides intelligent agent capabilities for complex task decomposition, execution, and reporting through multiple specialized agents.

### Core Architecture

The system consists of 4 main components:
- **genie-backend**: Spring Boot backend service (Java 17) providing multi-agent orchestration
- **genie-tool**: Python FastAPI service providing specialized tools (code interpreter, search, reporting)
- **genie-client**: MCP (Model Context Protocol) client service for external tool integration
- **ui**: React/TypeScript frontend with Vite build system

### Agent System Design

The backend implements multiple agent patterns:
- **PlanningAgent**: Task decomposition using plan-and-execute pattern
- **ReactAgent**: Real-time reactive agent following observe-think-act cycle
- **ExecutorAgent**: Task execution agent for running specific sub-tasks
- **SummaryAgent**: Result aggregation and final answer synthesis

## Common Development Commands

### Backend (genie-backend)
```bash
cd genie-backend
sh build.sh        # Build with Maven
sh start.sh        # Start Spring Boot service (port 8080)
mvn test           # Run tests
```

### Frontend (ui)
```bash
cd ui
pnpm install       # Install dependencies
pnpm dev           # Development server (port 3000)
pnpm build         # Production build
pnpm lint          # ESLint
pnpm fix           # Auto-fix ESLint issues
```

### Python Tools (genie-tool)
```bash
cd genie-tool
uv sync                              # Install dependencies and create virtual environment
source .venv/bin/activate           # Activate virtual environment

# Database setup (first run only)
# For SQLite (default):
uv run python -m genie_tool.db.db_engine

# For H2 (local debugging - recommended for development):
uv run python -m genie_tool.db.migrations.create_h2_database

# For MySQL (enterprise setup):
uv run python -m genie_tool.db.migrations.create_mysql_database

uv run python server.py            # Start tool server (port 1601)
```

### MCP Client (genie-client)
```bash
cd genie-client
uv venv
source .venv/bin/activate
sh start.sh                        # Start MCP client (port 8188)
```

### Full System Deployment
```bash
sh check_dep_port.sh              # Check dependencies and port conflicts
sh Genie_start.sh                 # Start all services (Control+C to stop all)
```

## Configuration

### LLM Configuration
Edit `genie-backend/src/main/resources/application.yml`:
- Configure `llm.default` for primary model settings
- Add model configurations in `llm.settings` JSON for different agents
- Set `code_interpreter_url`, `deep_search_url`, `mcp_client_url` for service endpoints

### Tool Configuration
Edit `genie-tool/.env` (copy from `.env_template`):
- `OPENAI_API_KEY`, `OPENAI_BASE_URL`: LLM API settings
- `SERPER_SEARCH_API_KEY`: Web search capability (get from serper.dev)
- `DEFAULT_MODEL`: Model identifier

### Database Configuration
Configure database type in `genie-tool/.env`:
- `DATABASE_TYPE`: Set to "sqlite" (default), "h2", or "mysql"

For SQLite (default):
- `SQLITE_DB_PATH`: Database file path (default: autobots.db)

For H2 (local debugging - recommended for development):
- `H2_DB_PATH`: Database file path (default: ./genie_h2_db.db)
- `H2_MODE`: Set to "file" (persistent) or "memory" (temporary)

For MySQL (enterprise):
- `MYSQL_HOST`: MySQL server host (default: localhost)
- `MYSQL_PORT`: MySQL server port (default: 3306)
- `MYSQL_USER`: MySQL username (default: root)
- `MYSQL_PASSWORD`: MySQL password
- `MYSQL_DATABASE`: Database name (default: genie_db)

### MCP Integration
Configure MCP servers in `application.yml`:
```yaml
mcp_server_url: "http://ip1:port1/sse,http://ip2:port2/sse"
```

## Architecture Patterns

### Multi-Agent Coordination
- Uses DAG-based execution engine for parallel task processing
- Implements cross-task memory management for workflow continuity
- Supports both reactive and planning agent patterns dynamically

### Tool System
- Pluggable tool architecture via `BaseTool` interface
- Built-in tools: CodeInterpreter, DeepSearch, FileOperations, ReportGenerator
- MCP protocol integration for external tool ecosystem

### Key Design Principles
- **Tool Evolution**: Automatic tool composition from atomic components
- **Multi-level Thinking**: Work-level and task-level planning hierarchy
- **Streaming Responses**: Full pipeline supports real-time output via SSE

### Enterprise Features
- **Database Support**: SQLite for basic use, H2 for development/debugging, MySQL for production
- **Session Management**: Persistent conversation sessions with history
- **User Management**: Multi-user support with role-based access control
- **Report Management**: Generated reports storage and retrieval
- **Task Tracking**: Detailed execution logs and performance metrics

## Adding Custom Components

### Custom Agent Tool
Implement `BaseTool` interface in `genie-backend/src/main/java/com/jd/genie/agent/tool/common/`:
```java
public class CustomTool implements BaseTool {
    public String getName() { return "custom_tool"; }
    public String getDescription() { return "Tool description"; }
    public Map<String, Object> toParams() { return paramSchema; }
    public Object execute(Object input) { return result; }
}
```

Register in `GenieController.buildToolCollection()`:
```java
CustomTool customTool = new CustomTool();
toolCollection.addTool(customTool);
```

### Custom MCP Server
Configure MCP server URLs in `application.yml` and implement MCP protocol endpoints.

## Important File Locations

### Configuration Files
- `genie-backend/src/main/resources/application.yml`: Main backend configuration
- `genie-tool/.env`: Python tool service configuration
- `ui/.env`: Frontend API endpoints

### Core Implementation
- `genie-backend/src/main/java/com/jd/genie/controller/GenieController.java`: Main API controller
- `genie-backend/src/main/java/com/jd/genie/agent/agent/`: Agent implementations
- `genie-tool/genie_tool/tool/`: Python tool implementations
- `genie-tool/genie_tool/db/models/`: Database models (User, Session, Conversation, Report, TaskExecution)
- `genie-tool/genie_tool/db/repositories/`: Data access layer
- `genie-tool/genie_tool/services/`: Business logic layer

### Build Scripts
- `genie-backend/build.sh`, `genie-backend/start.sh`: Backend deployment
- `ui/start.sh`: Frontend development server
- `Genie_start.sh`: Full system startup script

### Database Scripts
- `genie-tool/genie_tool/db/db_engine.py`: Database initialization
- `genie-tool/genie_tool/db/migrations/create_h2_database.py`: H2 setup script (for development)
- `genie-tool/genie_tool/db/migrations/create_mysql_database.py`: MySQL setup script (for production)
- `genie-tool/genie_tool/db/migrations/migrate_sqlite_to_mysql.py`: Data migration script