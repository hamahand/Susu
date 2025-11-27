# SusuSave Mobile App - Branding Assets

## App Icon Template

The `app-icon-template.svg` is a 1024x1024px template for generating app icons.

### Generating App Icons

You can use this SVG to generate all required icon sizes for iOS and Android:

#### Using Expo
```bash
# Install expo-optimize if not already installed
npm install -g sharp-cli

# Convert SVG to PNG and generate icons
npx expo-optimize
```

#### Manual Generation
Use online tools or Figma/Sketch to export these sizes:

**iOS (all required sizes):**
- 20x20 @2x, @3x (40px, 60px)
- 29x29 @2x, @3x (58px, 87px)
- 40x40 @2x, @3x (80px, 120px)
- 60x60 @2x, @3x (120px, 180px)
- 76x76 @1x, @2x (76px, 152px)
- 83.5x83.5 @2x (167px)
- 1024x1024 (App Store)

**Android (all required sizes):**
- 36x36 (ldpi)
- 48x48 (mdpi)
- 72x72 (hdpi)
- 96x96 (xhdpi)
- 144x144 (xxhdpi)
- 192x192 (xxxhdpi)
- 512x512 (Play Store)

### Using ImageMagick (Command Line)

If you have ImageMagick installed:

```bash
# Install ImageMagick first
brew install imagemagick  # macOS
# or
sudo apt-get install imagemagick  # Linux

# Convert SVG to PNG at different sizes
convert app-icon-template.svg -resize 1024x1024 icon-1024.png
convert app-icon-template.svg -resize 512x512 icon-512.png
convert app-icon-template.svg -resize 192x192 icon-192.png
# ... repeat for all sizes
```

### Using Online Tools

1. **Appicon.co** - Upload the SVG and download iOS/Android icon sets
2. **Icon Kitchen** - Generates adaptive icons for Android
3. **MakeAppIcon** - Generates all sizes from one image

## Splash Screen

The `splash-logo.svg` is designed for the app splash screen.

### app.json Configuration

Update your `app.json`:

```json
{
  "expo": {
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash-icon.png",
      "resizeMode": "contain",
      "backgroundColor": "#2E7D32"
    },
    "adaptiveIcon": {
      "foregroundImage": "./assets/adaptive-icon.png",
      "backgroundColor": "#2E7D32"
    }
  }
}
```

## Brand Colors

```javascript
const colors = {
  primary: '#2E7D32',      // Material Green 800
  primaryDark: '#1B5E20',  // Material Green 900
  primaryDarker: '#047857', // Emerald 700
  primaryLight: '#4CAF50', // Material Green 500
  white: '#FFFFFF',
  background: '#F9FAFB',
  text: '#1F2937'
};
```

## Logo Usage in App

### In React Native Components

```tsx
// Using the logo SVG in your app
import Logo from './assets/logo.svg';

// In your component
<Logo width={200} height={60} />
```

### Installation for SVG Support

If SVGs don't work, install:

```bash
npm install react-native-svg
npx expo install react-native-svg
```

## Design Philosophy

- **Green Gradient**: Represents growth, savings, and prosperity
- **Three Circles**: Symbolize community and collective savings (ROSCA concept)
- **Cedi Symbol (₵)**: Ghanaian currency, showing local relevance
- **Clean & Modern**: Professional yet approachable design

## Questions?

For custom sizes or formats, use the SVG files as they scale perfectly to any dimension.

