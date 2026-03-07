
import uvicorn
from bootstrap import Application
from configs import Config

# Initialize and run the application instance
##################################################
application = Application()
stackpilot = application.app
app_context = Config().context 
info = app_context.get("app_info")
port = info.get("port", 8017) if info else 8017
#################################################
if __name__ == "__main__":
    uvicorn.run("stackpilotapp:stackpilot", host="0.0.0.0", port=port, reload=False, log_config=None)





