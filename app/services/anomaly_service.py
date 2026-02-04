"""Anomaly detection service."""
from typing import List
from app.models.invoice import Invoice, InvoiceItem
from app.models.anomaly import AnomalyResult, AnomalyDetail, AnomalyType
from app.services.storage_service import StorageService


class AnomalyService:
    """Service for detecting anomalies in invoices."""
    
    def __init__(self, storage_service: StorageService):
        self.storage = storage_service
    
    def analyze_invoice(self, invoice: Invoice) -> AnomalyResult:
        """
        Analyze an invoice for anomalies by comparing with historical data.
        
        Returns:
            AnomalyResult with risk score and explanations
        """
        historical_invoices = self.storage.get_by_vendor(
            invoice.parsed_data.vendor_name
        )
        
        # Exclude the current invoice from historical data
        historical_invoices = [
            inv for inv in historical_invoices
            if inv.id != invoice.id
        ]
        
        anomalies: List[AnomalyDetail] = []
        
        if not historical_invoices:
            # No historical data - low risk but note it
            return AnomalyResult(
                is_suspicious=False,
                risk_score=10,
                anomalies=[],
                explanation="No historical data available for this vendor. First invoice from this vendor."
            )
        
        # Check for price increases
        price_anomalies = self._check_price_increases(
            invoice, historical_invoices
        )
        anomalies.extend(price_anomalies)
        
        # Check for quantity deviations
        quantity_anomalies = self._check_quantity_deviations(
            invoice, historical_invoices
        )
        anomalies.extend(quantity_anomalies)
        
        # Check for new items
        new_item_anomalies = self._check_new_items(
            invoice, historical_invoices
        )
        anomalies.extend(new_item_anomalies)
        
        # Check for total amount deviation
        amount_anomalies = self._check_amount_deviation(
            invoice, historical_invoices
        )
        anomalies.extend(amount_anomalies)
        
        # Calculate overall risk score
        risk_score = self._calculate_risk_score(anomalies)
        is_suspicious = risk_score >= 50
        
        # Generate human-readable explanation
        explanation = self._generate_explanation(anomalies, risk_score)
        
        return AnomalyResult(
            is_suspicious=is_suspicious,
            risk_score=risk_score,
            anomalies=anomalies,
            explanation=explanation
        )
    
    def _check_price_increases(
        self, invoice: Invoice, historical: List[Invoice]
    ) -> List[AnomalyDetail]:
        """Check for sudden price increases."""
        anomalies = []
        
        # Build historical price map
        historical_prices: dict[str, List[float]] = {}
        for hist_inv in historical:
            for item in hist_inv.parsed_data.items:
                if item.name not in historical_prices:
                    historical_prices[item.name] = []
                historical_prices[item.name].append(item.unit_price)
        
        # Check current invoice prices
        for item in invoice.parsed_data.items:
            if item.name in historical_prices:
                avg_price = sum(historical_prices[item.name]) / len(historical_prices[item.name])
                price_increase_pct = ((item.unit_price - avg_price) / avg_price) * 100
                
                if price_increase_pct > 20:  # More than 20% increase
                    severity = min(100, int(30 + (price_increase_pct - 20) * 2))
                    anomalies.append(AnomalyDetail(
                        type=AnomalyType.PRICE_INCREASE,
                        item_name=item.name,
                        severity=severity,
                        description=f"Price increased by {price_increase_pct:.1f}% "
                                   f"(from avg ${avg_price:.2f} to ${item.unit_price:.2f})"
                    ))
        
        return anomalies
    
    def _check_quantity_deviations(
        self, invoice: Invoice, historical: List[Invoice]
    ) -> List[AnomalyDetail]:
        """Check for unreasonable quantity deviations."""
        anomalies = []
        
        # Build historical quantity map
        historical_quantities: dict[str, List[float]] = {}
        for hist_inv in historical:
            for item in hist_inv.parsed_data.items:
                if item.name not in historical_quantities:
                    historical_quantities[item.name] = []
                historical_quantities[item.name].append(item.quantity)
        
        # Check current invoice quantities
        for item in invoice.parsed_data.items:
            if item.name in historical_quantities:
                avg_quantity = sum(historical_quantities[item.name]) / len(historical_quantities[item.name])
                max_quantity = max(historical_quantities[item.name])
                
                # Check if quantity is significantly higher than average
                if item.quantity > avg_quantity * 2:  # More than 2x average
                    deviation_pct = ((item.quantity - avg_quantity) / avg_quantity) * 100
                    severity = min(100, int(25 + (deviation_pct - 100) * 0.3))
                    anomalies.append(AnomalyDetail(
                        type=AnomalyType.QUANTITY_DEVIATION,
                        item_name=item.name,
                        severity=severity,
                        description=f"Quantity is {deviation_pct:.1f}% above average "
                                   f"(avg: {avg_quantity:.1f}, current: {item.quantity:.1f})"
                    ))
                # Check if quantity exceeds historical maximum significantly
                elif item.quantity > max_quantity * 1.5:  # 50% more than max ever seen
                    severity = min(100, int(40 + (item.quantity / max_quantity - 1.5) * 20))
                    anomalies.append(AnomalyDetail(
                        type=AnomalyType.QUANTITY_DEVIATION,
                        item_name=item.name,
                        severity=severity,
                        description=f"Quantity exceeds historical maximum by "
                                   f"{((item.quantity / max_quantity - 1) * 100):.1f}% "
                                   f"(max: {max_quantity:.1f}, current: {item.quantity:.1f})"
                    ))
        
        return anomalies
    
    def _check_new_items(
        self, invoice: Invoice, historical: List[Invoice]
    ) -> List[AnomalyDetail]:
        """Check for new items that never appeared before."""
        anomalies = []
        
        # Build set of all historical item names
        historical_items = set()
        for hist_inv in historical:
            for item in hist_inv.parsed_data.items:
                historical_items.add(item.name.lower())
        
        # Check for new items
        for item in invoice.parsed_data.items:
            if item.name.lower() not in historical_items:
                # Calculate severity based on item value
                item_value_pct = (item.total_price / invoice.parsed_data.total_amount) * 100
                severity = min(100, int(20 + item_value_pct * 0.5))
                
                anomalies.append(AnomalyDetail(
                    type=AnomalyType.NEW_ITEM,
                    item_name=item.name,
                    severity=severity,
                    description=f"New item '{item.name}' never seen before for this vendor "
                               f"(value: ${item.total_price:.2f}, {item_value_pct:.1f}% of total)"
                ))
        
        return anomalies
    
    def _check_amount_deviation(
        self, invoice: Invoice, historical: List[Invoice]
    ) -> List[AnomalyDetail]:
        """Check for total amount deviations."""
        anomalies = []
        
        historical_amounts = [
            inv.parsed_data.total_amount for inv in historical
        ]
        
        if not historical_amounts:
            return anomalies
        
        avg_amount = sum(historical_amounts) / len(historical_amounts)
        min_amount = min(historical_amounts)
        max_amount = max(historical_amounts)
        current_amount = invoice.parsed_data.total_amount
        
        # Check if amount deviates significantly from average
        deviation_pct = abs((current_amount - avg_amount) / avg_amount) * 100
        
        if deviation_pct > 30:  # More than 30% deviation
            severity = min(100, int(35 + (deviation_pct - 30) * 1.5))
            direction = "above" if current_amount > avg_amount else "below"
            anomalies.append(AnomalyDetail(
                type=AnomalyType.AMOUNT_DEVIATION,
                severity=severity,
                description=f"Total amount is {deviation_pct:.1f}% {direction} average "
                           f"(avg: ${avg_amount:.2f}, current: ${current_amount:.2f}, "
                           f"range: ${min_amount:.2f} - ${max_amount:.2f})"
            ))
        
        return anomalies
    
    def _calculate_risk_score(self, anomalies: List[AnomalyDetail]) -> int:
        """Calculate overall risk score from anomalies."""
        if not anomalies:
            return 0
        
        # Weighted average of severities, with higher weight for more anomalies
        total_severity = sum(anomaly.severity for anomaly in anomalies)
        base_score = total_severity / len(anomalies)
        
        # Increase score if multiple anomalies exist
        multiplier = 1.0 + (len(anomalies) - 1) * 0.1
        
        return min(100, int(base_score * multiplier))
    
    def _generate_explanation(
        self, anomalies: List[AnomalyDetail], risk_score: int
    ) -> str:
        """Generate human-readable explanation."""
        if not anomalies:
            return "No anomalies detected. Invoice appears normal."
        
        if risk_score >= 70:
            risk_level = "HIGH RISK"
        elif risk_score >= 50:
            risk_level = "MODERATE RISK"
        else:
            risk_level = "LOW RISK"
        
        explanation_parts = [
            f"⚠️ {risk_level} (Score: {risk_score}/100)",
            f"Detected {len(anomalies)} anomaly/ies:"
        ]
        
        for i, anomaly in enumerate(anomalies, 1):
            explanation_parts.append(f"{i}. {anomaly.description}")
        
        return "\n".join(explanation_parts)
