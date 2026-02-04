# Invoice Parser Frontend

Modern React frontend for the Invoice Parser and Anomaly Detection system.

## Features

- 🎨 Modern, responsive UI design
- 📤 Drag-and-drop invoice upload
- 📋 Invoice list view with filtering
- 🔍 Detailed invoice view with analysis
- ⚠️ Real-time anomaly detection display
- 🎯 Risk scoring visualization
- 📱 Mobile-friendly responsive design

## Tech Stack

- **React 18** with TypeScript
- **React Router** for navigation
- **Axios** for API communication
- **Vite** for fast development and building
- **CSS3** for styling

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

This will build the frontend and output to the `static` directory, which can be served by the FastAPI backend.

## Project Structure

```
frontend/
├── src/
│   ├── pages/          # Page components
│   │   ├── InvoiceUpload.tsx
│   │   ├── InvoiceList.tsx
│   │   └── InvoiceDetail.tsx
│   ├── services/       # API service layer
│   │   └── api.ts
│   ├── App.tsx         # Main app component with routing
│   ├── App.css         # App styles
│   ├── main.tsx        # Entry point
│   └── index.css       # Global styles
├── public/             # Static assets
├── index.html          # HTML template
├── vite.config.ts      # Vite configuration
├── tsconfig.json       # TypeScript configuration
└── package.json        # Dependencies
```

## Pages

### Invoice Upload (`/`)
- Drag-and-drop file upload
- Real-time processing feedback
- Immediate analysis results display

### Invoice List (`/invoices`)
- Grid view of all invoices
- Risk score indicators
- Quick navigation to details

### Invoice Detail (`/invoices/:id`)
- Complete invoice information
- Detailed anomaly analysis
- Itemized breakdown

## API Integration

The frontend communicates with the backend API through the `api.ts` service layer. All API calls are typed with TypeScript interfaces.

## Environment Variables

Create a `.env` file in the `frontend` directory:

```env
VITE_API_URL=http://localhost:8000/api
```

If not set, it defaults to `/api` (relative path).
