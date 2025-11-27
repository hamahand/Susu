# Quick Setup Guide for SusuSave Landing Page

## 🚀 View Your Landing Page

### Option 1: Open Directly in Browser

```bash
cd /Users/maham/susu/web
open index.html
```

### Option 2: Run a Local Server (Recommended)

```bash
cd /Users/maham/susu/web

# Python 3 (Already installed on your Mac)
python3 -m http.server 8080

# Then open: http://localhost:8080
```

### Option 3: Use VS Code Live Server

If you use VS Code:
1. Install "Live Server" extension
2. Right-click `index.html`
3. Select "Open with Live Server"

## 📸 Adding Images (Optional)

The landing page works without images, but you can add:

### 1. App Screenshot

Create or add a screenshot of your mobile app:
- File: `web/assets/app-screenshot.png`
- Size: 1170 x 2532px (iPhone size)

### 2. App Store Badges

Download official badges:
- **Apple**: https://developer.apple.com/app-store/marketing/guidelines/
- **Google**: https://play.google.com/intl/en_us/badges/

Save as:
- `web/assets/app-store.svg`
- `web/assets/google-play.svg`

### 3. Logo/Favicon

Replace the ₵ symbol with your logo:
- `web/assets/logo.svg` (for header)
- `web/assets/favicon.png` (for browser tab)

## 🎨 Customization

### Change Colors

Edit `web/styles.css` at the top:

```css
:root {
    --primary: #2E7D32;      /* Your brand color */
    --secondary: #10b981;    /* Accent color */
    /* ... */
}
```

### Update Content

Edit `web/index.html` directly. Search for:
- Statistics (1000+ users, etc.)
- Feature descriptions
- FAQ answers
- Contact information

### Update Links

Replace all `#` links with real URLs:
- App store download links
- Social media profiles
- Contact/support pages

## 🌐 Deploy to Production

### Netlify (Easiest)

1. Go to [netlify.com](https://netlify.com)
2. Sign up (free)
3. Drag and drop the `web` folder
4. Done! You get a URL like `yoursite.netlify.app`

### Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd /Users/maham/susu/web
vercel
```

### GitHub Pages

1. Push to GitHub:
```bash
git add web/
git commit -m "Add landing page"
git push
```

2. Enable GitHub Pages:
   - Go to repository Settings
   - Click "Pages"
   - Select your branch
   - Choose `/web` folder
   - Save

Your site will be at: `https://yourusername.github.io/susu/`

## 🔗 Connect to Backend

When you deploy the landing page, update links:

### Update API URL in Download Buttons

Edit `index.html`:

```html
<!-- Replace placeholder app store links -->
<a href="YOUR_APP_STORE_URL" class="download-badge">
<a href="YOUR_PLAY_STORE_URL" class="download-badge">
```

### Add Contact Form (Optional)

You can integrate with:
- **Formspree**: https://formspree.io (easiest)
- **EmailJS**: https://www.emailjs.com
- Your backend API

## 📱 Test Responsiveness

Open in browser and test:

```bash
# Desktop
Open normally

# Mobile simulation
1. Open Chrome DevTools (F12)
2. Click device toggle (Ctrl+Shift+M)
3. Select iPhone/Android
```

## ✅ Pre-Launch Checklist

- [ ] Test on Chrome, Firefox, Safari
- [ ] Test on mobile (iPhone & Android)
- [ ] All links work (no `#` placeholders)
- [ ] Images load properly
- [ ] Forms submit correctly
- [ ] Page loads fast (< 3 seconds)
- [ ] SEO meta tags filled
- [ ] Analytics tracking added
- [ ] Privacy policy link works
- [ ] Contact information is correct

## 🎯 Next Steps

1. **View the landing page** using one of the methods above
2. **Customize colors and content** to match your brand
3. **Add images** to make it more visual
4. **Deploy** to Netlify or Vercel
5. **Share** with users!

## 🆘 Troubleshooting

### Images not loading

Check file paths are correct:
```html
<img src="assets/your-image.png" alt="Description">
```

### Styles not applying

1. Clear browser cache (Ctrl+Shift+R)
2. Check console for errors (F12)
3. Verify `styles.css` is in same folder

### Mobile menu not working

1. Check JavaScript console for errors
2. Ensure `script.js` is loaded
3. Verify file path: `<script src="script.js"></script>`

## 📞 Support

Questions? Contact:
- Email: support@sususave.com
- GitHub: File an issue

---

**You're ready to go! 🎉**

Open the landing page now:
```bash
cd /Users/maham/susu/web && python3 -m http.server 8080
```

Then visit: **http://localhost:8080**

