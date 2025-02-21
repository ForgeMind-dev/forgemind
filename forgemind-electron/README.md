# forgemind-electron
This is the console our users interact with to use our AI.

## Setup
1. Install [nvm](https://github.com/nvm-sh/nvm) or [nvm-windows](https://github.com/coreybutler/nvm-windows)
2. Install node v20.13.1: `nvm install 20.13.1`
3. use node v20.13.1 `nvm use 20.13.1`
4. Install dependencies: `npm install`
5. Development View: `npm run dev`
6. Production View: `npm run prod`
```
forgemind-electron
├─ .DS_Store
├─ .env
├─ .env.production
├─ README.md
├─ build
│  ├─ asset-manifest.json
│  ├─ electron.js
│  ├─ index.html
│  ├─ index.js
│  ├─ main
│  │  └─ main.js
│  ├─ renderer
│  │  ├─ App.js
│  │  ├─ components
│  │  │  ├─ BottomBar.js
│  │  │  ├─ ChatWindow.js
│  │  │  ├─ ConnectCADModal.js
│  │  │  ├─ OptimizeModal.js
│  │  │  ├─ RefineModal.js
│  │  │  ├─ RelationsModal.js
│  │  │  └─ Sidebar.js
│  │  └─ types.js
│  └─ static
│     ├─ css
│     │  ├─ main.dfb9036d.css
│     │  └─ main.dfb9036d.css.map
│     ├─ js
│     │  ├─ main.54d6e3c4.js
│     │  ├─ main.54d6e3c4.js.LICENSE.txt
│     │  └─ main.54d6e3c4.js.map
│     └─ media
│        ├─ full_logo.251516e40b8757722ca4.png
│        └─ logo_icon.ac50bb95b34189874ba7.png
├─ icons
│  ├─ icon.icns
│  ├─ icon.ico
│  └─ icons.png
├─ package-lock.json
├─ package.json
├─ public
│  ├─ electron.js
│  └─ index.html
├─ src
│  ├─ global.d.ts
│  ├─ index.tsx
│  ├─ main
│  │  └─ main.ts
│  └─ renderer
│     ├─ App.tsx
│     ├─ api.ts
│     ├─ assets
│     │  ├─ full_logo.png
│     │  ├─ logo_icon.png
│     │  └─ logo_icon1.png
│     ├─ components
│     │  ├─ BottomBar.tsx
│     │  ├─ ChatWindow.tsx
│     │  ├─ ConnectCADModal.tsx
│     │  ├─ OptimizeModal.tsx
│     │  ├─ RefineModal.tsx
│     │  ├─ RelationsModal.tsx
│     │  └─ Sidebar.tsx
│     ├─ styles
│     │  ├─ App.css
│     │  ├─ BottomBar.css
│     │  ├─ ChatWindow.css
│     │  ├─ Sidebar.css
│     │  ├─ buttons.css
│     │  ├─ global.css
│     │  ├─ layout.css
│     │  ├─ modal.css
│     │  └─ reset.css
│     └─ types.ts
└─ tsconfig.json

```