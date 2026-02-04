import axios from 'axios'

// Ensure base URL always ends with /api so routes like /invoices/:id/submit-to-erpnext resolve correctly
const raw = import.meta.env.VITE_API_URL || '/api'
const API_BASE_URL = raw.endsWith('/api') ? raw : raw.replace(/\/?$/, '') + '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface InvoiceItem {
  name: string
  quantity: number
  unit_price: number
  total_price: number
}

export interface ParsedInvoice {
  vendor_name: string
  invoice_number: string
  invoice_date: string
  total_amount: number
  items: InvoiceItem[]
  currency: string
}

export interface Invoice {
  id: string
  parsed_data: ParsedInvoice
  uploaded_at: string
  is_suspicious?: boolean
  risk_score?: number
  anomaly_explanation?: string
  submitted_to_erpnext?: boolean
  erpnext_invoice_name?: string
}

export interface AnomalyDetail {
  type: string
  item_name?: string
  severity: number
  description: string
}

export interface AnomalyResult {
  is_suspicious: boolean
  risk_score: number
  anomalies: AnomalyDetail[]
  explanation: string
}

export const invoiceApi = {
  // Upload invoice file
  uploadInvoice: async (file: File, syncToERPNext: boolean = false): Promise<Invoice> => {
    const formData = new FormData()
    formData.append('file', file)
    
    // Ensure boolean is converted to string properly
    const syncParam = syncToERPNext ? 'true' : 'false'
    console.log('API: syncToERPNext parameter:', syncParam, 'original:', syncToERPNext)
    
    try {
      const response = await api.post<Invoice>(
        `/invoices/upload?sync_to_erpnext=${syncParam}`, 
        formData, 
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 30000, // 30 second timeout
        }
      )
      return response.data
    } catch (error: any) {
      if (error.code === 'ECONNREFUSED' || error.message?.includes('Network Error')) {
        throw new Error('Cannot connect to backend server. Please make sure the server is running at http://localhost:8000')
      }
      throw error
    }
  },

  // Create invoice from JSON
  createInvoice: async (invoiceData: {
    vendor_name: string
    invoice_number: string
    invoice_date: string
    total_amount: number
    items: InvoiceItem[]
    currency?: string
  }): Promise<Invoice> => {
    const response = await api.post<Invoice>('/invoices/create', invoiceData)
    return response.data
  },

  // Get invoice by ID
  getInvoice: async (id: string): Promise<Invoice> => {
    const response = await api.get<Invoice>(`/invoices/${id}`)
    return response.data
  },

  // List all invoices
  listInvoices: async (): Promise<Invoice[]> => {
    const response = await api.get<Invoice[]>('/invoices')
    return response.data
  },

  // Analyze invoice for anomalies
  analyzeInvoice: async (id: string): Promise<AnomalyResult> => {
    try {
      const response = await api.post<AnomalyResult>(`/invoices/${id}/analyze`, {}, {
        timeout: 60000, // 60 second timeout
      })
      return response.data
    } catch (error: any) {
      if (error.code === 'ECONNREFUSED' || error.message?.includes('Network Error')) {
        throw new Error('Cannot connect to backend server. Please make sure the server is running at http://localhost:8000')
      }
      throw error
    }
  },

  // Delete invoice
  deleteInvoice: async (id: string): Promise<{ message: string; deleted: boolean }> => {
    const response = await api.delete<{ message: string; deleted: boolean }>(`/invoices/${id}`)
    return response.data
  },

  // Submit invoice to ERPNext
  submitToERPNext: async (id: string): Promise<Invoice> => {
    const response = await api.post<Invoice>(`/invoices/${id}/submit-to-erpnext`)
    return response.data
  },

  // Check if ERPNext is configured (optional integration)
  getErpnextHealth: async (): Promise<{ configured: boolean; message?: string }> => {
    try {
      const response = await api.get<{ configured: boolean; message?: string }>('/erpnext/health')
      return response.data
    } catch {
      return { configured: false, message: 'Could not check ERPNext status' }
    }
  },
}

export default api
