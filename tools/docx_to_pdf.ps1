<#
.SYNOPSIS
  DOCX dosyasını Microsoft Word ile PDF'e dönüştürür; önce tüm field'ları günceller.
.EXAMPLE
  pwsh tools/docx_to_pdf.ps1 report/final/test.docx
  pwsh tools/docx_to_pdf.ps1 report/final/test.docx -Pdf report/final/test.pdf
.NOTES
  Kaynak DOCX değiştirilmez (kaydetmeden kapatılır). Word kurulu değilse hata verir;
  Word yoksa `tools/docx_to_pdf.py` LibreOffice'e düşer.
#>
param(
    [Parameter(Mandatory = $true)][string]$Docx,
    [string]$Pdf
)
$ErrorActionPreference = 'Stop'
$docxPath = (Resolve-Path $Docx).Path
if (-not $Pdf) { $Pdf = [IO.Path]::ChangeExtension($docxPath, '.pdf') }
$pdfPath = [IO.Path]::GetFullPath($Pdf)

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($docxPath, $false, $true)   # ConfirmConversions=false, ReadOnly=true
    [void]$doc.Fields.Update()
    foreach ($toc in $doc.TablesOfContents) { [void]$toc.Update() }
    # Alan/TOC güncellemesi sayfa akışını değiştirir; sayfa sayısını ondan SONRA hesapla.
    # Repaginate zorlanır, böylece bildirilen sayfa sayısı gerçek sayfalamayla tutarlı olur.
    $doc.Repaginate()
    # 17=PDF, OpenAfter=no, OptimizeFor=print(0), Range=all(0), From/To, Item=content(0),
    # IncludeDocProps, KeepIRM, CreateBookmarks=headings(1), DocStructureTags, BitmapMissingFonts,
    # UseISO19005_1 (PDF/A-1: tüm yazı tipleri gömülür)
    $doc.ExportAsFixedFormat($pdfPath, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $true)
    $doc.Close([ref]0)                                       # 0 = wdDoNotSaveChanges

    # Gerçek sayfa sayısını üretilen PDF'ten (pypdf) oku; Word istatistiği export sonrası
    # yeniden sayfalamadan farklı kalabiliyordu (örn. 10 vs 8). Ölçüt PDF'in kendisidir.
    $pages = $null
    try {
        $pages = & uv run python -c "import sys,pypdf;print(len(pypdf.PdfReader(sys.argv[1]).pages))" $pdfPath 2>$null
        $pages = ($pages | Select-Object -Last 1).Trim()
    } catch { $pages = $null }
    if ($pages) {
        Write-Output "PDF: $pdfPath (sayfa sayısı: $pages, PDF'ten okundu)"
    } else {
        Write-Output "PDF: $pdfPath"
    }
}
finally {
    $word.Quit()
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($word)
}
