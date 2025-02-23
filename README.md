# forgemind

**READ THE FUCKING MANUAL**

This is the monorepo of ForgeMind. The reliability of this product is dependent on all parts of the stack being in sync with each other all of the time.

1. Do **not** try to run these applications without using the provided instructions. We want to make sure that our code does not just work on your computer.
2. Keep dependencies (requirements.txt, package.json, etc.) synchronized. 
3. We do not have a testing process, so we have to keep a healthy environment.
4. Make sure that you are modifying git history at the root level directory, not just within each subfolder (forgemind-electron, forgemind-backend, etc).
5. As you begin to touch the CAD integrations, be extra careful to **READ THE FUCKING MANUAL**

```
forgemind
├─ forgemind-backend
│  ├─ app.py
│  ├─ Procfile
│  ├─ README.md
│  ├─ requirements.txt
│  ├─ runtime.txt
│  ├─ run_local_mac.sh
│  └─ run_local_windows.ps1
├─ forgemind-fusion
│  ├─ AddInIcon.svg
│  ├─ commands
│  │  ├─ Info
│  │  │  ├─ entry.py
│  │  │  ├─ resources
│  │  │  │  ├─ 16x16.png
│  │  │  │  ├─ 16x16@2x.png
│  │  │  │  ├─ 32x32.png
│  │  │  │  └─ 32x32@2x.png
│  │  │  ├─ __init__.py
│  │  │  └─ __pycache__
│  │  │     ├─ entry.cpython-312.pyc
│  │  │     └─ __init__.cpython-312.pyc
│  │  ├─ __init__.py
│  │  └─ __pycache__
│  │     └─ __init__.cpython-312.pyc
│  ├─ config.py
│  ├─ ForgeMind.manifest
│  ├─ ForgeMind.py
│  ├─ icon.png
│  ├─ lib
│  │  └─ fusionAddInUtils
│  │     ├─ event_utils.py
│  │     ├─ general_utils.py
│  │     ├─ __init__.py
│  │     └─ __pycache__
│  │        ├─ event_utils.cpython-312.pyc
│  │        ├─ general_utils.cpython-312.pyc
│  │        └─ __init__.cpython-312.pyc
│  ├─ logic
│  │  ├─ main.py
│  │  ├─ __init__.py
│  │  └─ __pycache__
│  │     ├─ main.cpython-312.pyc
│  │     └─ __init__.cpython-312.pyc
│  └─ __pycache__
│     └─ config.cpython-312.pyc
├─ forgemind-webapp
│  ├─ electron
│  │  ├─ icons
│  │  │  ├─ icon.icns
│  │  │  ├─ icon.ico
│  │  │  └─ icons.png
│  │  ├─ package-lock.json
│  │  ├─ package.json
│  │  ├─ public
│  │  │  ├─ electron.js
│  │  │  └─ index.html
│  │  ├─ README.md
│  │  ├─ server.js
│  │  ├─ src
│  │  │  ├─ global.d.ts
│  │  │  ├─ index.tsx
│  │  │  ├─ main
│  │  │  │  └─ main.ts
│  │  │  └─ renderer
│  │  │     ├─ api.ts
│  │  │     ├─ App.tsx
│  │  │     ├─ assets
│  │  │     │  ├─ full_logo.png
│  │  │     │  ├─ logo_icon.png
│  │  │     │  ├─ logo_icon1.png
│  │  │     │  └─ trash_bin.png
│  │  │     ├─ components
│  │  │     │  ├─ BottomBar.tsx
│  │  │     │  ├─ ChatWindow.tsx
│  │  │     │  ├─ ConnectCADModal.tsx
│  │  │     │  ├─ Header.tsx
│  │  │     │  ├─ OptimizeModal.tsx
│  │  │     │  ├─ RefineModal.tsx
│  │  │     │  ├─ RelationsModal.tsx
│  │  │     │  └─ Sidebar.tsx
│  │  │     ├─ styles
│  │  │     │  ├─ BottomBar.css
│  │  │     │  ├─ buttons.css
│  │  │     │  ├─ ChatWindow.css
│  │  │     │  ├─ Header.css
│  │  │     │  ├─ layout.css
│  │  │     │  ├─ modal.css
│  │  │     │  ├─ reset.css
│  │  │     │  └─ Sidebar.css
│  │  │     └─ types.ts
│  │  └─ tsconfig.json
│  ├─ package-lock.json
│  ├─ package.json
│  ├─ Procfile
│  ├─ public
│  │  ├─ favicon.ico
│  │  ├─ index.html
│  │  └─ manifest.json
│  ├─ README.md
│  ├─ src
│  │  ├─ App.css
│  │  ├─ App.tsx
│  │  ├─ assets
│  │  │  ├─ images
│  │  │  │  ├─ logo.png
│  │  │  │  ├─ logo1.png
│  │  │  │  ├─ logo_black_cropped2.png
│  │  │  │  ├─ logo_black_cropped3.png
│  │  │  │  ├─ logo_black_cropped4.png
│  │  │  │  ├─ logo_black_cropped5.1.png
│  │  │  │  └─ logo_black_cropped6.png
│  │  │  └─ styles
│  │  │     └─ global.css
│  │  ├─ components
│  │  │  ├─ archive
│  │  │  │  ├─ CallToAction.css
│  │  │  │  ├─ CallToAction.tsx
│  │  │  │  ├─ FeatureCard.css
│  │  │  │  ├─ FeatureCard.tsx
│  │  │  │  ├─ FeaturesSection.css
│  │  │  │  ├─ FeaturesSection.tsx
│  │  │  │  ├─ HowItWorks.css
│  │  │  │  ├─ HowItWorks.tsx
│  │  │  │  ├─ OverviewSection.css
│  │  │  │  ├─ OverviewSection.tsx
│  │  │  │  ├─ TeamSection.css
│  │  │  │  ├─ TeamSection.tsx
│  │  │  │  ├─ TechShowcase.css
│  │  │  │  └─ TechShowcase.tsx
│  │  │  ├─ layout
│  │  │  │  ├─ Footer.css
│  │  │  │  ├─ Footer.tsx
│  │  │  │  ├─ Header.css
│  │  │  │  └─ Header.tsx
│  │  │  └─ ui
│  │  │     ├─ About.css
│  │  │     ├─ About.tsx
│  │  │     ├─ Contact.css
│  │  │     ├─ Contact.tsx
│  │  │     ├─ Hero.css
│  │  │     ├─ Hero.tsx
│  │  │     ├─ LoginModal.css
│  │  │     ├─ LoginModal.tsx
│  │  │     ├─ RotatingText.css
│  │  │     ├─ RotatingText.tsx
│  │  │     ├─ WaitlistModal.css
│  │  │     └─ WaitlistModal.tsx
│  │  ├─ declarations.d.ts
│  │  ├─ index.tsx
│  │  ├─ pages
│  │  │  ├─ Dashboard.css
│  │  │  ├─ Dashboard.tsx
│  │  │  ├─ Home.css
│  │  │  └─ Home.tsx
│  │  └─ supabaseClient.ts
│  └─ tsconfig.json
└─ README.md

```