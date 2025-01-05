Get-ChildItem -Path "D:\amlak" -Filter "*.py" -Recurse | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if (!($content -match "# -\*- coding: utf-8 -\*-")) {
        $newContent = "# -*- coding: utf-8 -*-`n`n" + $content
        $newContent | Set-Content $_.FullName -Encoding UTF8
    }
}
