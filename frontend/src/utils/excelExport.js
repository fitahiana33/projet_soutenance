/**
 * excelExport.js - Utility for exporting data tables to MS Excel files (.xls/.xlsx compatible XML)
 */

export function exportToExcel(filename, sheetName, columns, data) {
  if (!data || !data.length) {
    alert('Aucune donnée à exporter.')
    return
  }

  // Generate MS Excel XML Format (compatible with Excel 2003+, 2016, 365, LibreOffice)
  let xml = `<?xml version="1.0"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:x="urn:schemas-microsoft-com:office:excel"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
 <Styles>
  <Style ss:ID="Header">
   <Font ss:FontName="Calibri" ss:Size="11" ss:Bold="1" ss:Color="#FFFFFF"/>
   <Interior ss:Color="#1E293B" ss:Pattern="Solid"/>
   <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>
  </Style>
  <Style ss:ID="DataCell">
   <Font ss:FontName="Calibri" ss:Size="10" ss:Color="#1E293B"/>
   <Alignment ss:Vertical="Center"/>
  </Style>
 </Styles>
 <Worksheet ss:Name="${escapeXml(sheetName || 'Données')}">
  <Table>
   <Row ss:Height="24">
`

  // Add Headers
  columns.forEach(col => {
    xml += `    <Cell ss:StyleID="Header"><Data ss:Type="String">${escapeXml(col.header)}</Data></Cell>\n`
  })
  xml += `   </Row>\n`

  // Add Data Rows
  data.forEach(row => {
    xml += `   <Row ss:Height="20">\n`
    columns.forEach(col => {
      const rawVal = col.formatter ? col.formatter(row[col.key], row) : row[col.key]
      const val = rawVal !== undefined && rawVal !== null ? rawVal : ''
      const isNum = typeof val === 'number' && !isNaN(val)
      const type = isNum ? 'Number' : 'String'
      xml += `    <Cell ss:StyleID="DataCell"><Data ss:Type="${type}">${escapeXml(String(val))}</Data></Cell>\n`
    })
    xml += `   </Row>\n`
  })

  xml += `  </Table>
 </Worksheet>
</Workbook>`

  const blob = new Blob([xml], { type: 'application/vnd.ms-excel;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${filename || 'export'}_${new Date().toISOString().slice(0, 10)}.xls`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

function escapeXml(str) {
  if (str === null || str === undefined) return ''
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}
