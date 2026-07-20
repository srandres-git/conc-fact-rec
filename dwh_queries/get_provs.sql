DECLARE @rfc_list NVARCHAR(MAX);
SET @rfc_list = '';

SELECT 
    Proveedor as [ID Proveedor SAP],
    [Número de identificación fiscal] as [RFC Proveedor],
    [Ejecutivo de Cuentas por Pagar] as [Ejecutivo CPP SAP]
FROM raw_sap.detalle_proveedor 
WHERE [Número de identificación fiscal] IN (
    SELECT VALUE
    FROM  STRING_SPLIT(@rfc_list,',')
)
ORDER BY Proveedor DESC;