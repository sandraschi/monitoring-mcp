# Per-repo fleet start config for monitoring-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'monitoring-mcp'
    BackendPort  = 10851
    FrontendPort = 10850
    HealthPath   = '/health'
    WebRoot      = 'web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'monitoring_mcp.server:app'
        SyncExtras    = @('dev')
        SyncOnStart  = $true
        Env           = @{ WEB_PORT = '10851' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
