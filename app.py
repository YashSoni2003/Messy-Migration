from app import create_app
from config import get_config

if __name__ == '__main__':
    config = get_config()
    app = create_app()
    app.config.from_object(config)
    
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=config.DEBUG
    )