"""Custom exceptions for the application."""


class InvoiceParserException(Exception):
    """Base exception for invoice parser errors."""
    pass


class InvoiceNotFoundError(InvoiceParserException):
    """Raised when an invoice is not found."""
    pass


class InvalidInvoiceFormatError(InvoiceParserException):
    """Raised when invoice format is invalid."""
    pass


class ParsingError(InvoiceParserException):
    """Raised when invoice parsing fails."""
    pass
