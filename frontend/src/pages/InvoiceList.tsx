import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { invoiceApi, Invoice } from '../services/api'
import './InvoiceList.css'

function InvoiceList() {
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedInvoiceId, setSelectedInvoiceId] = useState<string | null>(null)
  const [submittingId, setSubmittingId] = useState<string | null>(null)

  useEffect(() => {
    loadInvoices()
  }, [])

  const loadInvoices = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await invoiceApi.listInvoices()
      // Sort by uploaded_at descending (newest first)
      data.sort((a, b) => 
        new Date(b.uploaded_at).getTime() - new Date(a.uploaded_at).getTime()
      )
      setInvoices(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load invoices')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (invoiceId: string, invoiceNumber: string) => {
    const invoice = invoices.find(inv => inv.id === invoiceId)
    if (invoice?.submitted_to_erpnext) {
      if (!window.confirm(`Warning: This invoice has been submitted to ERPNext.\n\nAre you sure you want to delete invoice ${invoiceNumber}?`)) {
        return
      }
    } else {
      if (!window.confirm(`Are you sure you want to delete invoice ${invoiceNumber}?`)) {
        return
      }
    }

    try {
      await invoiceApi.deleteInvoice(invoiceId)
      // Reload the list
      await loadInvoices()
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to delete invoice')
    }
  }

  const handleSubmitToERPNext = async (invoiceId: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (!window.confirm('Are you sure you want to submit this invoice to ERPNext?')) {
      return
    }

    try {
      setSubmittingId(invoiceId)
      setError(null)
      await invoiceApi.submitToERPNext(invoiceId)
      // Reload the list to show updated status
      await loadInvoices()
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to submit invoice to ERPNext')
    } finally {
      setSubmittingId(null)
    }
  }

  const getRiskClass = (score?: number) => {
    if (!score) return 'unknown'
    if (score >= 70) return 'high'
    if (score >= 50) return 'medium'
    return 'low'
  }

  if (loading) {
    return (
      <div className="invoice-list">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading invoices...</p>
        </div>
      </div>
    )
  }

  // ERPNext "not configured" is not a blocking error — show list and a dismissible notice
  const isErpnextConfigError = error?.includes('ERPNext is not configured')
  if (error && !isErpnextConfigError) {
    return (
      <div className="invoice-list">
        <div className="error-message">
          <strong>Error:</strong> {error}
          <button className="retry-button" onClick={loadInvoices}>
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="invoice-list">
      {isErpnextConfigError && (
        <div className="error-message erpnext-notice">
          <strong>Note:</strong> {error}
          <span className="erpnext-notice-hint">Only &quot;Submit to ERPNext&quot; needs this. You can still view and manage invoices.</span>
          <button className="retry-button" type="button" onClick={() => setError(null)}>
            Dismiss
          </button>
        </div>
      )}
      <div className="list-header">
        <h1>All Invoices</h1>
        <button className="btn btn-primary" onClick={loadInvoices}>
          Refresh
        </button>
      </div>

      {invoices.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📄</div>
          <h2>No invoices yet</h2>
          <p>Upload your first invoice to get started</p>
          <Link to="/" className="btn btn-primary">
            Upload Invoice
          </Link>
        </div>
      ) : (
        <div className="invoices-table-container">
          <table className="invoices-table">
            <thead>
              <tr>
                <th>Vendor</th>
                <th>Invoice #</th>
                <th>Date</th>
                <th>Amount</th>
                <th>Items</th>
                <th>Risk Score</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {invoices.map((invoice) => (
                <tr 
                  key={invoice.id}
                  className={invoice.is_suspicious ? 'suspicious-row' : ''}
                >
                  <td>
                    <div className="vendor-cell">
                      <strong>{invoice.parsed_data.vendor_name}</strong>
                      {invoice.is_suspicious && (
                        <span className="suspicious-badge-inline">⚠️ Suspicious</span>
                      )}
                    </div>
                  </td>
                  <td>
                    <Link to={`/invoices/${invoice.id}`} className="invoice-link">
                      {invoice.parsed_data.invoice_number}
                    </Link>
                  </td>
                  <td>
                    {new Date(invoice.parsed_data.invoice_date).toLocaleDateString()}
                  </td>
                  <td className="amount-cell">
                    ${invoice.parsed_data.total_amount.toFixed(2)}
                  </td>
                  <td>
                    <span 
                      className="items-clickable"
                      onClick={(e) => {
                        e.preventDefault()
                        e.stopPropagation()
                        setSelectedInvoiceId(invoice.id)
                      }}
                      title="Click to view items"
                    >
                      {invoice.parsed_data.items.length} item(s)
                    </span>
                  </td>
                  <td>
                    {invoice.risk_score !== undefined ? (
                      <span className={`risk-badge-table ${getRiskClass(invoice.risk_score)}`}>
                        {invoice.risk_score}/100
                      </span>
                    ) : (
                      <span className="risk-badge-table unknown">-</span>
                    )}
                  </td>
                  <td>
                    {invoice.submitted_to_erpnext ? (
                      <div className="submitted-status-inline">
                        <span className="submitted-icon">✓</span>
                        <span>Submitted</span>
                        {invoice.erpnext_invoice_name && (
                          <span className="erpnext-name-small"> ({invoice.erpnext_invoice_name})</span>
                        )}
                      </div>
                    ) : (
                      <span className="not-submitted">Not Submitted</span>
                    )}
                  </td>
                  <td>
                    <div className="table-actions">
                      {!invoice.submitted_to_erpnext && (
                        <button
                          className="submit-btn-small"
                          onClick={(e) => {
                            e.preventDefault()
                            e.stopPropagation()
                            handleSubmitToERPNext(invoice.id, e)
                          }}
                          disabled={submittingId === invoice.id}
                          title="Submit to ERPNext"
                        >
                          {submittingId === invoice.id ? '...' : '📤'}
                        </button>
                      )}
                      <button
                        className="delete-btn-small"
                        onClick={(e) => {
                          e.preventDefault()
                          e.stopPropagation()
                          handleDelete(invoice.id, invoice.parsed_data.invoice_number)
                        }}
                        title="Delete invoice"
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Items Modal */}
      {selectedInvoiceId && (
        <div className="items-modal-overlay" onClick={() => setSelectedInvoiceId(null)}>
          <div className="items-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>
                {invoices.find(inv => inv.id === selectedInvoiceId)?.parsed_data.invoice_number} - Items
              </h2>
              <button 
                className="modal-close-btn"
                onClick={() => setSelectedInvoiceId(null)}
                aria-label="Close"
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="items-list">
                {invoices.find(inv => inv.id === selectedInvoiceId)?.parsed_data.items.map((item, index) => (
                  <div key={index} className="item-row">
                    <div className="item-info">
                      <div className="item-name">{item.name}</div>
                      <div className="item-details">
                        <span>Qty: {item.quantity}</span>
                        <span>Unit Price: ${item.unit_price.toFixed(2)}</span>
                      </div>
                    </div>
                    <div className="item-total">
                      ${item.total_price.toFixed(2)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default InvoiceList
