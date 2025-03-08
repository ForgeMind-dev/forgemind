# forgemind

**READ THE FUCKING MANUAL**

This is the monorepo of ForgeMind. The reliability of this product is dependent on all parts of the stack being in sync with each other all of the time.

1. Do **not** try to run these applications without using the provided instructions. We want to make sure that our code does not just work on your computer.
2. Keep dependencies (requirements.txt, package.json, etc.) synchronized. 
3. We do not have a testing process, so we have to keep a healthy environment.
4. Make sure that you are modifying git history at the root level directory, not just within each subfolder (forgemind-electron, forgemind-backend, etc).
5. As you begin to touch the CAD integrations, be extra careful to **READ THE FUCKING MANUAL**

## Heroku Setup Instructions

### Configuring Supabase Authentication

For proper authentication, you need to set up the following environment variables in Heroku:

1. **Regular client credentials** (for normal operations):
```
heroku config:set SUPABASE_URL=your_supabase_url --app forgemind-backend
heroku config:set SUPABASE_ANON_KEY=your_supabase_anon_key --app forgemind-backend
```

2. **Admin client credentials** (for admin operations, such as user management):
```
heroku config:set SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key --app forgemind-backend
```

The service role key can be found in your Supabase project settings under "API" > "Project API Keys".

**Important**: The service role key has admin privileges and should never be exposed to the client-side code.

### Authentication Flow

The application uses different authentication approaches depending on the context:

- **Frontend (webapp)**: Uses standard Supabase client-side auth with `supabase.auth.getUser()`
- **Backend (Python)**: Uses a combination of methods based on available credentials:
  - Direct token validation with `supabase.auth.get_user(token)`
  - Admin user operations with `supabase_admin.auth.admin.list_users()` (requires service role key)
  - Database queries to verify user existence
```
forgemind
├─ README.md
├─ forgemind-backend
│  ├─ .env
│  ├─ Procfile
│  ├─ README.md
│  ├─ app.py
│  ├─ requirements.txt
│  ├─ run_local_mac.sh
│  ├─ run_local_windows.cmd
│  ├─ runtime.txt
├─ forgemind-electron
│  ├─ .env
│  ├─ .env.production
│  ├─ README.md
│  ├─ icons
│  │  ├─ icon.icns
│  │  ├─ icon.ico
│  │  └─ icons.png
│  ├─ package-lock.json
│  ├─ package.json
│  ├─ public
│  │  ├─ electron.js
│  │  └─ index.html
│  ├─ src
│  │  ├─ global.d.ts
│  │  ├─ index.tsx
│  │  └─ main
│  │     └─ main.ts
│  └─ tsconfig.json
└─ forgemind-webapp
   ├─ .env
   ├─ Procfile
   ├─ README.md
   ├─ package-lock.json
   ├─ package.json
   ├─ public
   │  ├─ favicon.ico
   │  ├─ index.html
   │  └─ manifest.json
   ├─ src
   │  ├─ App.css
   │  ├─ App.tsx
   │  ├─ app
   │  │  ├─ App.tsx
   │  │  ├─ api.ts
   │  │  ├─ assets
   │  │  │  ├─ full_logo.png
   │  │  │  ├─ logo_icon.png
   │  │  │  ├─ logo_icon1.png
   │  │  │  └─ trash_bin.png
   │  │  ├─ components
   │  │  │  ├─ BottomBar.tsx
   │  │  │  ├─ ChatWindow.tsx
   │  │  │  ├─ ConnectCADModal.tsx
   │  │  │  ├─ Header.tsx
   │  │  │  ├─ OptimizeModal.tsx
   │  │  │  ├─ RefineModal.tsx
   │  │  │  ├─ RelationsModal.tsx
   │  │  │  └─ Sidebar.tsx
   │  │  ├─ styles
   │  │  │  ├─ BottomBar.css
   │  │  │  ├─ ChatWindow.css
   │  │  │  ├─ Header.css
   │  │  │  ├─ Sidebar.css
   │  │  │  ├─ buttons.css
   │  │  │  ├─ layout.css
   │  │  │  ├─ modal.css
   │  │  │  └─ reset.css
   │  │  └─ types.ts
   │  ├─ assets
   │  │  ├─ images
   │  │  │  ├─ logo.png
   │  │  │  ├─ logo1.png
   │  │  │  ├─ logo_black_cropped2.png
   │  │  │  ├─ logo_black_cropped3.png
   │  │  │  ├─ logo_black_cropped4.png
   │  │  │  ├─ logo_black_cropped5.1.png
   │  │  │  └─ logo_black_cropped6.png
   │  │  └─ styles
   │  │     └─ global.css
   │  ├─ components
   │  │  ├─ archive
   │  │  │  ├─ CallToAction.css
   │  │  │  ├─ CallToAction.tsx
   │  │  │  ├─ FeatureCard.css
   │  │  │  ├─ FeatureCard.tsx
   │  │  │  ├─ FeaturesSection.css
   │  │  │  ├─ FeaturesSection.tsx
   │  │  │  ├─ HowItWorks.css
   │  │  │  ├─ HowItWorks.tsx
   │  │  │  ├─ OverviewSection.css
   │  │  │  ├─ OverviewSection.tsx
   │  │  │  ├─ TeamSection.css
   │  │  │  ├─ TeamSection.tsx
   │  │  │  ├─ TechShowcase.css
   │  │  │  └─ TechShowcase.tsx
   │  │  ├─ layout
   │  │  │  ├─ Footer.css
   │  │  │  ├─ Footer.tsx
   │  │  │  ├─ Header.css
   │  │  │  └─ Header.tsx
   │  │  └─ ui
   │  │     ├─ About.css
   │  │     ├─ About.tsx
   │  │     ├─ Contact.css
   │  │     ├─ Contact.tsx
   │  │     ├─ Hero.css
   │  │     ├─ Hero.tsx
   │  │     ├─ LoginModal.css
   │  │     ├─ LoginModal.tsx
   │  │     ├─ RotatingText.css
   │  │     ├─ RotatingText.tsx
   │  │     ├─ WaitlistModal.css
   │  │     └─ WaitlistModal.tsx
   │  ├─ declarations.d.ts
   │  ├─ index.tsx
   │  ├─ pages
   │  │  ├─ Dashboard.css
   │  │  ├─ Dashboard.tsx
   │  │  ├─ Home.css
   │  │  └─ Home.tsx
   │  └─ supabaseClient.ts
   └─ tsconfig.json

```