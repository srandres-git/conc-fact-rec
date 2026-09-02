DECLARE @year INT;
SET @year = 2026;

WITH balance AS (
    SELECT
        document_number,
        MIN(bill_uuid) AS bill_uuid,
        MIN(document_type) AS document_type,
        MIN(text_reference) AS text_reference,
        MIN(created_by )AS created_by,
        MIN(clearing_date) AS clearing_date,
        MIN(bill_date) AS bill_date,
        SUM(gross_price) AS gross_price,
        MIN(cleared_amount) AS cleared_amount -- not agg
    FROM dev_bronze.sap_bill_aging_balance
    WHERE bill_date >= DATEFROMPARTS(@year, 1, 1) -- Limit to one year
    AND bill_date < DATEFROMPARTS(@year+1, 1, 1)
    AND document_number IS NOT NULL -- [TODO] Revisar los nulos
    GROUP BY document_number
),
conformed AS (
    SELECT
        MIN(document_number) AS document_number,
        MIN(document_date) AS document_date,
        MIN(invoice_status_sk) AS invoice_status_sk,
        MIN(row_source_system_id) AS row_source_system_id,
        MIN(gross_amount) AS gross_amount, -- not agg
        MIN(document_total_amount) AS document_total_amount, -- not agg
        MIN(withholding_total_amount) AS withholding_total_amount, -- not agg
        MIN(iva_withholding_amount) AS iva_withholding_amount, -- not agg
        MIN(isr_withholding_amount) AS isr_withholding_amount -- not agg
    FROM dev_silver.f_conformed_cxp_bill
    WHERE row_source_system_id = 103 -- Only SAP
    AND document_date >= DATEFROMPARTS(@year, 1, 1) -- Limit to one year
    AND document_date < DATEFROMPARTS(@year+1, 1, 1)
    GROUP BY document_number
),
dstatus AS (
    SELECT 
        invoice_status_sk,
        CASE
            WHEN UPPER(invoice_status) = 'CANCELLED' THEN 'Cancelada'
            WHEN UPPER(invoice_status) = 'CLEARED' THEN 'Pagado'
            WHEN UPPER(invoice_status) = 'OPEN' THEN 'Contabilizada'
            WHEN UPPER(invoice_status) = 'PARTIALLY CLEARED' THEN 'Parcialmente pagado'
            ELSE invoice_status
        END AS estatus
    FROM dev_silver.d_conformed_invoice_status
)
SELECT 
    conformed.document_number AS ID,
    balance.bill_uuid AS [ID de factura oficial],
    dstatus.estatus AS [Estado de factura],
    balance.document_type AS [Tipo de documento],
    balance.text_reference AS [Referencia externa],
    balance.created_by AS [Creado por],
    conformed.document_date AS [Fecha de factura],
    balance.clearing_date AS [Fecha de compensación],
    balance.gross_price AS [Importe bruto], -- not agg
    conformed.iva_withholding_amount AS [Retención de IVA], -- not agg
    conformed.isr_withholding_amount AS [Retención de ISR], -- not agg
    -- Se calcula el importe del bruto (agregado) de la tabla de saldos
    -- menos las retenciones (no agregadas) de la tabla de conformed
    -- si la columna de total proveniente de retenciones es cero,
    -- se toma el total por default de conformed
    CASE
        WHEN conformed.withholding_total_amount = 0 THEN conformed.document_total_amount -- not agg
        ELSE balance.gross_price - conformed.iva_withholding_amount - conformed.isr_withholding_amount -- balance agg, conformed not agg
    END AS [Importe de la factura], 
    balance.cleared_amount AS [Importe compensado], -- not agg
    ABS(cleared_amount)
    - ABS(
        CASE
            WHEN conformed.withholding_total_amount = 0 THEN conformed.document_total_amount
            ELSE balance.gross_price - conformed.iva_withholding_amount - conformed.isr_withholding_amount
        END
    ) AS Saldo
FROM conformed
LEFT JOIN balance ON conformed.document_number = balance.document_number
LEFT JOIN dstatus ON conformed.invoice_status_sk = dstatus.invoice_status_sk