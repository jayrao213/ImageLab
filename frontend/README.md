# ImageLab Frontend

Modern Next.js frontend for the ImageLab image management system with AI-powered search.

## Features

- 🏠 **Dashboard** - System health check and overview
- 👥 **User Management** - View all users in the system
- 🖼️ **Image Gallery** - Browse and view all uploaded images
- 📤 **Upload** - Upload images with automatic AI labeling
- 🔍 **Smart Search** - Search images by AI-detected labels
- 🎨 **Modern UI** - Built with Tailwind CSS and dark mode support

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client for API calls

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout with navigation
│   ├── page.tsx            # Home/Dashboard page
│   ├── globals.css         # Global styles
│   ├── users/
│   │   └── page.tsx        # Users list page
│   ├── images/
│   │   └── page.tsx        # Image gallery page
│   ├── upload/
│   │   └── page.tsx        # Image upload page
│   └── search/
│       └── page.tsx        # Label search page
├── components/
│   └── Navigation.tsx      # Navigation bar component
├── lib/
│   └── api.ts              # API client and types
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## Getting Started

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure API URL

The frontend is pre-configured to connect to `http://localhost:8000` (the FastAPI backend).

To change this, edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### 4. Build for Production

```bash
npm run build
npm start
```

## Pages Overview

### Home (`/`)
- System health check (S3 bucket and database status)
- Quick statistics (users, images)
- Quick action buttons

### Users (`/users`)
- List all users in the system
- Display user details (name, username, ID)

### Images (`/images`)
- Gallery view of all uploaded images
- Filter by user
- View image details and AI labels
- Delete all images function

### Upload (`/upload`)
- Select user
- Choose image file
- Preview before upload
- Automatic AI labeling on upload

### Search (`/search`)
- Search images by label
- Partial match support
- View matching labels with confidence scores
- Popular search suggestions

## API Integration

All API calls are handled through `lib/api.ts`, which provides:

- Type-safe functions for all backend endpoints
- Centralized error handling
- TypeScript interfaces matching backend models

## Styling

The app uses Tailwind CSS with:
- Responsive design (mobile-first)
- Dark mode support
- Custom color palette (primary blue theme)
- Utility classes for rapid development

## Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API URL (default: `http://localhost:8000`)

## Development Tips

### Hot Reload
Changes to any file will automatically reload the browser.

### Type Safety
TypeScript ensures type safety between frontend and backend. All API response types are defined in `lib/api.ts`.

### Adding New Pages
1. Create a new folder in `app/`
2. Add `page.tsx` inside it
3. The route will be automatically available

### Styling Components
Use Tailwind utility classes directly in JSX. Dark mode variants use the `dark:` prefix.

## Common Tasks

### Change API Endpoint
Edit `.env.local` and restart the dev server.

### Add New API Function
1. Add TypeScript interface in `lib/api.ts`
2. Create function using axios
3. Export and use in pages

### Customize Theme
Edit `tailwind.config.js` to change colors, fonts, etc.

## Troubleshooting

### Cannot Connect to Backend
- Ensure the FastAPI backend is running on port 8000
- Check the `NEXT_PUBLIC_API_URL` in `.env.local`
- Look for CORS errors in the browser console

### Build Errors
- Run `npm install` to ensure all dependencies are installed
- Delete `.next` folder and rebuild
- Check for TypeScript errors with `npm run lint`

### Images Not Loading
- Verify the backend API is accessible
- Check browser console for network errors
- Ensure S3 credentials are configured in the backend

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Performance

- Images are lazy-loaded
- API calls use efficient caching
- Dark mode respects system preferences
- Responsive images for different screen sizes

## Next Steps

- Add user authentication
- Implement image editing features
- Add image tagging and categories
- Create image sharing functionality
- Add batch upload support
