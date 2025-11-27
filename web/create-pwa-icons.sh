#!/bin/bash

# Create PWA icons from SVG source
# This script creates various icon sizes needed for PWA

echo "Creating PWA icons for SusuSave..."

# Create directory for generated icons
mkdir -p assets/pwa-icons

# Icon sizes needed for PWA
sizes=(16 32 48 64 96 128 144 152 192 256 384 512)

# Create PNG versions of the favicon for different sizes
for size in "${sizes[@]}"; do
    echo "Creating ${size}x${size} icon..."
    
    # Create a simple PNG favicon using ImageMagick (if available)
    if command -v convert &> /dev/null; then
        convert -size ${size}x${size} xc:"#2E7D32" \
                -fill white -pointsize $((size/4)) -gravity center \
                -annotate +0+0 "S" \
                assets/pwa-icons/icon-${size}x${size}.png
    else
        # Fallback: create a simple colored square
        echo "ImageMagick not available, creating placeholder..."
        # We'll create SVG versions instead
        cat > assets/pwa-icons/icon-${size}x${size}.svg << EOF
<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="${size}" height="${size}" rx="$((size/8))" fill="#2E7D32"/>
  <text x="50%" y="50%" text-anchor="middle" dy="0.35em" fill="white" font-family="Arial, sans-serif" font-size="$((size/3))" font-weight="bold">S</text>
</svg>
EOF
    fi
done

echo "PWA icons created successfully!"
echo "Icons are available in assets/pwa-icons/"
