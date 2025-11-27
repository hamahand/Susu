# SusuSave PWA - Quick Start Guide

## Getting Started in 5 Minutes

### 1. Install Dependencies
```bash
cd web/app
npm install
```

### 2. Configure Environment
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and set your API URL
# For local development:
VITE_API_URL=http://localhost:8000

# For production:
VITE_API_URL=https://api.sususave.com
```

### 3. Start Development Server
```bash
npm run dev
```

The app will be available at: `http://localhost:3000/app/`

### 4. Access the App

Open your browser and navigate to:
- **Landing Page**: `http://localhost:3000/`
- **PWA App**: `http://localhost:3000/app/`

## First Time Use

1. **Register an Account**
   - Go to `/app/register`
   - Enter your name, phone number (+233...), and password
   - You'll be auto-logged in after registration

2. **Create Your First Group**
   - Click "Create Group" on the dashboard
   - Enter group name, contribution amount, and number of members
   - Share the generated group code with others

3. **Or Join an Existing Group**
   - Click "Join Group"
   - Enter the group code shared by the admin
   - You'll be added to the group rotation

## Key Features to Try

### For All Users
- ✅ View all your groups on the dashboard
- ✅ See detailed group statistics
- ✅ Track payment status for each round
- ✅ View next recipient and payout amount
- ✅ Update your profile information
- ✅ Check member rotation order

### For Group Admins
- ✅ Approve payouts when all members have paid
- ✅ Invite new members via SMS
- ✅ View pending invitations
- ✅ Copy group code to share

## Testing PWA Features

### 1. Test Offline Mode
```bash
# Build for production first
npm run build
npm run preview

# Then:
1. Open the app in Chrome
2. Open DevTools (F12)
3. Go to Application > Service Workers
4. Check "Offline"
5. Refresh the page - it should still work!
```

### 2. Test Installation
```bash
# After running preview:
1. Open in Chrome
2. Look for install icon in address bar
3. Or wait 10 seconds for custom prompt
4. Click "Install"
5. App opens as standalone
```

### 3. Test Shortcuts
```bash
# After installing:
1. Right-click the app icon
2. See shortcuts for:
   - My Groups
   - Create Group
   - Join Group
```

## Production Build

```bash
# Build optimized production bundle
npm run build

# Output will be in dist/ directory
# Total size: ~500KB (gzipped)

# Preview production build
npm run preview
```

## Deployment

### Quick Deploy to Netlify/Vercel

1. **Build the app**
   ```bash
   npm run build
   ```

2. **Deploy dist/ folder**
   - Drag and drop `dist/` to Netlify
   - Or connect your Git repo

3. **Configure**
   - Set base path: `/app/`
   - Add redirect rule: `/app/* → /app/index.html`
   - Set environment variable: `VITE_API_URL`

### Deploy with Landing Page

If deploying both landing page and PWA:

```nginx
# Nginx example
server {
    # Landing page at root
    location / {
        root /var/www/landing;
        try_files $uri $uri/ /index.html;
    }
    
    # PWA at /app/
    location /app {
        alias /var/www/pwa/dist;
        try_files $uri $uri/ /app/index.html;
    }
}
```

## Common Issues

### Issue: "Network Error"
**Solution**: Make sure backend API is running and VITE_API_URL is correct

### Issue: Service Worker not registering
**Solution**: Service workers only work on HTTPS or localhost. Deploy to test.

### Issue: Install prompt not showing
**Solution**: 
- Clear browser data
- Uninstall if already installed
- Wait 10 seconds after page load
- Works best in Chrome

### Issue: API calls failing
**Solution**: 
- Check CORS settings on backend
- Verify API URL in .env
- Check browser console for errors

## Development Tips

### Hot Module Replacement
Vite provides instant HMR - changes reflect immediately without refresh

### TypeScript
All files are type-checked. Run `npm run type-check` to verify.

### Debugging
- Use React DevTools browser extension
- Check Network tab for API calls
- Use Application tab for PWA features

### Component Development
All components are in `/src/components/` with their own CSS files

### Adding New Pages
1. Create in `/src/pages/`
2. Add route in `App.tsx`
3. Import as lazy component for code splitting

## Environment Variables

Available variables:
- `VITE_API_URL` - Backend API URL (required)

Access in code:
```typescript
import { config } from './config';
console.log(config.API_BASE_URL);
```

## Scripts Reference

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run type-check` - Check TypeScript types

## Support & Documentation

- **Full Documentation**: See `README.md`
- **Implementation Details**: See `PWA_COMPLETE.md`
- **API Documentation**: See `/backend/docs/API.md`

## Next Steps

1. ✅ Customize branding in `manifest.json`
2. ✅ Add your logo to `/public/assets/`
3. ✅ Configure backend API URL
4. ✅ Test all features locally
5. ✅ Build and deploy to production
6. ✅ Test PWA installation on mobile
7. ✅ Share feedback and report bugs

---

**Happy Coding!** 🚀

For questions or issues, check the full README.md or open an issue on GitHub.

