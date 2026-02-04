import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { invoiceApi, Invoice, AnomalyResult } from '../services/api'
import './InvoiceDetail.css'

function InvoiceDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [invoice, setInvoice] = useState<Invoice | null>(null)
  const [analysis, setAnalysis] = useState<AnomalyResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (id) {
      loadInvoice()
    }
  }, [id])

  const loadInvoice = async () => {
    if (!id) return

    try {
      setLoading(true)
      setError(null)
      const invoiceData = await invoiceApi.getInvoice(id)
      setInvoice(invoiceData)

      // If invoice already has analysis, use it
      if (invoiceData.risk_score !== undefined) {
        setAnalysis({
          is_suspicious: invoiceData.is_suspicious || false,
          risk_score: invoiceData.risk_score,
          anomalies: [],
          explanation: invoiceData.anomaly_explanation || '',
        })
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load invoice')
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async () => {
    if (!id) return

    try {
      setAnalyzing(true)
      setError(null)
      const analysisResult = await invoiceApi.analyzeInvoice(id)
      setAnalysis(analysisResult)
      // Reload invoice to get updated risk score
      await loadInvoice()
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to analyze invoice')
    } finally {
      setAnalyzing(false)
    }
  }

  const handleSubmitToERPNext = async () => {
    if (!invoice) return
    // Use invoice.id from loaded state so we always submit the same invoice we're viewing
    const invoiceId = invoice.id

    if (!window.confirm('Are you sure you want to submit this invoice to ERPNext?')) {
      return
    }

    try {
      setSubmitting(true)
      setError(null)
      const submitUrl = `/invoices/${invoiceId}/submit-to-erpnext`
      if (typeof window !== 'undefined' && (window as any).__DEBUG_API) {
        console.log('Submit to ERPNext: POST', submitUrl, 'invoiceId=', invoiceId)
      }
      const updatedInvoice = await invoiceApi.submitToERPNext(invoiceId)
      setInvoice(updatedInvoice)
      alert(`Invoice submitted successfully to ERPNext!\nERPNext Invoice: ${updatedInvoice.erpnext_invoice_name || 'N/A'}`)
    } catch (err: any) {
      const detail = err.response?.data?.detail || err.message || 'Failed to submit invoice to ERPNext'
      const status = err.response?.status
      const requestUrl = err.config?.url != null ? `${err.config.baseURL || ''}${err.config.url}` : ''
      const isNotFound = status === 404
      const extra = requestUrl ? ` (POST ${requestUrl})` : ''
      setError(
        isNotFound
          ? `${detail}${extra} If the server restarted, upload the invoice again.`
          : detail + (requestUrl ? ` (POST ${requestUrl})` : '')
      )
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async () => {
    if (!id || !invoice) return

    const confirmMessage = invoice.submitted_to_erpnext
      ? `Warning: This invoice has been submitted to ERPNext.\n\nAre you sure you want to delete invoice ${invoice.parsed_data.invoice_number}?\n\nThis action cannot be undone.`
      : `Are you sure you want to delete invoice ${invoice.parsed_data.invoice_number}?\n\nThis action cannot be undone.`
    
    if (!window.confirm(confirmMessage)) {
      return
    }

    try {
      await invoiceApi.deleteInvoice(id)
      // Navigate back to invoice list
      navigate('/invoices')
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to delete invoice')
    }
  }

  const getRiskClass = (score: number) => {
    if (score >= 70) return 'high'
    if (score >= 50) return 'medium'
    return 'low'
  }

  if (loading) {
    return (
      <div className="invoice-detail">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading invoice...</p>
        </div>
      </div>
    )
  }

  if (error && !invoice) {
    return (
      <div className="invoice-detail">
        <div className="error-message">
          <strong>Error:</strong> {error}
          <button className="btn btn-secondary" onClick={() => navigate('/invoices')}>
            Back to List
          </button>
        </div>
      </div>
    )
  }

  if (!invoice) {
    return (
      <div className="invoice-detail">
        <div className="error-message">
          Invoice not found
          <button className="btn btn-secondary" onClick={() => navigate('/invoices')}>
            Back to List
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="invoice-detail">
      <div className="detail-header">
        <button className="back-button" onClick={() => navigate('/invoices')}>
          ← Back to List
        </button>
        <div className="header-actions">
          {invoice.submitted_to_erpnext && (
            <div className="submitted-status">
              ✓ Submitted to ERPNext
              {invoice.erpnext_invoice_name && (
                <span className="erpnext-name"> ({invoice.erpnext_invoice_name})</span>
              )}
            </div>
          )}
          {!analysis && (
            <button
              className="btn btn-primary"
              onClick={handleAnalyze}
              disabled={analyzing}
            >
              {analyzing ? 'Analyzing...' : 'Analyze Invoice'}
            </button>
          )}
          {!invoice.submitted_to_erpnext && (
            <button
              className="btn btn-success"
              onClick={handleSubmitToERPNext}
              disabled={submitting}
              title="Submit to ERPNext"
            >
              {submitting ? 'Submitting...' : '📤 Submit to ERPNext'}
            </button>
          )}
          <button
            className="btn btn-danger"
            onClick={handleDelete}
            title="Delete this invoice"
          >
            🗑️ Delete Invoice
          </button>
        </div>
      </div>

      {error && (
        <div className={`error-message ${error.includes('ERPNext is not configured') ? 'erpnext-notice' : ''}`}>
          <span>
            <strong>{error.includes('ERPNext is not configured') ? 'Note:' : 'Error:'}</strong> {error}
            {error.includes('ERPNext is not configured') && (
              <span className="erpnext-notice-hint">Only &quot;Submit to ERPNext&quot; needs this. You can still view and manage this invoice.</span>
            )}
          </span>
          {error.includes('ERPNext is not configured') && (
            <button type="button" className="btn btn-secondary" onClick={() => setError(null)}>Dismiss</button>
          )}
        </div>
      )}

      <div className="detail-content">
        <div className={`invoice-card ${invoice.is_suspicious ? 'suspicious' : 'safe'}`}>
          <div className="card-header-section">
            <div>
              <h1>{invoice.parsed_data.vendor_name}</h1>
              <p className="invoice-meta">
                Invoice #{invoice.parsed_data.invoice_number} •{' '}
                {new Date(invoice.parsed_data.invoice_date).toLocaleDateString()}
              </p>
            </div>
            {invoice.is_suspicious && (
              <span className="suspicious-badge-large">⚠️ SUSPICIOUS</span>
            )}
          </div>

          {analysis && (
            <div className="analysis-section">
              <div className="analysis-header">
                <h2>Analysis Results</h2>
                <div className={`risk-badge-large ${getRiskClass(analysis.risk_score)}`}>
                  Risk Score: {analysis.risk_score}/100
                </div>
              </div>

              {analysis.anomalies.length > 0 && (
                <div className="anomalies-section">
                  <h3>Detected Anomalies ({analysis.anomalies.length})</h3>
                  <div className="anomalies-list">
                    {analysis.anomalies.map((anomaly, index) => (
                      <div key={index} className="anomaly-item">
                        <div className="anomaly-header">
                          <span className="anomaly-type">
                            {anomaly.type.replace('_', ' ').toUpperCase()}
                          </span>
                          {anomaly.item_name && (
                            <span className="anomaly-item-name">{anomaly.item_name}</span>
                          )}
                          <span className="anomaly-severity">
                            Severity: {anomaly.severity}/100
                          </span>
                        </div>
                        <p className="anomaly-description">{anomaly.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="explanation-box">
                <h3>Explanation</h3>
                <p>{analysis.explanation}</p>
              </div>
            </div>
          )}

          <div className="invoice-info-section">
            <h2>Invoice Information</h2>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Vendor Name</span>
                <span className="info-value">{invoice.parsed_data.vendor_name}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Invoice Number</span>
                <span className="info-value">{invoice.parsed_data.invoice_number}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Invoice Date</span>
                <span className="info-value">
                  {new Date(invoice.parsed_data.invoice_date).toLocaleDateString()}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Total Amount</span>
                <span className="info-value amount">
                  ${invoice.parsed_data.total_amount.toFixed(2)} {invoice.parsed_data.currency}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Uploaded At</span>
                <span className="info-value">
                  {new Date(invoice.uploaded_at).toLocaleString()}
                </span>
              </div>
              {invoice.risk_score !== undefined && (
                <div className="info-item">
                  <span className="info-label">Risk Score</span>
                  <span className={`info-value risk ${getRiskClass(invoice.risk_score)}`}>
                    {invoice.risk_score}/100
                  </span>
                </div>
              )}
            </div>
          </div>

          <div className="items-section">
            <h2>Invoice Items</h2>
            <div className="items-table-wrapper">
              <table className="items-table">
                <thead>
                  <tr>
                    <th>Item Name</th>
                    <th>Quantity</th>
                    <th>Unit Price</th>
                    <th>Total Price</th>
                  </tr>
                </thead>
                <tbody>
                  {invoice.parsed_data.items.map((item, index) => (
                    <tr key={index}>
                      <td>{item.name}</td>
                      <td>{item.quantity}</td>
                      <td>${item.unit_price.toFixed(2)}</td>
                      <td>${item.total_price.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr>
                    <td colSpan={3} className="total-label">
                      <strong>Total</strong>
                    </td>
                    <td className="total-value">
                      <strong>${invoice.parsed_data.total_amount.toFixed(2)}</strong>
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default InvoiceDetail
