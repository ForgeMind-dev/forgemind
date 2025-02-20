# forgemind.dev

```
forgemind
├─ README.md
├─ forgemind-electron
│  ├─ .env
│  ├─ README.md
│  ├─ dist
│  │  ├─ index.js
│  │  ├─ main
│  │  │  └─ main.js
│  │  └─ renderer
│  │     ├─ App.js
│  │     ├─ components
│  │     │  ├─ BottomBar.js
│  │     │  ├─ ChatWindow.js
│  │     │  ├─ ConnectCADModal.js
│  │     │  ├─ OptimizeModal.js
│  │     │  ├─ RefineModal.js
│  │     │  ├─ RelationsModal.js
│  │     │  └─ Sidebar.js
│  │     └─ types.js
│  ├─ package-lock.json
│  ├─ package.json
│  ├─ public
│  │  └─ index.html
│  ├─ src
│  │  ├─ global.d.ts
│  │  ├─ index.tsx
│  │  ├─ main
│  │  │  └─ main.ts
│  │  └─ renderer
│  │     ├─ App.tsx
│  │     ├─ assets
│  │     │  ├─ full_logo.png
│  │     │  ├─ logo_icon.png
│  │     │  └─ logo_icon1.png
│  │     ├─ components
│  │     │  ├─ BottomBar.tsx
│  │     │  ├─ ChatWindow.tsx
│  │     │  ├─ ConnectCADModal.tsx
│  │     │  ├─ OptimizeModal.tsx
│  │     │  ├─ RefineModal.tsx
│  │     │  ├─ RelationsModal.tsx
│  │     │  └─ Sidebar.tsx
│  │     ├─ styles
│  │     │  ├─ App.css
│  │     │  ├─ BottomBar.css
│  │     │  ├─ ChatWindow.css
│  │     │  ├─ Sidebar.css
│  │     │  ├─ buttons.css
│  │     │  ├─ global.css
│  │     │  ├─ layout.css
│  │     │  ├─ modal.css
│  │     │  └─ reset.css
│  │     └─ types.ts
│  └─ tsconfig.json
├─ forgemind-fusion
│  ├─ .env
│  ├─ AddInIcon.svg
│  ├─ ForgeMind.manifest
│  ├─ ForgeMind.py
│  ├─ commands
│  │  ├─ Basic
│  │  │  ├─ __init__.py
│  │  │  ├─ entry.py
│  │  │  └─ resources
│  │  │     ├─ 16x16.png
│  │  │     ├─ 16x16@2x.png
│  │  │     ├─ 32x32.png
│  │  │     └─ 32x32@2x.png
│  │  ├─ Browser
│  │  │  ├─ __init__.py
│  │  │  ├─ entry.py
│  │  │  └─ resources
│  │  │     ├─ 16x16.png
│  │  │     ├─ 32x32.png
│  │  │     └─ html
│  │  │        ├─ index.html
│  │  │        └─ static
│  │  │           └─ palette.js
│  │  ├─ Everything
│  │  │  ├─ __init__.py
│  │  │  ├─ entry.py
│  │  │  └─ resources
│  │  │     ├─ 16x16.png
│  │  │     ├─ 16x16@2x.png
│  │  │     ├─ 32x32.png
│  │  │     ├─ 32x32@2x.png
│  │  │     └─ buttons
│  │  │        ├─ 16x16-dark.png
│  │  │        ├─ 16x16-disabled.png
│  │  │        ├─ 16x16.png
│  │  │        ├─ 32x32-dark.png
│  │  │        ├─ 32x32-disabled.png
│  │  │        └─ 32x32.png
│  │  ├─ Info
│  │  │  ├─ __init__.py
│  │  │  ├─ entry.py
│  │  │  └─ resources
│  │  │     ├─ 16x16.png
│  │  │     ├─ 16x16@2x.png
│  │  │     ├─ 32x32.png
│  │  │     └─ 32x32@2x.png
│  │  ├─ Selections
│  │  │  ├─ __init__.py
│  │  │  ├─ entry.py
│  │  │  └─ resources
│  │  │     ├─ 16x16.png
│  │  │     ├─ 16x16@2x.png
│  │  │     ├─ 32x32.png
│  │  │     └─ 32x32@2x.png
│  │  ├─ Table
│  │  │  ├─ __init__.py
│  │  │  ├─ entry.py
│  │  │  └─ resources
│  │  │     ├─ 16x16-dark.png
│  │  │     ├─ 16x16.png
│  │  │     ├─ 16x16@2x-dark.png
│  │  │     ├─ 16x16@2x.png
│  │  │     ├─ 32x32-dark.png
│  │  │     ├─ 32x32.png
│  │  │     ├─ 32x32@2x-dark.png
│  │  │     └─ 32x32@2x.png
│  │  └─ __init__.py
│  ├─ config.py
│  ├─ icon.png
│  ├─ lib
│  │  └─ fusionAddInUtils
│  │     ├─ __init__.py
│  │     ├─ event_utils.py
│  │     └─ general_utils.py
│  └─ logic
│     ├─ __init__.py
│     └─ main.py
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