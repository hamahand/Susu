# Landing Page Updates - iOS/Android Coming Soon + PWA Routing

## Changes Made

### 1. Added "Coming Soon" Badges for Native Apps

Added a new download section in the CTA area with:
- **iOS App Store** badge with "Coming Soon" tag
- **Google Play Store** badge with "Coming Soon" tag
- Both badges feature authentic app store icons (Apple logo and Google Play icon)
- Badges are styled with:
  - Semi-transparent background
  - Grayed out appearance (opacity: 0.7, grayscale filter)
  - Cursor: not-allowed to indicate they're not clickable yet
  - Animated "Coming Soon" tags with pulsing effect

### 2. Updated "Get Started" Buttons to Route to PWA

**Hero Section:**
- Changed "Open Web App" → "🚀 Get Started"
- Routes to `/app/` (PWA)

**CTA Section:**
- Changed "🌐 Open Web App" → "🚀 Get Started Now"
- Routes to `/app/` (PWA)
- Added clear messaging: "Access our Progressive Web App (PWA)"

### 3. Improved User Flow

**Clear Hierarchy:**
1. Primary CTA: "Get Started Now" → routes to PWA
2. Secondary option: Download native apps (Coming Soon)
3. Tertiary option: USSD access (*920*55#)

**Messaging:**
- "Access our Progressive Web App (PWA) • Works on any device"
- "Install for offline access and app-like experience"
- "Download Native Apps" section clearly separated
- "No smartphone? Dial *920*55#" for feature phone users

### 4. Styling Details

**Coming Soon Tag:**
```css
- Position: Absolute (top-right corner)
- Background: Accent color (#f59e0b - amber)
- Animation: Pulsing effect (scale 1.0 → 1.05)
- Box shadow with glow effect
```

**Download Badges:**
```css
- Responsive design (stacks on mobile)
- Professional app store styling
- Icons: Apple and Google Play SVG logos
- Proper typography hierarchy
```

**Mobile Responsive:**
- Badges stack vertically on mobile (< 968px)
- Full width with max-width constraint
- Proper spacing and padding adjustments

## User Journey

### Current State:
1. User lands on page
2. Sees "Get Started" button prominently
3. Clicks → Goes to PWA at `/app/`
4. Can install PWA for app-like experience
5. Scrolls down to see native apps are "Coming Soon"
6. Alternative: Can use USSD on any phone

### Future State (when native apps are ready):
- Simply remove `coming-soon` class from badges
- Add href links to App Store and Google Play
- Change cursor from `not-allowed` to `pointer`
- Remove "Coming Soon" tags

## Files Modified

1. **`/web/index.html`**
   - Updated hero section CTA button
   - Added download section with iOS/Android badges
   - Updated CTA section with clearer messaging

2. **`/web/styles.css`**
   - Added `.download-section` styles
   - Added `.download-badges` styles
   - Added `.coming-soon-tag` with animation
   - Added mobile responsive styles

## Testing Checklist

- [x] "Get Started" buttons route to `/app/`
- [x] iOS badge shows "Coming Soon" tag
- [x] Android badge shows "Coming Soon" tag
- [x] Badges are not clickable (cursor: not-allowed)
- [x] Pulsing animation works on "Coming Soon" tags
- [x] Responsive design works on mobile
- [x] USSD option is still visible and clear
- [x] PWA messaging is clear and prominent

## Next Steps

When native apps are ready:
1. Build and publish iOS app to App Store
2. Build and publish Android app to Google Play
3. Update `/web/index.html`:
   ```html
   <a href="https://apps.apple.com/app/..." class="download-badge">
   <!-- Remove coming-soon class -->
   <!-- Remove coming-soon-tag span -->
   ```
4. Update CSS to remove grayscale filter
5. Test app store links

## Visual Hierarchy

```
┌─────────────────────────────────┐
│  🚀 Get Started Now (Primary)   │  ← Routes to PWA
├─────────────────────────────────┤
│  Access PWA • Works everywhere  │
├─────────────────────────────────┤
│                                 │
│  Download Native Apps           │
│  ┌──────────┐  ┌──────────┐   │
│  │ App Store│  │Google Play│   │
│  │ 🏷️Coming │  │🏷️Coming   │   │
│  │   Soon   │  │   Soon    │   │
│  └──────────┘  └──────────┘   │
├─────────────────────────────────┤
│  Dial *920*55# (USSD)           │
└─────────────────────────────────┘
```

## Impact

✅ **Better UX**: Clear primary action (Get Started → PWA)
✅ **Expectations Set**: Users know native apps are coming
✅ **Immediate Access**: Users can use PWA right away
✅ **Inclusive**: USSD option for feature phones
✅ **Future-Ready**: Easy to activate when apps are published

