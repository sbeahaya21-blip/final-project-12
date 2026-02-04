import { Routes, Route, Link, useLocation } from 'react-router-dom'
import InvoiceUpload from './pages/InvoiceUpload'
import InvoiceList from './pages/InvoiceList'
import InvoiceDetail from './pages/InvoiceDetail'
import './App.css'

function App() {
  const location = useLocation()

  return (
    <div className="app">
      {/* ERPNext-style Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <Link to="/" className="sidebar-logo">
            <span className="logo-icon">📄</span>
            <span className="logo-text">Invoice Parser</span>
          </Link>
        </div>
        <nav className="sidebar-nav">
          <Link 
            to="/" 
            className={location.pathname === '/' ? 'nav-item active' : 'nav-item'}
          >
            <span className="nav-icon">⬆️</span>
            <span className="nav-label">Upload Invoice</span>
          </Link>
          <Link 
            to="/invoices" 
            className={location.pathname.startsWith('/invoices') && location.pathname !== '/' ? 'nav-item active' : 'nav-item'}
          >
            <span className="nav-icon">📋</span>
            <span className="nav-label">All Invoices</span>
          </Link>
        </nav>
      </aside>

      {/* Main Content Area */}
      <div className="main-wrapper">
        <header className="topbar">
          <div className="topbar-content">
            <h1 className="page-title">
              {location.pathname === '/' && 'Upload Invoice'}
              {location.pathname === '/invoices' && 'All Invoices'}
              {location.pathname.startsWith('/invoices/') && location.pathname !== '/invoices' && 'Invoice Details'}
            </h1>
          </div>
        </header>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<InvoiceUpload />} />
            <Route path="/invoices" element={<InvoiceList />} />
            <Route path="/invoices/:id" element={<InvoiceDetail />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App
