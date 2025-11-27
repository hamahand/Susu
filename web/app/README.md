# SusuSave PWA

A Progressive Web App for SusuSave - Ghana's modern ROSCA (Rotating Savings and Credit Association) platform.

## Features

- 📱 **Full Mobile App Parity** - All features from the React Native app
- 🔒 **Secure Authentication** - Login with password or OTP
- 👥 **Group Management** - Create, join, and manage savings groups
- 💰 **Smart Payments** - Track contributions and payouts
- 📊 **Real-time Dashboard** - Live group statistics and member status
- 📨 **Invitations** - Invite members via SMS
- 🌐 **Offline Support** - Service worker caching for offline access
- 📲 **Installable** - Add to home screen as a native-like app
- 📱 **Responsive** - Works on all devices and screen sizes

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Axios** - API client
- **Vite PWA Plugin** - PWA capabilities
- **CSS Modules** - Scoped styling

## Getting Started

### Prerequisites

- Node.js 16+ and npm/yarn
- Backend API running (see `/backend` directory)

### Installation

```bash
# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Update API URL in .env
VITE_API_URL=http://localhost:8000
```

### Development

```bash
# Start dev server
npm run dev

# App will be available at http://localhost:3000/app/
```

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
/app/
├── public/              # Static assets
│   ├── manifest.json   # PWA manifest
│   └── sw.js          # Service worker
├── src/
│   ├── api/           # API service layer
│   ├── components/    # Reusable components
│   ├── contexts/      # React contexts (Auth, etc.)
│   ├── hooks/         # Custom React hooks
│   ├── pages/         # Page components
│   ├── styles/        # Global styles
│   ├── types/         # TypeScript types
│   ├── utils/         # Utility functions
│   ├── App.tsx        # Main app component
│   └── main.tsx       # Entry point
├── index.html         # HTML template
├── vite.config.ts     # Vite configuration
└── package.json       # Dependencies
```

## Available Routes

### Public Routes
- `/app/login` - Login page
- `/app/register` - Registration page
- `/app/otp-verify` - OTP verification

### Protected Routes (Require Authentication)
- `/app/dashboard` - My groups dashboard
- `/app/groups/create` - Create new group
- `/app/groups/join` - Join existing group
- `/app/groups/:id` - Group details & dashboard
- `/app/profile` - User profile settings

## PWA Features

### Service Worker
- Caches static assets for offline access
- Network-first strategy for API requests
- Background sync for failed requests (future)
- Push notifications support (future)

### Install Prompt
- Automatic install prompt after 10 seconds
- Dismissal persists for 7 days
- Shows only if not already installed

### Offline Support
- Offline indicator when network is unavailable
- Cached pages work without internet
- API requests queued for retry when online

## Environment Variables

```bash
VITE_API_URL=http://localhost:8000  # Backend API URL
```

## Deployment

### Build Output
The `npm run build` command creates an optimized production build in the `dist/` directory.

### Deployment Options

1. **Static Hosting** (Netlify, Vercel, etc.)
   - Deploy the `dist/` folder
   - Configure base path as `/app/`
   - Set up redirects for SPA routing

2. **Server Deployment**
   - Serve `dist/` directory as static files
   - Configure server to serve `index.html` for all `/app/*` routes
   - Ensure `/` serves the landing page

### Example Nginx Configuration

```nginx
location /app {
    alias /path/to/dist;
    try_files $uri $uri/ /app/index.html;
}

location / {
    root /path/to/landing;
    try_files $uri $uri/ /index.html;
}
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

See LICENSE file in the repository root.

## Support

For issues and questions, please open an issue on GitHub or contact support@sususave.com.

