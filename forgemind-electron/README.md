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
└─ tsconfig.json

```