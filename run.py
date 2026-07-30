#!/usr/bin/env python
from app import create_app

# Create app instance
app = create_app()

if __name__ == '__main__':
    # Render uses PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)