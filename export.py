import pandas as pd

from utils import excel_col_letter, is_numeric


def export_conciliacion_facturas(fact_sat: pd.DataFrame, output_file: str, cols_conc: list[str]):
    """
    Exporta la conciliación de facturas recibidas a un archivo Excel con formato de colores por grupo de columnas.
    """
    # Define colores por grupo (según comentarios en COLS_CONC)
    verde_cols = [
        'Estatus', 'Estatus Sustitución', 'Estatus para Cancelación', 'Estatus Cancelación', 'Fecha Cancelación', 'Ver.',
        'CFDI Relacionado', 'Tipo Relación CFDI', 'Tipo Relación CFDI Descripción', 'Tipo', 'UUID', 'UUID Sustitución',
        'Serie', 'Folio', 'Emisión', 'Fecha Sustitución', 'Uso CFDI', 'Emisor RFC', 'Emisor Nombre', 'Emisor Régimen Fiscal',
        'Emisor Régimen Fiscal Descripción', 'Conceptos Descripción', 'Conceptos ClaveProdServ SAT', 'Conceptos ClaveProdServ SAT Descripción',
        'SubTotal', 'Total SAT MXN', 'Total SAT XML', 'Tipo Cambio', 'Moneda', 'Forma Pago', 'Método Pago'
    ]
    amarillo_cols = [
        'Estatus SAP', 'Estatus CP', 'Comentario', 'Servicio', 'Estatus Box', 'Ejecutivo CxP', 'Ref. externa SAP',
        'Tipo de servicio', 'ID Proveedor SAP', 'Total SAP MXN', 'Dif. Total MXN', 'Total SAP XML', 'Dif. Total XML'
    ]
    azul_cols = ['Mes']

    # Formato de encabezado por color
    def get_header_format(col_name, workbook):
        if col_name in verde_cols:
            return workbook.add_format({'bold': True, 'bg_color': '#A9D08E', 'border': 2, 'font_color': '#000000'})  # verde
        elif col_name in amarillo_cols:
            return workbook.add_format({'bold': True, 'bg_color': '#FFD966', 'border': 2, 'font_color': '#000000'})  # amarillo
        elif col_name in azul_cols:
            return workbook.add_format({'bold': True, 'bg_color': '#BDD7EE', 'border': 2, 'font_color': '#000000'})  # azul
        else:
            return workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border': 2, 'font_color': '#000000'})  # default azul claro

    with pd.ExcelWriter(output_file, engine='xlsxwriter', datetime_format='dd-mm-yyyy') as writer:
        fact_sat[cols_conc].to_excel(writer, sheet_name='Conciliación', index=False, freeze_panes=(2, 0), startrow=1)
        workbook = writer.book
        worksheet = writer.sheets['Conciliación']
        worksheet.set_tab_color('#BDD7EE')  # azul claro

        comma_format = workbook.add_format({'num_format': '#,##0.00'})
        # Escribe encabezado con formato de color
        for col_num, col_name in enumerate(cols_conc):
            worksheet.write(1, col_num, col_name, get_header_format(col_name, workbook))
            # Ajusta ancho de columna
            max_len = max(fact_sat[col_name].astype(str).map(len).max() if col_name in fact_sat.columns else 0, len(col_name))
            col_len = max_len + 2 if max_len < 30 else 30
            # Aplica formato numérico si corresponde
            if is_numeric(col_name):
                worksheet.set_column(col_num, col_num, col_len, comma_format)
                
                # Subtotales en la primera fila
                if not col_name in ['Tipo Cambio']: # No todas las columnas numéricas se suman
                    last_row = len(fact_sat) + 2
                    col_letter = excel_col_letter(col_num)
                    formula = f'=SUBTOTAL(9, {col_letter}3:{col_letter}{last_row})'
                    worksheet.write_formula(0, col_num, formula, comma_format)
            else:
                worksheet.set_column(col_num, col_num, col_len)

    print(f'Archivo exportado: {output_file}')