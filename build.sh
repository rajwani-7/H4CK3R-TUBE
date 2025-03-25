#!/bin/bash

echo "=== Building for Vercel deployment ==="

# Ensure all directories exist
mkdir -p .vercel/output/static
mkdir -p .vercel/output/functions/api

# Copy static files
echo "Copying static files..."
cp -r static .vercel/output/static/
cp -r templates .vercel/output/static/

# Copy Python files
echo "Copying Python files..."
cp vercel_app.py .vercel/output/functions/
cp -r api .vercel/output/functions/

# Generate simple index.html for the root
echo "Creating simple index redirect..."
cat > .vercel/output/static/index.html << EOF
<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="refresh" content="0;url=/api">
  <title>YouTube Downloader</title>
</head>
<body>
  <p>Redirecting to the application...</p>
</body>
</html>
EOF

echo "Build complete! Ready for Vercel deployment." 